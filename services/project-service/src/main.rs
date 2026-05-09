use axum::{
    extract::{Path, Query, State, ws::{Message, WebSocket, WebSocketUpgrade}},
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use futures::{SinkExt, StreamExt};
use regex::Regex;
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
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
    marketplace_blocks: Arc<RwLock<HashMap<String, Vec<BlockPackage>>>>,
    marketplace_store_path: Arc<PathBuf>,
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

#[derive(Deserialize)]
struct GeneratePlanRequest {
    prompt: String,
    #[serde(default, rename = "benchmarkId")]
    benchmark_id: Option<String>,
    #[serde(default, rename = "irSnapshot")]
    ir_snapshot: Option<Value>,
    #[serde(default, rename = "responseFormat")]
    response_format: Option<String>,
}

#[derive(Clone, Serialize, Deserialize)]
struct BlockDependency {
    id: String,
    version: String,
}

#[derive(Clone, Serialize, Deserialize)]
struct BlockPackageMetadata {
    id: String,
    name: String,
    description: String,
    version: String,
    author: String,
    license: String,
    framework: Vec<String>,
    trust: String,
    keywords: Vec<String>,
    category: String,
    #[serde(rename = "createdAt")]
    created_at: String,
    #[serde(rename = "updatedAt")]
    updated_at: String,
    #[serde(default)]
    dependencies: Vec<BlockDependency>,
}

#[derive(Clone, Serialize, Deserialize)]
struct BlockPackage {
    metadata: BlockPackageMetadata,
    #[serde(rename = "irNode")]
    ir_node: Value,
    signature: String,
}

#[derive(Clone, Serialize)]
struct RegistryEntry {
    id: String,
    name: String,
    description: String,
    version: String,
    author: String,
    license: String,
    framework: Vec<String>,
    trust: String,
    keywords: Vec<String>,
    category: String,
    #[serde(rename = "createdAt")]
    created_at: String,
    #[serde(rename = "updatedAt")]
    updated_at: String,
    dependencies: Vec<BlockDependency>,
    signature: String,
}

impl RegistryEntry {
    fn from_block(pkg: &BlockPackage) -> Self {
        Self {
            id: pkg.metadata.id.clone(),
            name: pkg.metadata.name.clone(),
            description: pkg.metadata.description.clone(),
            version: pkg.metadata.version.clone(),
            author: pkg.metadata.author.clone(),
            license: pkg.metadata.license.clone(),
            framework: pkg.metadata.framework.clone(),
            trust: pkg.metadata.trust.clone(),
            keywords: pkg.metadata.keywords.clone(),
            category: pkg.metadata.category.clone(),
            created_at: pkg.metadata.created_at.clone(),
            updated_at: pkg.metadata.updated_at.clone(),
            dependencies: pkg.metadata.dependencies.clone(),
            signature: pkg.signature.clone(),
        }
    }
}

#[derive(Deserialize)]
struct MarketplaceSearchQuery {
    q: Option<String>,
    category: Option<String>,
    framework: Option<String>,
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

    let marketplace_store_path = PathBuf::from("data/marketplace_blocks.json");
    let marketplace_blocks = load_marketplace_blocks(&marketplace_store_path).await;

    let state = AppState {
        projects: Arc::new(RwLock::new(HashMap::new())),
        rooms: Arc::new(RwLock::new(HashMap::new())),
        data_dir: Arc::new(PathBuf::from("data/yjs_docs")),
        ai_client: reqwest::Client::new(),
        ai_base_url: Arc::new(ai_base_url),
        ai_api_key: Arc::new(ai_api_key),
        ai_model: Arc::new(ai_model),
        marketplace_blocks: Arc::new(RwLock::new(marketplace_blocks)),
        marketplace_store_path: Arc::new(marketplace_store_path),
    };

    let app = Router::new()
        .route("/health", get(health))
        .route("/projects", post(create_project))
        .route("/projects/:id", get(get_project))
        .route("/api/ai/generate-component", post(generate_component))
        .route("/api/ai/generate-plan", post(generate_plan))
        .route("/api/marketplace/publish", post(publish_block))
        .route("/api/marketplace/search", get(search_blocks))
        .route("/api/marketplace/blocks/:id", get(get_block))
        .route("/api/marketplace/blocks/:id/versions", get(list_block_versions))
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

async fn generate_plan(
    State(state): State<AppState>,
    Json(request): Json<GeneratePlanRequest>,
) -> impl IntoResponse {
    let prompt = request.prompt.trim();
    if prompt.is_empty() {
        return (StatusCode::BAD_REQUEST, Json(json!({ "error": "prompt cannot be empty" }))).into_response();
    }

    let generated = if state.ai_api_key.is_some() {
        match generate_plan_with_openai_proxy(
            &state,
            prompt,
            request.benchmark_id.as_deref(),
            request.ir_snapshot,
            request.response_format.as_deref(),
        )
        .await
        {
            Ok(plan) => plan,
            Err(error) => {
                return (
                    StatusCode::BAD_GATEWAY,
                    Json(json!({ "error": format!("AI upstream failed: {error}") })),
                )
                    .into_response();
            }
        }
    } else {
        json!({ "plan": create_fallback_plan(prompt, request.benchmark_id.as_deref()) })
    };

    if let Err(error) = validate_plan_payload(&generated) {
        return (
            StatusCode::UNPROCESSABLE_ENTITY,
            Json(json!({ "error": format!("invalid plan payload: {error}") })),
        )
            .into_response();
    }

    (StatusCode::OK, Json(generated)).into_response()
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

async fn generate_plan_with_openai_proxy(
    state: &AppState,
    prompt: &str,
    benchmark_id: Option<&str>,
    ir_snapshot: Option<Value>,
    response_format: Option<&str>,
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
                "content": "You are a planning engine for a React page builder. Return JSON only with a top-level 'plan' array. Each step must include description, target, action (create|update|delete), and expectedDiff. Keep the plan short and executable."
            },
            {
                "role": "user",
                "content": format!(
                    "Prompt: {prompt}\nBenchmarkId: {}\nResponseFormat: {}\nCurrent IR Snapshot: {}",
                    benchmark_id.unwrap_or("unknown"),
                    response_format.unwrap_or("agent-plan"),
                    ir_snapshot.unwrap_or(json!(null))
                )
            }
        ],
        "temperature": 0.2
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

    let plan = if parsed.get("plan").and_then(Value::as_array).is_some() {
        parsed.get("plan").cloned().unwrap_or(Value::Array(vec![]))
    } else if parsed.is_array() {
        parsed
    } else {
        Value::Array(vec![parsed])
    };

    Ok(json!({
        "plan": plan,
        "usage": payload.get("usage").cloned().unwrap_or(json!({}))
    }))
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

fn create_fallback_plan(prompt: &str, benchmark_id: Option<&str>) -> Value {
    let normalized = prompt.to_lowercase();

    if benchmark_id == Some("security-accessibility-audit")
        || normalized.contains("audit")
        || normalized.contains("security")
        || normalized.contains("accessibility")
    {
        return json!([
            {
                "description": "Audit the current page for security and accessibility issues",
                "target": "page:/",
                "action": "update",
                "expectedDiff": "Produce severity-rated findings and suggested fixes without destructive edits.",
                "mode": "report"
            }
        ]);
    }

    if benchmark_id == Some("single-element-creation") || normalized.contains("button") || normalized.contains("subscribe") {
        return json!([
            {
                "description": "Insert CTA button in the hero section",
                "target": "page:/",
                "action": "create",
                "expectedDiff": "Append one accessible call-to-action button below the headline."
            }
        ]);
    }

    if benchmark_id == Some("multi-page-scaffold") || normalized.contains("pricing") || normalized.contains("contact") {
        return json!([
            {
                "description": "Create a marketing scaffold with linked sections",
                "target": "app-shell",
                "action": "create",
                "expectedDiff": "Add home, pricing, and contact sections with simple navigation links."
            }
        ]);
    }

    if benchmark_id == Some("responsive-refactor") || normalized.contains("responsive") || normalized.contains("mobile") {
        return json!([
            {
                "description": "Refactor hero layout to avoid overflow on mobile",
                "target": "page:/",
                "action": "update",
                "expectedDiff": "Switch to a responsive layout that stacks media below copy on narrow viewports."
            }
        ]);
    }

    json!([
        {
            "description": "Inspect the current page and prepare a targeted update",
            "target": "page:/",
            "action": "update",
            "expectedDiff": "Produce a narrow, benchmark-style change with preserved structure."
        }
    ])
}

fn validate_plan_payload(value: &Value) -> Result<(), String> {
    let plan = value
        .get("plan")
        .and_then(Value::as_array)
        .ok_or_else(|| "missing plan array".to_string())?;

    if plan.is_empty() {
        return Err("plan must contain at least one step".to_string());
    }

    for (index, step) in plan.iter().enumerate() {
        let description = step
            .get("description")
            .and_then(Value::as_str)
            .ok_or_else(|| format!("plan[{index}] missing description"))?;
        if description.trim().is_empty() {
            return Err(format!("plan[{index}] description cannot be empty"));
        }

        let target = step
            .get("target")
            .and_then(Value::as_str)
            .ok_or_else(|| format!("plan[{index}] missing target"))?;
        if target.trim().is_empty() {
            return Err(format!("plan[{index}] target cannot be empty"));
        }

        let action = step
            .get("action")
            .and_then(Value::as_str)
            .ok_or_else(|| format!("plan[{index}] missing action"))?;
        if action != "create" && action != "update" && action != "delete" {
            return Err(format!("plan[{index}] action must be create, update, or delete"));
        }

        let expected_diff = step
            .get("expectedDiff")
            .and_then(Value::as_str)
            .ok_or_else(|| format!("plan[{index}] missing expectedDiff"))?;
        if expected_diff.trim().is_empty() {
            return Err(format!("plan[{index}] expectedDiff cannot be empty"));
        }
    }

    Ok(())
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
        "component" => {
            let component_id = value
                .get("componentId")
                .and_then(Value::as_str)
                .ok_or_else(|| "component node missing componentId".to_string())?;
            if component_id.trim().is_empty() {
                return Err("componentId cannot be empty".to_string());
            }

            if !value.get("props").map(Value::is_object).unwrap_or(false) {
                return Err("component props must be an object".to_string());
            }

            let slots = value
                .get("slots")
                .and_then(Value::as_object)
                .ok_or_else(|| "component slots must be an object".to_string())?;

            for (_slot_name, slot_nodes) in slots {
                let slot_array = slot_nodes
                    .as_array()
                    .ok_or_else(|| "component slot content must be an array".to_string())?;
                for child in slot_array {
                    validate_ir_node(child)?;
                }
            }

            Ok(())
        }
        "slot" => {
            let slot_name = value
                .get("slotName")
                .and_then(Value::as_str)
                .ok_or_else(|| "slot node missing slotName".to_string())?;
            if slot_name.trim().is_empty() {
                return Err("slotName cannot be empty".to_string());
            }

            if let Some(fallback) = value.get("fallback") {
                let fallback_nodes = fallback
                    .as_array()
                    .ok_or_else(|| "slot fallback must be an array".to_string())?;
                for child in fallback_nodes {
                    validate_ir_node(child)?;
                }
            }

            Ok(())
        }
        _ => Err("unsupported node type".to_string()),
    }
}

fn canonicalize_json(value: &Value) -> String {
    match value {
        Value::Null => "null".to_string(),
        Value::Bool(v) => {
            if *v { "true".to_string() } else { "false".to_string() }
        }
        Value::Number(number) => number.to_string(),
        Value::String(text) => serde_json::to_string(text).unwrap_or_else(|_| "\"\"".to_string()),
        Value::Array(items) => {
            let serialized = items.iter().map(canonicalize_json).collect::<Vec<_>>().join(",");
            format!("[{serialized}]")
        }
        Value::Object(map) => {
            let mut keys = map.keys().cloned().collect::<Vec<_>>();
            keys.sort();
            let serialized = keys
                .iter()
                .map(|key| {
                    let value = map.get(key).unwrap_or(&Value::Null);
                    let key_json = serde_json::to_string(key).unwrap_or_else(|_| "\"\"".to_string());
                    format!("{key_json}:{}", canonicalize_json(value))
                })
                .collect::<Vec<_>>()
                .join(",");
            format!("{{{serialized}}}")
        }
    }
}

fn hash_ir_node(ir_node: &Value) -> String {
    let canonical = canonicalize_json(ir_node);
    let mut hasher = Sha256::new();
    hasher.update(canonical.as_bytes());
    format!("{:x}", hasher.finalize())
}

fn verify_block_signature(pkg: &BlockPackage) -> bool {
    hash_ir_node(&pkg.ir_node) == pkg.signature.to_lowercase()
}

fn parse_semver(version: &str) -> Option<(u64, u64, u64, Option<String>, Option<String>)> {
    let semver_regex = Regex::new(r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$").ok()?;
    let captures = semver_regex.captures(version)?;
    let major = captures.get(1)?.as_str().parse::<u64>().ok()?;
    let minor = captures.get(2)?.as_str().parse::<u64>().ok()?;
    let patch = captures.get(3)?.as_str().parse::<u64>().ok()?;
    let pre = captures.get(4).map(|m| m.as_str().to_string());
    let build = captures.get(5).map(|m| m.as_str().to_string());
    Some((major, minor, patch, pre, build))
}

fn compare_semver(a: &str, b: &str) -> std::cmp::Ordering {
    match (parse_semver(a), parse_semver(b)) {
        (Some(left), Some(right)) => {
            let ordering = left.0.cmp(&right.0)
                .then(left.1.cmp(&right.1))
                .then(left.2.cmp(&right.2));
            if ordering != std::cmp::Ordering::Equal {
                return ordering;
            }

            match (&left.3, &right.3) {
                (None, None) => std::cmp::Ordering::Equal,
                (None, Some(_)) => std::cmp::Ordering::Greater,
                (Some(_), None) => std::cmp::Ordering::Less,
                (Some(l), Some(r)) => l.cmp(r),
            }
        }
        _ => a.cmp(b),
    }
}

fn validate_marketplace_block(pkg: &BlockPackage) -> Result<(), String> {
    if pkg.metadata.id.trim().is_empty() {
        return Err("metadata.id cannot be empty".to_string());
    }
    if pkg.metadata.name.trim().is_empty() {
        return Err("metadata.name cannot be empty".to_string());
    }
    if pkg.metadata.description.trim().is_empty() {
        return Err("metadata.description cannot be empty".to_string());
    }
    if parse_semver(&pkg.metadata.version).is_none() {
        return Err("metadata.version must be semver".to_string());
    }
    if pkg.metadata.author.trim().is_empty() {
        return Err("metadata.author cannot be empty".to_string());
    }
    if pkg.metadata.license.trim().is_empty() {
        return Err("metadata.license cannot be empty".to_string());
    }
    if pkg.metadata.framework.is_empty() {
        return Err("metadata.framework cannot be empty".to_string());
    }
    if pkg.metadata.category.trim().is_empty() {
        return Err("metadata.category cannot be empty".to_string());
    }

    if pkg.metadata.trust != "verified"
        && pkg.metadata.trust != "community"
        && pkg.metadata.trust != "unverified"
    {
        return Err("metadata.trust must be verified, community, or unverified".to_string());
    }

    for dependency in &pkg.metadata.dependencies {
        if dependency.id.trim().is_empty() {
            return Err("dependency id cannot be empty".to_string());
        }
        if parse_semver(&dependency.version).is_none() {
            return Err(format!("dependency {} must use semver", dependency.id));
        }
    }

    if !pkg.signature.chars().all(|ch| ch.is_ascii_hexdigit()) || pkg.signature.len() != 64 {
        return Err("signature must be a 64-char SHA-256 hex string".to_string());
    }

    validate_ir_node(&pkg.ir_node)?;

    if !verify_block_signature(pkg) {
        return Err("signature does not match irNode hash".to_string());
    }

    Ok(())
}

async fn load_marketplace_blocks(path: &PathBuf) -> HashMap<String, Vec<BlockPackage>> {
    match fs::read(path).await {
        Ok(bytes) => serde_json::from_slice::<HashMap<String, Vec<BlockPackage>>>(&bytes).unwrap_or_default(),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => HashMap::new(),
        Err(_) => HashMap::new(),
    }
}

async fn persist_marketplace_blocks(state: &AppState) -> Result<(), String> {
    let snapshot = {
        let guard = state.marketplace_blocks.read().await;
        serde_json::to_vec_pretty(&*guard).map_err(|error| format!("serialize store failed: {error}"))?
    };

    if let Some(parent) = state.marketplace_store_path.parent() {
        fs::create_dir_all(parent)
            .await
            .map_err(|error| format!("failed to create marketplace data dir: {error}"))?;
    }

    fs::write(&*state.marketplace_store_path, snapshot)
        .await
        .map_err(|error| format!("failed to write marketplace data: {error}"))?;

    Ok(())
}

async fn publish_block(
    State(state): State<AppState>,
    Json(pkg): Json<BlockPackage>,
) -> impl IntoResponse {
    if let Err(error) = validate_marketplace_block(&pkg) {
        return (StatusCode::BAD_REQUEST, Json(json!({ "error": error }))).into_response();
    }

    {
        let mut guard = state.marketplace_blocks.write().await;
        let versions = guard.entry(pkg.metadata.id.clone()).or_default();

        if let Some(existing) = versions.iter_mut().find(|existing| existing.metadata.version == pkg.metadata.version) {
            *existing = pkg.clone();
        } else {
            versions.push(pkg.clone());
        }

        versions.sort_by(|a, b| compare_semver(&a.metadata.version, &b.metadata.version));
    }

    if let Err(error) = persist_marketplace_blocks(&state).await {
        return (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(json!({ "error": error })),
        )
            .into_response();
    }

    (StatusCode::OK, Json(pkg)).into_response()
}

async fn search_blocks(
    State(state): State<AppState>,
    Query(query): Query<MarketplaceSearchQuery>,
) -> impl IntoResponse {
    let needle = query.q.unwrap_or_default().to_lowercase();
    let category = query.category.unwrap_or_default().to_lowercase();
    let framework = query.framework.unwrap_or_default().to_lowercase();

    let guard = state.marketplace_blocks.read().await;
    let mut entries: Vec<RegistryEntry> = guard
        .values()
        .filter_map(|versions| versions.last())
        .filter(|pkg| {
            if !needle.is_empty() {
                let haystack = format!(
                    "{} {} {} {}",
                    pkg.metadata.id,
                    pkg.metadata.name,
                    pkg.metadata.description,
                    pkg.metadata.keywords.join(" ")
                )
                .to_lowercase();
                if !haystack.contains(&needle) {
                    return false;
                }
            }

            if !category.is_empty() && pkg.metadata.category.to_lowercase() != category {
                return false;
            }

            if !framework.is_empty()
                && !pkg
                    .metadata
                    .framework
                    .iter()
                    .any(|item| item.to_lowercase() == framework)
            {
                return false;
            }

            true
        })
        .map(RegistryEntry::from_block)
        .collect();

    entries.sort_by(|a, b| b.updated_at.cmp(&a.updated_at));
    (StatusCode::OK, Json(entries)).into_response()
}

async fn get_block(
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> impl IntoResponse {
    let guard = state.marketplace_blocks.read().await;
    let Some(versions) = guard.get(&id) else {
        return (StatusCode::NOT_FOUND, Json(json!({ "error": "block not found" }))).into_response();
    };

    let Some(latest) = versions.last() else {
        return (StatusCode::NOT_FOUND, Json(json!({ "error": "block not found" }))).into_response();
    };

    (StatusCode::OK, Json(latest.clone())).into_response()
}

async fn list_block_versions(
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> impl IntoResponse {
    let guard = state.marketplace_blocks.read().await;
    let Some(versions) = guard.get(&id) else {
        return (StatusCode::NOT_FOUND, Json(json!({ "error": "block not found" }))).into_response();
    };

    let mut sorted = versions
        .iter()
        .map(|item| item.metadata.version.clone())
        .collect::<Vec<_>>();
    sorted.sort_by(|a, b| compare_semver(a, b));

    (StatusCode::OK, Json(sorted)).into_response()
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
