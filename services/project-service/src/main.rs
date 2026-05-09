use axum::{
    extract::Path,
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::{collections::HashMap, net::SocketAddr, sync::Arc};
use tokio::sync::RwLock;
use tower_http::{cors::CorsLayer, trace::TraceLayer};
use uuid::Uuid;

#[derive(Clone, Default)]
struct AppState {
    projects: Arc<RwLock<HashMap<Uuid, ProjectMeta>>>,
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

#[tokio::main]
async fn main() {
    let state = AppState::default();

    let app = Router::new()
        .route("/health", get(health))
        .route("/projects", post(create_project))
        .route("/projects/:id", get(get_project))
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
    axum::extract::State(state): axum::extract::State<AppState>,
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
    axum::extract::State(state): axum::extract::State<AppState>,
    Path(id): Path<Uuid>,
) -> impl IntoResponse {
    let guard = state.projects.read().await;
    match guard.get(&id) {
        Some(project) => (StatusCode::OK, Json(project.clone())).into_response(),
        None => (StatusCode::NOT_FOUND, "project not found").into_response(),
    }
}
