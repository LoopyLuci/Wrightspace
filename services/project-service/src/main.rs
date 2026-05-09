use axum::{
    extract::{Path, State, ws::{Message, WebSocket, WebSocketUpgrade}},
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use futures::{SinkExt, StreamExt};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::{collections::HashMap, net::SocketAddr, path::PathBuf, sync::{Arc, Mutex}};
use tokio::{fs, sync::{broadcast, RwLock}};
use tower_http::{cors::CorsLayer, trace::TraceLayer};
use yrs::{Doc, ReadTxn, StateVector, Transact, Update};
use yrs::sync::protocol::{Message as SyncProtocolMessage, SyncMessage};
use yrs::updates::{decoder::Decode, encoder::Encode};
use uuid::Uuid;
use futures::stream::SplitSink;

#[derive(Clone)]
struct AppState {
    projects: Arc<RwLock<HashMap<Uuid, ProjectMeta>>>,
    rooms: Arc<RwLock<HashMap<Uuid, Arc<RoomState>>>>,
    data_dir: Arc<PathBuf>,
    ai_client: reqwest::Client,
    ai_base_url: Arc<String>,
    ai_api_key: Arc<Option<String>>,
    ai_model: Arc<String>,
}

#[derive(Clone, Serialize, Deserialize)]
struct ProjectMeta {
    id: Uuid,
    name: String,
}

#[derive(Deserialize)]
struct CreateProjectRequest {
    name: String,
}

#[derive(Deserialize)]
struct GenerateComponentRequest {
    prompt: String,
    #[serde(default, rename = "designTokens")]
    design_tokens: Value,
}

#[derive(Clone)]
struct RoomMessage {
    source: Uuid,
    payload: Vec<u8>,
}

struct RoomState {
    doc: Mutex<Doc>,
    broadcaster: broadcast::Sender<RoomMessage>,
    snapshot_path: PathBuf,
}

impl RoomState {
    async fn load_snapshot(&self) {
        match fs::read(&self.snapshot_path).await {
            Ok(bytes) => {
                if let Err(error) = self.apply_snapshot(&bytes).await {
                    eprintln!("failed to load snapshot for {}: {error}", self.snapshot_path.display());
                }
            }
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
            Err(error) => eprintln!("failed to read snapshot for {}: {error}", self.snapshot_path.display()),
        }
    }

    async fn apply_snapshot(&self, bytes: &[u8]) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let update = Update::decode_v1(bytes)?;
        let doc = self.doc.lock().expect("room doc mutex poisoned");
        doc.transact_mut().apply_update(update)?;
        Ok(())
    }

    async fn persist(&self) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let snapshot = {
            let doc = self.doc.lock().expect("room doc mutex poisoned");
            let txn = doc.transact();
            let state_vector = StateVector::default();
            txn.encode_state_as_update_v1(&state_vector)
        };

        if let Some(parent) = self.snapshot_path.parent() {
            fs::create_dir_all(parent).await?;
        }

        fs::write(&self.snapshot_path, snapshot).await?;
        Ok(())
    }

    async fn sync_step1(&self, state_vector: StateVector) -> Vec<u8> {
        let update = {
            let doc = self.doc.lock().expect("room doc mutex poisoned");
            let txn = doc.transact();
            let update = txn.encode_state_as_update_v1(&state_vector);
            update
        };

        SyncProtocolMessage::Sync(SyncMessage::SyncStep2(update)).encode_v1()
    }

    async fn server_state_vector(&self) -> Vec<u8> {
        let state_vector = {
            let doc = self.doc.lock().expect("room doc mutex poisoned");
            let txn = doc.transact();
            let state_vector = txn.state_vector();
            state_vector
        };

        SyncProtocolMessage::Sync(SyncMessage::SyncStep1(state_vector)).encode_v1()
    }
}

