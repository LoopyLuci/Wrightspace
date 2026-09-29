"""
Tests for TaskFlow Flask Backend
"""
import pytest
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db, User, Project, Analytics

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_register(client):
    """Test user registration"""
    response = client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123',
        'name': 'Test User'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['user']['email'] == 'test@example.com'

def test_login(client):
    """Test user login"""
    # Register first
    client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123',
        'name': 'Test User'
    })
    
    # Login
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data

def test_protected_route_without_token(client):
    """Test that protected routes require token"""
    response = client.get('/api/v1/projects')
    assert response.status_code == 401

def test_create_project(client):
    """Test project creation"""
    # Register and login
    client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123',
        'name': 'Test User'
    })
    login_response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = json.loads(login_response.data)['token']
    
    # Create project
    response = client.post('/api/v1/projects', 
        json={'name': 'Test Project', 'description': 'A test project'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 201

def test_track_analytics(client):
    """Test analytics tracking"""
    response = client.post('/api/v1/analytics', json={
        'event': 'page_view',
        'data': {'path': '/'}
    })
    assert response.status_code == 201

def test_security_headers(client):
    """Test security headers are present"""
    response = client.get('/')
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'DENY'
