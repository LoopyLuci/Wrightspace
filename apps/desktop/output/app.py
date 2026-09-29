#!/usr/bin/env python3
"""WebBuilder Flask Backend: Production-grade REST API with comprehensive error handling, logging, and security."""

import logging
import os
import re
import secrets
import traceback
from datetime import datetime, timedelta
from functools import wraps
from typing import Any

from flask import Flask, request, jsonify, send_from_directory, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

# ═══════════════════════════════════════════════════════════════════════════
# Logging Setup
# ═══════════════════════════════════════════════════════════════════════════

def setup_logging(app: Flask) -> None:
    """Setup structured logging for the Flask app."""
    from logging.handlers import RotatingFileHandler

    log_dir = os.path.join(os.path.expanduser("~"), ".webbuilder", "logs")
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d | %(message)s"
    )

    # File handler
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "flask.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Error file handler
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, "flask.error.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(logging.INFO)


# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

class Config:
    """Flask configuration with environment variable support."""
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///webbuilder.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRATION_HOURS = int(os.environ.get("JWT_EXPIRATION_HOURS", "24"))
    RATE_LIMIT_DEFAULT = os.environ.get("RATE_LIMIT_DEFAULT", "100 per hour")
    RATE_LIMIT_LOGIN = os.environ.get("RATE_LIMIT_LOGIN", "5 per minute")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB


# ═══════════════════════════════════════════════════════════════════════════
# Extensions
# ═══════════════════════════════════════════════════════════════════════════

db = SQLAlchemy()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)


# ═══════════════════════════════════════════════════════════════════════════
# Models
# ═══════════════════════════════════════════════════════════════════════════

class User(UserMixin, db.Model):
    """User model with validation."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password: str) -> None:
        """Hash and set password."""
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify password."""
        return check_password_hash(self.password_hash, password)

    def generate_token(self) -> str:
        """Generate JWT token."""
        payload = {
            "user_id": self.id,
            "exp": datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token: str) -> "User | None":
        """Verify JWT token and return user."""
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            return User.query.get(payload["user_id"])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))


class Project(db.Model):
    """Project model."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Analytics(db.Model):
    """Analytics event model."""
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    event_data = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════
# Decorators & Middleware
# ═══════════════════════════════════════════════════════════════════════════

def token_required(f):
    """Decorator to require valid JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token missing"}), 401
        token = token.replace("Bearer ", "")
        user = User.verify_token(token)
        if not user:
            return jsonify({"error": "Invalid or expired token"}), 401
        g.current_user = user
        return f(user, *args, **kwargs)
    return decorated