#[tokio::main]
async fn main() {
    let ai_base_url = std::env::var("AI_BASE_URL")
        .or_else(|_| std::env::var("OPENAI_BASE_URL"))
        .unwrap_or_else(|_| "https://api.openai.com".to_string());
    let ai_api_key = std::env::var("AI_API_KEY")
        .or_else(|_| std::env::var("OPENAI_API_KEY"))
        .ok();
    let ai_model = std::env::var("AI_MODEL").unwrap_or_else(|_| "gpt-4o-mini".to_string());

    let state = AppState {
        projects: Arc::new(RwLock::new(HashMap::new())),
        rooms: Arc::new(RwLock::new(HashMap::new())),
        data_dir: Arc::new(PathBuf::from("data/yjs_docs")),
        ai_client: reqwest::Client::new(),
        ai_base_url: Arc::new(ai_base_url),
        ai_api_key: Arc::new(ai_api_key),
        ai_model: Arc::new(ai_model),
    };

    let app = Router::new()
        .route("/health", get(health))
        .route("/projects", post(create_project))
        .route("/projects/:id", get(get_project))
        .route("/api/ai/generate-component", post(generate_component))
        .route("/ws/projects/:id/collab", get(collab_socket))
        .with_state(state)
        .layer(CorsLayer::permissive())
        .layer(TraceLayer::new_for_http());

    let addr = SocketAddr::from(([127, 0, 0, 1], 4001));
    println!("project-service listening on {}", addr);

    let listener = tokio::net::TcpListener::bind(addr)
        .await
        .expect("failed to bind socket");

    axum::serve(listener, app)
        .await
        .expect("project-service server failed");
}

async fn health() -> impl IntoResponse {
    (StatusCode::OK, "ok")
}

async fn create_project(
    State(state): State<AppState>,
    Json(request): Json<CreateProjectRequest>,
) -> impl IntoResponse {
    let id = Uuid::new_v4();
    let project = ProjectMeta {
        id,
        name: request.name,
    };

    state.projects.write().await.insert(id, project.clone());
    (StatusCode::CREATED, Json(project))
}

async fn get_project(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
) -> impl IntoResponse {
    let guard = state.projects.read().await;
    match guard.get(&id) {
        Some(project) => (StatusCode::OK, Json(project.clone())).into_response(),
        None => (StatusCode::NOT_FOUND, "project not found").into_response(),
    }
}

async fn generate_component(
    State(state): State<AppState>,
    Json(request): Json<GenerateComponentRequest>,
) -> impl IntoResponse {
    let prompt = request.prompt.trim();
    if prompt.is_empty() {
        return (StatusCode::BAD_REQUEST, Json(json!({ "error": "prompt cannot be empty" }))).into_response();
    }

    let generated = if state.ai_api_key.is_some() {
        match generate_with_openai_proxy(&state, prompt, request.design_tokens).await {
            Ok(node) => node,
            Err(error) => {
                return (
                    StatusCode::BAD_GATEWAY,
                    Json(json!({ "error": format!("AI upstream failed: {error}") })),
                )
                    .into_response();
            }
        }
    } else {
        create_fallback_ir_node(prompt)
    };

    if let Err(error) = validate_ir_node(&generated) {
        return (
            StatusCode::UNPROCESSABLE_ENTITY,
            Json(json!({ "error": format!("invalid irNode payload: {error}") })),
        )
            .into_response();
    }

    (StatusCode::OK, Json(json!({ "irNode": generated }))).into_response()
}

async fn generate_with_openai_proxy(
    state: &AppState,
    prompt: &str,
    design_tokens: Value,
) -> Result<Value, String> {
    let api_key = state
        .ai_api_key
        .as_ref()
        .clone()
        .ok_or_else(|| "missing API key".to_string())?;

    let endpoint = format!("{}/v1/chat/completions", state.ai_base_url.trim_end_matches('/'));
    let request_body = json!({
        "model": state.ai_model.as_str(),
        "messages": [
            {
                "role": "system",
                "content": "You are an IR generator for a React page builder. Return JSON only with a top-level 'irNode' object. Valid node types are 'element' and 'text'. Element shape: {id,type:'element',tag,styles,props,children}. Text shape: {id,type:'text',content,styles}."
            },
            {
                "role": "user",
                "content": format!("Prompt: {prompt}\nDesign tokens: {}", design_tokens)
            }
        ],
        "temperature": 0.3
    });

    let response = state
        .ai_client
        .post(endpoint)
        .bearer_auth(api_key)
        .json(&request_body)
        .send()
        .await
        .map_err(|error| format!("request error: {error}"))?;

    if !response.status().is_success() {
        let status = response.status();
        let body = response.text().await.unwrap_or_default();
        return Err(format!("status {status}: {body}"));
    }

    let payload = response
        .json::<Value>()
        .await
        .map_err(|error| format!("invalid JSON response: {error}"))?;

    let content = payload
        .get("choices")
        .and_then(|choices| choices.as_array())
        .and_then(|choices| choices.first())
        .and_then(|choice| choice.get("message"))
        .and_then(|message| message.get("content"))
        .and_then(|content| content.as_str())
        .ok_or_else(|| "missing choices[0].message.content".to_string())?;

    let extracted_json = extract_first_json_object(content)?;
    let parsed = serde_json::from_str::<Value>(&extracted_json)
        .map_err(|error| format!("response content was not valid JSON: {error}"))?;

    if let Some(node) = parsed.get("irNode") {
        return Ok(node.clone());
    }

    Ok(parsed)
}

