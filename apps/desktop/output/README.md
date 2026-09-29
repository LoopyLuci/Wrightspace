# TaskFlow - Complete Web Application

## Architecture

```
taskflow/
├── app.py              # Flask backend with API, auth, database
├── index.html          # Enhanced frontend with UX/accessibility/SEO
├── sitemap.xml         # SEO sitemap
├── robots.txt          # Crawler directives
├── test_app.py         # Pytest test suite
├── requirements.txt    # Python dependencies
└── taskflow.db         # SQLite database (auto-created)
```

## Features Implemented

### Backend (Flask)
- **REST API** with `/api/v1/` prefix
- **JWT Authentication** - Register, Login, Logout with token-based auth
- **Rate Limiting** - 5/minute for login, 100/hour default
- **Security Headers** - CSP, X-Frame-Options, HSTS, X-Content-Type-Options
- **SQLAlchemy ORM** - User, Project, Analytics models
- **Input Validation** - Email uniqueness, password length
- **Error Handling** - 404, 500, 429 with JSON responses
- **CORS** - Cross-origin resource sharing

### Frontend
- **WCAG 2.1 AA** compliant (ARIA, skip-nav, focus styles, reduced-motion)
- **SEO** - Open Graph, Twitter Cards, JSON-LD, sitemap.xml, canonical URL
- **Performance** - Preload critical assets, lazy load below-fold images
- **UX** - Scroll progress, back-to-top, smooth scroll offset, mobile menu
- **Responsive** - Mobile-first with breakpoints
- **Analytics** - Page view tracking via API

### Security
- Password hashing (bcrypt via werkzeug)
- JWT token expiration
- Rate limiting on auth endpoints
- Security headers on all responses
- Input validation and sanitization

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/v1/health | No | Health check |
| POST | /auth/register | No | User registration |
| POST | /auth/login | No | User login (returns JWT) |
| POST | /auth/logout | Yes | Logout |
| GET | /api/v1/projects | Yes | List user projects |
| POST | /api/v1/projects | Yes | Create project |
| POST | /api/v1/analytics | No | Track analytics event |
| GET | / | No | Serve index.html |
| GET | /sitemap.xml | No | SEO sitemap |
| GET | /robots.txt | No | Crawler directives |

## Quick Start

```bash
# Install dependencies
pip install flask flask-sqlalchemy flask-login flask-limiter flask-cors pyjwt bcrypt pytest

# Run the server
python app.py

# Run tests
pytest test_app.py -v
```

## Testing

```bash
pytest test_app.py -v
```

## Deployment

For production:
- Use gunicorn: `gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()`
- Set `SECRET_KEY` environment variable
- Use PostgreSQL: `DATABASE_URL=postgresql://...`
- Enable HTTPS for HSTS to work