def validate_json(*required_fields):
    """Decorator to validate JSON request body."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            data = request.get_json(silent=True)
            if not data:
                return jsonify({"error": "Invalid or missing JSON body"}), 400
            missing = [field for field in required_fields if field not in data]
            if missing:
                return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400
            return f(*args, **kwargs)
        return decorated
    return decorator


# ═══════════════════════════════════════════════════════════════════════════
# App Factory
# ═══════════════════════════════════════════════════════════════════════════

def create_app() -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__, static_folder=".", static_url_path="")
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    limiter.init_app(app)
    CORS(app)

    # Setup logging
    setup_logging(app)

    # ═══════════════════════════════════════════════════════════════════
    # Security Headers
    # ═══════════════════════════════════════════════════════════════════

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = "no-store"
        return response

    # ═══════════════════════════════════════════════════════════════════
    # Request Logging
    # ═══════════════════════════════════════════════════════════════════

    @app.before_request
    def log_request():
        g.start_time = datetime.utcnow()
        app.logger.info(f"→ {request.method} {request.path} from {request.remote_addr}")

    @app.after_request
    def log_response(response):
        duration = (datetime.utcnow() - g.get("start_time", datetime.utcnow())).total_seconds()
        app.logger.info(f"← {request.method} {request.path} {response.status_code} ({duration:.3f}s)")
        return response

    # ═══════════════════════════════════════════════════════════════════
    # Error Handlers
    # ═══════════════════════════════════════════════════════════════════

    @app.errorhandler(400)
    def bad_request(error):
        app.logger.warning(f"Bad request: {error}")
        return jsonify({"error": "Bad request", "status": 400}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found", "status": 404}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"error": "Method not allowed", "status": 405}), 405

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        app.logger.warning(f"Rate limit exceeded: {request.remote_addr}")
        return jsonify({"error": "Rate limit exceeded", "status": 429}), 429

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {error}\n{traceback.format_exc()}")
        db.session.rollback()
        return jsonify({"error": "Internal server error", "status": 500}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        app.logger.error(f"Unhandled exception: {error}\n{traceback.format_exc()}")
        db.session.rollback()
        return jsonify({"error": "Internal server error", "status": 500}), 500

    # ═══════════════════════════════════════════════════════════════════
    # API Routes
    # ═══════════════════════════════════════════════════════════════════

    @app.route("/api/v1/health")
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
        })

    @app.route("/api/v1/projects", methods=["GET"])
    @token_required
    def get_projects(user):
        """Get all projects for current user."""
        try:
            projects = Project.query.filter_by(user_id=user.id).all()
            return jsonify({
                "projects": [{
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "created_at": p.created_at.isoformat(),
                    "updated_at": p.updated_at.isoformat(),
                } for p in projects]
            })
        except Exception as e:
            app.logger.error(f"Failed to get projects: {e}")
            return jsonify({"error": "Failed to retrieve projects"}), 500

    @app.route("/api/v1/projects", methods=["POST"])
    @token_required
    @validate_json("name")
    def create_project(user):
        """Create a new project."""
        try:
            data = request.get_json()

            # Validate name
            name = data.get("name", "").strip()
            if not name or len(name) > 200:
                return jsonify({"error": "Name must be 1-200 characters"}), 400

            project = Project(
                name=name,
                description=data.get("description", "")[:5000],
                content=data.get("content", "{}"),
                user_id=user.id,
            )
            db.session.add(project)
            db.session.commit()

            app.logger.info(f"Project created: {project.id} by user {user.id}")
            return jsonify({"id": project.id, "name": project.name}), 201

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Failed to create project: {e}")
            return jsonify({"error": "Failed to create project"}), 500

    @app.route("/api/v1/projects/<int:project_id>", methods=["GET"])
    @token_required
    def get_project(user, project_id):
        """Get a specific project."""
        try:
            project = Project.query.filter_by(id=project_id, user_id=user.id).first()
            if not project:
                return jsonify({"error": "Project not found"}), 404
            return jsonify({
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "content": project.content,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
            })
        except Exception as e:
            app.logger.error(f"Failed to get project {project_id}: {e}")
            return jsonify({"error": "Failed to retrieve project"}), 500

    @app.route("/api/v1/projects/<int:project_id>", methods=["PUT"])
    @token_required
    @validate_json()
    def update_project(user, project_id):
        """Update a project."""
        try:
            project = Project.query.filter_by(id=project_id, user_id=user.id).first()
            if not project:
                return jsonify({"error": "Project not found"}), 404

            data = request.get_json()
            if "name" in data:
                name = data["name"].strip()
                if not name or len(name) > 200:
                    return jsonify({"error": "Name must be 1-200 characters"}), 400
                project.name = name
            if "description" in data:
                project.description = data["description"][:5000]
            if "content" in data:
                project.content = data["content"]

            db.session.commit()
            app.logger.info(f"Project updated: {project.id}")
            return jsonify({"id": project.id, "name": project.name})

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Failed to update project: {e}")
            return jsonify({"error": "Failed to update project"}), 500

    @app.route("/api/v1/projects/<int:project_id>", methods=["DELETE"])
    @token_required
    def delete_project(user, project_id):
        """Delete a project."""
        try:
            project = Project.query.filter_by(id=project_id, user_id=user.id).first()
            if not project:
                return jsonify({"error": "Project not found"}), 404

            db.session.delete(project)
            db.session.commit()
            app.logger.info(f"Project deleted: {project.id}")
            return jsonify({"message": "Project deleted"})

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Failed to delete project: {e}")
            return jsonify({"error": "Failed to delete project"}), 500

    @app.route("/api/v1/analytics", methods=["POST"])
    @validate_json()
    def track_event():
        """Track an analytics event."""
        try:
            data = request.get_json()
            event = Analytics(
                event_type=data.get("event", "page_view")[:50],
                event_data=data.get("data", {}),
                ip_address=request.remote_addr,
                user_agent=request.headers.get("User-Agent", "")[:255],
            )
            db.session.add(event)
            db.session.commit()
            return jsonify({"status": "ok"}), 201
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Failed to track event: {e}")
            return jsonify({"error": "Failed to track event"}), 500

    # ═══════════════════════════════════════════════════════════════════
    # Auth Routes
    # ═══════════════════════════════════════════════════════════════════

    @app.route("/auth/register", methods=["POST"])
    @limiter.limit(Config.RATE_LIMIT_LOGIN)
    @validate_json("email", "password")
    def register():
        """Register a new user."""
        try:
            data = request.get_json()
            email = data["email"].strip().lower()
            password = data["password"]
            name = data.get("name", "").strip()

            # Validate email
            if not User.validate_email(email):
                return jsonify({"error": "Invalid email format"}), 400

            # Validate password
            if len(password) < 8:
                return jsonify({"error": "Password must be at least 8 characters"}), 400
            if len(password) > 128:
                return jsonify({"error": "Password must be at most 128 characters"}), 400

            # Check existing
            if User.query.filter_by(email=email).first():
                return jsonify({"error": "Email already registered"}), 409

            # Validate name
            if not name:
                name = email.split("@")[0]
            if len(name) > 100:
                return jsonify({"error": "Name must be at most 100 characters"}), 400

            user = User(email=email, name=name, role="user")
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            app.logger.info(f"User registered: {email}")
            return jsonify({
                "message": "User created successfully",
                "user": {"id": user.id, "email": user.email, "name": user.name},
            }), 201

        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Registration failed: {e}")
            return jsonify({"error": "Registration failed"}), 500

    @app.route("/auth/login", methods=["POST"])
    @limiter.limit(Config.RATE_LIMIT_LOGIN)
    @validate_json("email", "password")
    def login():
        """Login and get JWT token."""
        try:
            data = request.get_json()
            email = data["email"].strip().lower()
            password = data["password"]

            user = User.query.filter_by(email=email).first()
            if not user or not user.check_password(password):
                return jsonify({"error": "Invalid credentials"}), 401

            user.last_login = datetime.utcnow()
            db.session.commit()
            token = user.generate_token()

            app.logger.info(f"User logged in: {email}")
            return jsonify({
                "token": token,
                "user": {"id": user.id, "email": user.email, "name": user.name, "role": user.role},
            })

        except Exception as e:
            app.logger.error(f"Login failed: {e}")
            return jsonify({"error": "Login failed"}), 500

    @app.route("/auth/logout", methods=["POST"])
    @token_required
    def logout(user):
        """Logout (client-side token invalidation)."""
        return jsonify({"message": "Logged out successfully"})

    @app.route("/auth/me", methods=["GET"])
    @token_required
    def get_current_user(user):
        """Get current user info."""
        return jsonify({
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
        })

    # ═══════════════════════════════════════════════════════════════════
    # Static File Serving
    # ═══════════════════════════════════════════════════════════════════

    @app.route("/")
    def index():
        return send_from_directory(".", "index.html")

    @app.route("/<path:path>")
    def serve_static(path):
        return send_from_directory(".", path)

    # Create tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=False, host="0.0.0.0", port=5000)