fn extract_first_json_object(content: &str) -> Result<String, String> {
    if let Some(start) = content.find("```") {
        let after = &content[start + 3..];
        let fenced = if let Some(stripped) = after.strip_prefix("json") {
            stripped
        } else {
            after
        };

        if let Some(end) = fenced.find("```") {
            let candidate = fenced[..end].trim();
            if !candidate.is_empty() {
                return Ok(candidate.to_string());
            }
        }
    }

    let mut depth = 0usize;
    let mut start_index: Option<usize> = None;
    for (index, ch) in content.char_indices() {
        if ch == '{' {
            if start_index.is_none() {
                start_index = Some(index);
            }
            depth += 1;
        } else if ch == '}' {
            if depth == 0 {
                continue;
            }

            depth -= 1;
            if depth == 0 {
                if let Some(start) = start_index {
                    return Ok(content[start..=index].to_string());
                }
            }
        }
    }

    Err("could not find JSON object in model output".to_string())
}

fn create_fallback_ir_node(prompt: &str) -> Value {
    let headline = format!("AI Draft: {}", prompt.chars().take(64).collect::<String>());
    json!({
      "id": "ai-generated-section",
      "type": "element",
      "tag": "section",
      "styles": {
        "display": { "value": "flex" },
        "flexDirection": { "value": "column", "breakpoint": "base" },
        "padding": { "value": "6rem 2rem", "breakpoint": "base" }
      },
      "props": {
        "className": "hero-section"
      },
      "children": [
        {
          "id": "ai-generated-heading",
          "type": "text",
          "content": headline,
          "styles": {
            "fontSize": { "value": "3.5rem", "breakpoint": "base" },
            "fontWeight": { "value": "700" }
          }
        },
        {
          "id": "ai-generated-copy",
          "type": "text",
          "content": "Replace this with a richer generated section once AI credentials are configured.",
          "styles": {}
        }
      ]
    })
}

fn validate_ir_node(value: &Value) -> Result<(), String> {
    let node_type = value
        .get("type")
        .and_then(Value::as_str)
        .ok_or_else(|| "missing type".to_string())?;

    let id = value
        .get("id")
        .and_then(Value::as_str)
        .ok_or_else(|| "missing id".to_string())?;
    if id.trim().is_empty() {
        return Err("id cannot be empty".to_string());
    }

    match node_type {
        "text" => {
            let content = value.get("content").ok_or_else(|| "text node missing content".to_string())?;
            if !(content.is_string()
                || content
                    .get("binding")
                    .and_then(Value::as_str)
                    .map(|binding| !binding.trim().is_empty())
                    .unwrap_or(false))
            {
                return Err("text node content must be string or { binding }".to_string());
            }

            if !value.get("styles").map(Value::is_object).unwrap_or(false) {
                return Err("text node styles must be an object".to_string());
            }
            Ok(())
        }
        "element" => {
            let tag = value
                .get("tag")
                .and_then(Value::as_str)
                .ok_or_else(|| "element node missing tag".to_string())?;
            if tag.trim().is_empty() {
                return Err("element tag cannot be empty".to_string());
            }

            if !value.get("styles").map(Value::is_object).unwrap_or(false) {
                return Err("element styles must be an object".to_string());
            }

            if !value.get("props").map(Value::is_object).unwrap_or(false) {
                return Err("element props must be an object".to_string());
            }

            let children = value
                .get("children")
                .and_then(Value::as_array)
                .ok_or_else(|| "element children must be an array".to_string())?;

            for child in children {
                validate_ir_node(child)?;
            }

            Ok(())
        }
        _ => Err("unsupported node type".to_string()),
    }
}

async fn collab_socket(
    State(state): State<AppState>,
    Path(project_id): Path<Uuid>,
    ws: WebSocketUpgrade,
) -> impl IntoResponse {
    ws.on_upgrade(move |socket| handle_collab_socket(state, project_id, socket))
}

async fn handle_collab_socket(state: AppState, project_id: Uuid, socket: WebSocket) {
    let room = match get_or_create_room(&state, project_id).await {
        Ok(room) => room,
        Err(error) => {
            eprintln!("failed to create room {project_id}: {error}");
            return;
        }
    };

    let connection_id = Uuid::new_v4();
    let (mut sender, mut receiver): (SplitSink<WebSocket, Message>, _) = socket.split();
    let mut broadcast_receiver = room.broadcaster.subscribe();

    loop {
        tokio::select! {
            message = receiver.next() => {
                let Some(result) = message else {
                    break;
                };

                let message = match result {
                    Ok(message) => message,
                    Err(error) => {
                        eprintln!("websocket error for room {project_id}: {error}");
                        break;
                    }
                };

                match message {
                    Message::Binary(bytes) => {
                        if let Err(error) = handle_binary_message(&room, &state, project_id, connection_id, &bytes, &mut sender).await {
                            eprintln!("collab message error for room {project_id}: {error}");
                        }
                    }
                    Message::Close(_) => break,
                    _ => {}
                }
            }
            broadcast = broadcast_receiver.recv() => {
                match broadcast {
                    Ok(message) => {
                        if message.source == connection_id {
                            continue;
                        }

                        if sender.send(Message::Binary(message.payload)).await.is_err() {
                            break;
                        }
                    }
                    Err(broadcast::error::RecvError::Closed) => break,
                    Err(broadcast::error::RecvError::Lagged(_)) => continue,
                }
            }
        }
    }

    if let Err(error) = room.persist().await {
        eprintln!("failed to persist room {project_id} on disconnect: {error}");
    }
}

async fn handle_binary_message(
    room: &Arc<RoomState>,
    state: &AppState,
    project_id: Uuid,
    connection_id: Uuid,
    bytes: &[u8],
    sender: &mut SplitSink<WebSocket, Message>,
) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let message = SyncProtocolMessage::decode_v1(bytes)?;

    match message {
        SyncProtocolMessage::Sync(SyncMessage::SyncStep1(state_vector)) => {
            let sync_step_2 = room.sync_step1(state_vector).await;
            sender.send(Message::Binary(sync_step_2)).await?;

            let sync_step_1 = room.server_state_vector().await;
            sender.send(Message::Binary(sync_step_1)).await?;
        }
        SyncProtocolMessage::Sync(SyncMessage::SyncStep2(update))
        | SyncProtocolMessage::Sync(SyncMessage::Update(update)) => {
            let update_bytes = update.clone();
            let update = Update::decode_v1(&update_bytes)?;
            {
                let doc = room.doc.lock().expect("room doc mutex poisoned");
                doc.transact_mut().apply_update(update)?;
            }

            room.persist().await?;

            let payload = SyncProtocolMessage::Sync(SyncMessage::Update(update_bytes)).encode_v1();
            let _ = room.broadcaster.send(RoomMessage { source: connection_id, payload });
        }
        SyncProtocolMessage::AwarenessQuery | SyncProtocolMessage::Awareness(_) | SyncProtocolMessage::Auth(_) | SyncProtocolMessage::Custom(_, _) => {
            let payload = SyncProtocolMessage::decode_v1(bytes)?.encode_v1();
            let _ = room.broadcaster.send(RoomMessage { source: connection_id, payload });
        }
    }

    let _ = state;
    let _ = project_id;
    Ok(())
}

async fn get_or_create_room(state: &AppState, project_id: Uuid) -> Result<Arc<RoomState>, Box<dyn std::error::Error + Send + Sync>> {
    if let Some(room) = state.rooms.read().await.get(&project_id).cloned() {
        return Ok(room);
    }

    let mut rooms = state.rooms.write().await;
    if let Some(room) = rooms.get(&project_id).cloned() {
        return Ok(room);
    }

    let snapshot_path = state.data_dir.join(format!("{project_id}.bin"));
    let (sender, _) = broadcast::channel(128);
    let room = Arc::new(RoomState {
        doc: Mutex::new(Doc::new()),
        broadcaster: sender,
        snapshot_path,
    });

    room.load_snapshot().await;
    rooms.insert(project_id, room.clone());
    Ok(room)
}
