# Music App

A Django-based web application for managing music playlists with automatic metadata extraction from streaming platforms. The app provides secure user authentication, playlist creation/management, and integration with external music platforms (YouTube, Bandcamp, etc.) to automatically fetch track information.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Project Architecture](#project-architecture)
- [Module Descriptions](#module-descriptions)
- [High-Level User Flow](#high-level-user-flow)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
  - [Local Development](#local-development)
  - [Docker Development](#docker-development)
- [Environment Setup](#environment-setup)
- [Running the Application](#running-the-application)
- [Frontend Development](#frontend-development)
- [Testing](#testing)
- [Technology Stack](#technology-stack)
- [API Integrations](#api-integrations)
- [Development Roadmap](#development-roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**Music App** is a personal music archiving tool that allows users to:
- Create and manage playlists
- Store links to music from multiple streaming platforms
- Automatically fetch track metadata (title, artist, album, etc.)
- Organize tracks by type (tracks, mixes, samples)
- Share playlists publicly or keep them private

The application consists of three main Django modules and a TypeScript frontend workspace, each serving a distinct purpose in the system architecture.

---

## Key Features

### 🔐 Authentication & User Management
- Email-based registration with verification
- Secure token-based email verification
- Password reset functionality
- One-time use tokens for security
- Comprehensive activity logging

### 🎵 Playlist Management
- Create unlimited playlists
- Add tracks from multiple streaming platforms
- Automatic metadata extraction from YouTube, Bandcamp, and more
- Manual entry fallback if metadata unavailable
- Track positioning and ordering
- Public/private playlist visibility

### 🔗 Platform Integrations
- **YouTube** - Official API integration
- **YouTube Music** - Official API integration
- **Bandcamp** - Web scraping (JSON-LD)
- **SoundCloud** - Planned
- **Nina Protocol** - Planned

### ⚡ Performance & Optimization
- Optimized database queries (no N+1 problems)
- Transaction-safe operations
- Session-based metadata storage
- Comprehensive error handling

### 🎨 Client-Side Validation (TypeScript)
- Real-time form validation
- Email format validation
- Password strength enforcement (8+ chars, numbers, special chars, uppercase)
- Streaming link validation (YouTube, Bandcamp)
- Form text validation (length limits, mandatory fields)
- Password visibility toggle
- Comprehensive test coverage with Vitest

---

## Project Architecture

The application follows Django's multi-app architecture with clear separation of concerns:

```
┌──────────────────────────────────────────────────┐
│              music_app_main                      │
│        (Project Configuration)                   │
│  - settings.py, urls.py, wsgi.py                │
│  - Database configuration                        │
│  - Middleware & authentication backends          │
└────────────┬─────────────────────────────────────┘
            │
            ├─────────────────┬────────────────────┐
            │                 │                    │
┌───────────▼──────────┐ ┌────▼──────────────┐ ┌──▼────────────────┐
│  music_app_auth      │ │ music_app_archive │ │   Third-Party     │
│  (Authentication)    │ │ (Playlist Mgmt)   │ │   Platforms       │
│                      │ │                   │ │                   │
│ - User registration  │ │ - Playlists       │ │ - YouTube API     │
│ - Email verification │ │ - Tracks          │ │ - Bandcamp        │
│ - Login/Logout       │ │ - Streaming links │ │ - Spotify (future)│
│ - Password reset     │ │ - Metadata fetch  │ │ - SoundCloud      │
│ - Token management   │ │ - Query optimize  │ │                   │
└──────────────────────┘ └───────────────────┘ └───────────────────┘
            │
            │
┌───────────▼──────────┐
│ music_app_frontend   │
│ (TypeScript/Vite)    │
│                      │
│ - Form validation    │
│ - Client-side logic  │
│ - Password toggles   │
│ - Type definitions   │
│ - Vitest test suite  │
└──────────────────────┘
```

---

## Module Descriptions

### 1. `music_app_main` - Project Configuration

**Purpose:** Central configuration and coordination layer for the entire Django project.

**Responsibilities:**
- Django settings configuration (`settings.py`)
- URL routing coordination (includes URLs from other apps)
- WSGI/ASGI application entry point
- Database configuration
- Middleware setup
- Static files and media configuration
- Third-party package integration (e.g., Django Debug Toolbar)

**Key Files:**
```
music_app_main/
├── settings.py          # Global settings (DB, email, API keys)
├── urls.py              # Root URL configuration
├── wsgi.py              # WSGI application entry point
└── asgi.py              # ASGI application entry point (async)
```

**Settings Managed:**
- `DATABASES` - PostgreSQL/MySQL/SQLite configuration
- `INSTALLED_APPS` - Registered Django apps
- `MIDDLEWARE` - Request/response processing
- `AUTHENTICATION_BACKENDS` - Custom email-based auth
- `EMAIL_BACKEND` - SMTP configuration
- `STATIC_ROOT` / `MEDIA_ROOT` - File serving
- API keys (YouTube, Spotify, etc.)

---

### 2. `music_app_auth` - User Authentication

**Purpose:** Secure, email-based authentication system with token verification.

**Responsibilities:**
- User registration with email verification
- Login/logout functionality
- Password reset via email tokens
- One-time token generation and validation
- User session management
- Activity logging

**Key Models:**
- `CustomUser` - Extended user model with email as username
- `OneTimeToken` - Time-limited, single-use tokens
- `AppLogging` - User activity audit trail

**High-Level Process:**

#### Registration Flow
```
User submits form
    ↓
Account created (email_verified=False)
    ↓
One-time token generated
    ↓
Verification email sent
    ↓
User clicks link in email
    ↓
Token validated & marked used
    ↓
email_verified=True
    ↓
User can login
```

#### Login Flow
```
User enters email + password
    ↓
Email exists? → No → Error message
    ↓ Yes
Password correct? → No → Error message
    ↓ Yes
Email verified? → No → Error message
    ↓ Yes
Session created
    ↓
User logged in
```

#### Password Reset Flow
```
User enters email
    ↓
Reset token generated
    ↓
Email sent with reset link
    ↓
User clicks link
    ↓
Token validated
    ↓
User sets new password
    ↓
Token marked used
    ↓
Success
```

**Security Features:**
- ✓ Tokens expire after single use
- ✓ Time-limited tokens (configurable)
- ✓ Email verification required
- ✓ Password hashing (Django default)
- ✓ CSRF protection on all forms
- ✓ Activity logging for auditing
- ✓ Client-side validation (TypeScript)

**See:** [`music_app_auth/README.md`](music_app_auth/README.md) for detailed documentation.

---

### 3. `music_app_archive` - Playlist Management

**Purpose:** Core application for creating playlists and managing music tracks with automatic metadata fetching.

**Responsibilities:**
- Playlist CRUD operations
- Track management with metadata
- Streaming link validation and storage
- External API integration (YouTube, Bandcamp)
- Query optimization for performance
- Transactional data consistency

**Key Models:**
- `Playlist` - User playlists with privacy settings
- `Track` - Music tracks with metadata
- `StreamingLink` - URLs to streaming platforms
- `PlaylistTrack` - Junction table linking tracks to playlists

**High-Level Process:**

#### Create Playlist Flow
```
User creates playlist
    ↓
Validate: unique name per user
    ↓
Auto-generate slug
    ↓
Save to database
    ↓
Redirect to add tracks
```

#### Add Track Flow
```
User submits streaming URL
    ↓
Detect platform (YouTube, Bandcamp, etc.)
    ↓
Call platform API/scraper
    ↓
├─ Success → Metadata extracted
│              ↓
│          Store in session
│              ↓
│          Pre-fill form
│
└─ Failure → Empty form
              ↓
          Manual entry
    ↓
User reviews/edits metadata
    ↓
Save in transaction:
  - Track
  - StreamingLink
  - PlaylistTrack (with position)
    ↓
Success
```

#### View Playlist Flow
```
User opens playlist
    ↓
Optimized query (3 queries total):
  1. Playlist + Owner (select_related)
  2. PlaylistTracks + Tracks (select_related)
  3. All StreamingLinks (prefetch_related)
    ↓
Build track list with metadata
    ↓
Render template
```


**Performance Optimization:**
- **Without optimization:** 201 queries for 100 tracks
- **With optimization:** 3 queries for any number of tracks
- Uses `select_related()` and `prefetch_related()`
- Transaction-safe operations with `transaction.atomic()`

**Platform Integrations:**
- **YouTube** - Official API (requires key)
- **Bandcamp** - JSON-LD web scraping (no key)
- **Future:** SoundCloud, Nina Protocol

**See:** [`music_app_archive/README.md`](music_app_archive/README.md) for detailed documentation.

---

### 4. `music_app_frontend` - TypeScript Frontend Workspace

**Purpose:** Client-side validation and user interface interactions using TypeScript.

**Responsibilities:**
- Form validation (email, password, streaming links)
- Real-time error messaging
- Password visibility toggle
- Integration with Django forms
- Type-safe code with comprehensive testing

**Key Modules:**
- `validateEmail.ts` - Email format validation
- `validatePassword.ts` - Password strength validation (4 rules)
- `validateStreamingLink.ts` - URL and platform validation
- `validateAddTrackForm.ts` - Form text validation
- `showPassword.ts` - Password visibility toggle
- `musicAppAuth.ts` - Authentication form interfaces
- `musicAppPlaylist.ts` - Playlist and track interfaces

**Testing:**
- Comprehensive Vitest test suite
- ~95% code coverage
- Unit and DOM integration tests
- Edge case coverage

**Build Tools:**
- Vite - Fast build tool and dev server
- TypeScript - Type-safe JavaScript
- Vitest - Fast unit testing framework

**See:** [`music_app_frontend/README.md`](music_app_frontend/README.md) for detailed documentation.

---

## High-Level User Flow

### Complete User Journey

```
1. REGISTRATION
   User visits site → Register (TS validation) → Verify email → Account active
   
2. LOGIN
   Login page → Email + password (TS validation) → Authenticated
   
3. CREATE PLAYLIST
   Profile → Create playlist → Name + type + privacy → Save
   
4. ADD TRACKS
   Playlist → Add link (TS validation) → Paste URL (YouTube/Bandcamp)
         ↓
   API fetches metadata
         ↓
   Review/edit details → Save
         ↓
   Track added to playlist with position
   
5. VIEW PLAYLIST
   Playlist page → See all tracks with metadata
                → Click streaming links to listen
                
6. MANAGE
   Edit playlist details
   Add more tracks
   Reorder tracks (future)
   Delete tracks (future)
   Share playlist URL
```

---

## Project Structure

```
music-app/                        # Project root
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
├── environment.yml               # Conda environment
├── Dockerfile                    # Docker backend configuration
├── docker-compose.yml            # Docker services orchestration
├── .env.dev                      # Docker environment variables
├── .env                          # Local environment variables
├── .gitignore                    # Git ignore rules
├── README.md                     # This file
│
├── music_app_main/              # Project configuration
│   ├── __init__.py
│   ├── settings.py              # Global settings
│   ├── urls.py                  # Root URL configuration
│   ├── wsgi.py                  # WSGI entry point
│   └── asgi.py                  # ASGI entry point
│
├── music_app_auth/              # Authentication module
│   ├── migrations/
│   ├── src/                     # Business logic
│   ├── common/                  # Shared utilities
│   ├── views/                   # View controllers
│   ├── tests/                   # Test suite
│   ├── templates/               # HTML templates
│   ├── models.py
│   ├── forms.py
│   ├── urls.py
│   └── README.md
│
├── music_app_archive/           # Playlist management module
│   ├── migrations/
│   ├── src/                     # Business logic
│   │   ├── services.py
│   │   ├── utils.py
│   │   └── integrations/        # External APIs
│   ├── tests/
│   ├── templates/
│   ├── static/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   └── README.md
│
├── music_app_frontend/          # TypeScript frontend workspace
│   ├── node_modules/            # NPM dependencies (git-ignored)
│   ├── src/                     # TypeScript source files
│   │   ├── validateEmail.ts
│   │   ├── validatePassword.ts
│   │   ├── validateStreamingLink.ts
│   │   ├── validateAddTrackForm.ts
│   │   ├── showPassword.ts
│   │   ├── musicAppAuth.ts
│   │   └── musicAppPlaylist.ts
│   ├── tests/                   # Vitest test suite
│   │   ├── emailValidator.test.ts
│   │   ├── validatePassword.test.ts
│   │   ├── validateStreamingLink.test.ts
│   │   └── validateAddTrackForm.test.ts
│   ├── package.json             # NPM dependencies and scripts
│   ├── package-lock.json
│   ├── tsconfig.json            # TypeScript configuration
│   ├── vite.config.ts           # Vite bundler config
│   ├── vitest.config.ts         # Vitest test config
│   └── README.md
│
├── templates/                   # Global templates
│   ├── base.html
│   └── error_page.html
│
├── static/                      # Global static files
│   ├── css/
│   ├── js/
│   └── images/
│
└── logs/                        # Application logs (not in git)
    ├── auth.log
    ├── archive.log
    └── integrations.log
```

---

## Quick Start

### Installation Process

#### Mac

1. **Install Homebrew** (if not already installed):
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

2. **Install Miniconda**:
    ```bash
    brew install --cask miniconda
    ```

#### Windows

1. **Download and Install Miniconda** from the [official website](https://docs.conda.io/en/latest/miniconda.html).

2. **Open Anaconda Prompt** and follow the Software Dependencies and Running the Application for Debug steps.

### Local Development

#### Prerequisites
- Python 3.8+
- Node.js 16+
- NPM 8+
- pip or conda
- PostgreSQL/MySQL/SQLite
- Git

#### 1. Clone Repository

```bash
git clone https://github.com/yourusername/music-app.git
cd music-app
```

#### 2. Backend Setup

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Or using conda
conda env create -f environment.yml
conda activate music_app

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

#### 3. Frontend Setup

```bash
# Navigate to frontend workspace
cd music_app_frontend

# Install dependencies
npm install

# Run tests
npm test

# Build for development
npm run dev

# Build for production
npm run build
```

Visit: **http://127.0.0.1:8000/**

---

### Docker Development

Docker provides a consistent development environment with PostgreSQL, Django, and all dependencies pre-configured.

#### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

#### Architecture

```
┌─────────────────────────────────────────┐
│          Docker Compose                 │
│                                         │
│  ┌───────────────┐   ┌──────────────┐ │
│  │  postgres_db  │   │  django_web  │ │
│  │  (Port 5433)  │◄──┤  (Port 8000) │ │
│  │               │   │              │ │
│  │ PostgreSQL 16 │   │ Django App   │ │
│  │ Named Volume  │   │ Conda Env    │ │
│  └───────────────┘   └──────────────┘ │
│                                         │
│  Volumes:                               │
│  - postgres_data (persistent DB)        │
│  - static_volume (Django static files)  │
│  - . (bind mount for live code reload)  │
└─────────────────────────────────────────┘
```

#### Docker Services

**1. `db` Service (PostgreSQL):**
- Image: `postgres:16`
- Container: `postgres_db`
- Port: `5433:5432` (host:container)
- Volume: `postgres_data` for persistence
- Health check: `pg_isready`
- Credentials: Defined in `.env.dev`

**2. `web` Service (Django):**
- Build: Custom Dockerfile (`backend-dev` stage)
- Container: `django_web`
- Port: `8000:8000`
- Depends on: `db` (waits for health check)
- Volumes:
  - `.:/project_folder` (live code reload)
  - `static_volume:/project_folder/staticfiles`
- Environment: `.env.dev`
- Auto-runs: migrations + runserver

#### Quick Start with Docker

**1. Configure Environment:**

```bash
# Create Docker environment file
cp .env.dev.example .env.dev
nano .env.dev
```

Required in `.env.dev`:
```bash
# Database (matches docker-compose.yml)
POSTGRES_DB=music_app_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Django
SECRET_KEY=your-docker-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Email (same as local)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# API Keys
YOUTUBE_API_KEY=your-youtube-api-key
```

**2. Build and Start Services:**

```bash
# Build images
docker-compose build

# Start services (detached mode)
docker-compose up -d

# View logs
docker-compose logs -f web
docker-compose logs -f db

# Check service status
docker-compose ps
```

**3. Database Migrations (Auto-Run):**

Migrations run automatically on container start, but you can run manually:

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

**4. Access Application:**

- Django app: **http://localhost:8000/**
- Admin panel: **http://localhost:8000/admin/**
- PostgreSQL: **localhost:5433** (external access)

#### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services (keeps data)
docker-compose stop

# Stop and remove containers (keeps volumes)
docker-compose down

# Remove everything including volumes (⚠️ deletes database)
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build

# View logs
docker-compose logs -f [service_name]

# Execute command in container
docker-compose exec web python manage.py [command]

# Access container shell
docker-compose exec web bash

# Access database shell
docker-compose exec db psql -U postgres -d music_app_db
```

#### Frontend with Docker

The TypeScript frontend runs separately from Docker:

```bash
# In a new terminal (outside Docker)
cd music_app_frontend
npm install
npm run dev
```

The compiled JS files should be placed in Django's static directory where Docker can serve them.

#### Dockerfile Structure

```dockerfile
# Multi-stage build for development
FROM continuumio/miniconda3:latest AS backend-dev

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-traditional

# Create conda environment from environment.yml
COPY environment.yml /project_folder/
RUN conda env create -f environment.yml

# Create non-root user for security
RUN adduser --disabled-password nonroot
USER nonroot

# Copy project files
COPY . /project_folder/
WORKDIR /project_folder

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

#### Advantages of Docker Development

✅ **Consistent Environment** - Same Python, PostgreSQL versions across team  
✅ **Isolated Dependencies** - No conflicts with system packages  
✅ **Easy Database** - PostgreSQL running without local installation  
✅ **Quick Setup** - New developers start with one command  
✅ **Production Parity** - Dev environment mirrors production  
✅ **Easy Cleanup** - Remove everything with one command  

#### Troubleshooting Docker

**Database connection refused:**
```bash
# Check db service is healthy
docker-compose ps
docker-compose logs db

# Restart services
docker-compose restart
```

**Port already in use:**
```bash
# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
  - "5434:5432"  # Use 5434 instead of 5433
```

**Permission denied errors:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

**Changes not reflecting:**
```bash
# Rebuild containers
docker-compose up -d --build

# Or restart services
docker-compose restart web
```

---

## Environment Setup

### Getting API Keys

#### YouTube Data API v3
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **YouTube Data API v3**
4. Create credentials → API Key
5. Copy key to `.env` as `YOUTUBE_API_KEY`

**Free tier:** 10,000 quota units/day (sufficient for personal use)

#### Email Configuration (Gmail)
1. Enable 2-factor authentication on your Google account
2. Generate an [App Password](https://myaccount.google.com/apppasswords)
3. Use app password in `EMAIL_HOST_PASSWORD`

---

## Running the Application

### Local Development

```bash
# Backend
python manage.py runserver

# Frontend (separate terminal)
cd music_app_frontend
npm run dev
```

### Docker Development

```bash
# Start all services
docker-compose up -d

# Frontend (separate terminal)
cd music_app_frontend
npm run dev

# View logs
docker-compose logs -f web
```

### Production

```bash
# Collect static files
python manage.py collectstatic

# Frontend build
cd music_app_frontend
npm run build

# Use production WSGI server
gunicorn music_app_main.wsgi:application --workers 4 --bind 0.0.0.0:8000
```

---

## Frontend Development

The TypeScript frontend provides comprehensive client-side validation and user interactions.

### Development Workflow

```bash
cd music_app_frontend

# Install dependencies
npm install

# Start dev server with hot reload
npm run dev

# Run tests in watch mode
npm run test:watch

# Type check
npm run type-check

# Build for production
npm run build

# Run all tests
npm test

# Generate coverage report
npm run test:coverage
```

### Adding New Validation

1. Create validator function in `src/`
2. Add DOM integration
3. Write tests in `tests/`
4. Update documentation
5. Build and integrate with Django templates

See [`music_app_frontend/README.md`](music_app_frontend/README.md) for detailed frontend documentation.

---

## Testing

### Backend Tests

```bash
# Local
python manage.py test

# Docker
docker-compose exec web python manage.py test

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Frontend Tests

```bash
cd music_app_frontend

# Run all tests
npm test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

### Test Structure

```
Backend Tests:
├── music_app_auth/tests/
│   ├── test_models.py
│   ├── test_views.py
│   └── test_email_backend.py
└── music_app_archive/tests/
    ├── test_models.py
    ├── test_views.py
    ├── test_services.py
    └── test_integrations.py

Frontend Tests:
└── music_app_frontend/tests/
    ├── emailValidator.test.ts
    ├── validatePassword.test.ts
    ├── validateStreamingLink.test.ts
    └── validateAddTrackForm.test.ts
```

---

## Technology Stack

### Backend
- **Django 4.0+** - Web framework
- **Python 3.8+** - Programming language
- **PostgreSQL 16** - Production database
- **Django ORM** - Database abstraction

### Frontend
- **TypeScript 4.x+** - Type-safe JavaScript
- **Vite** - Next-generation build tool
- **Vitest** - Fast unit testing framework
- **HTML5/CSS3** - Markup and styling

### Development & Deployment
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Conda** - Python environment management
- **NPM** - JavaScript package management

### External Services
- **YouTube Data API v3** - Video metadata
- **Google SMTP** - Email sending
- **Bandcamp** - Web scraping for metadata

### Development Tools
- **Django Debug Toolbar** - Development debugging
- **Coverage.py** - Backend test coverage
- **Vitest** - Frontend test coverage
- **Git** - Version control

---

## API Integrations

### Supported Platforms

| Platform | Status | Method | Documentation |
|----------|--------|--------|--------------|
| YouTube | ✅ Live | Official API | [YouTube API Docs](https://developers.google.com/youtube/v3) |
| YouTube Music | ✅ Live | Official API | Same as YouTube |
| Bandcamp | ✅ Live | Web Scraping | Custom JSON-LD parser |
| Nina Protocol | 🔄 Planned | Official API | Custom developed|
| SoundCloud | 🔄 Planned | Web Scraping | API deprecated |


### Integration Architecture

```
User submits URL
       ↓
orchestrate_platform_api()
       ↓
detect_streaming_platform()
       ↓
    ┌──┴──────────────┐
    │                 │
    ▼                 ▼
YouTube API    Bandcamp Scraper
    │                 │
    └────────┬────────┘
             ↓
    Standardized metadata dict
             ↓
    Store in session
             ↓
    Pre-fill form
```

See [`music_app_archive/src/integrations/README.md`](music_app_archive/src/integrations/README.md) for detailed integration documentation.

---

## Development Roadmap

### Phase 1: Core Features ✅
- [x] User authentication with email verification
- [x] Basic playlist CRUD
- [x] YouTube integration
- [x] Bandcamp integration
- [x] Manual track entry
- [x] Query optimization
- [x] TypeScript frontend validation
- [x] Docker development environment

### Phase 2: Enhanced Features (In Progress) 🔄
- [ ] Update Python version
- [ ] Improve YouTube and Bandcamp API's 
- [ ] If song link exists, pull metadata from table
- [ ] SoundCloud integration
- [ ] Implement TypeScript to show relevent fields for Soundcloud mix
- [ ] Track reordering (drag-and-drop)
- [ ] Track deletion from playlists
- [ ] Playlist search functionality
- [ ] User profile customization
- [ ] Real-time validation improvements

---

## Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes (backend and/or frontend)
4. Write/update tests (Python and TypeScript)
5. Ensure all tests pass
6. Update documentation
7. Commit your changes
8. Push to branch
9. Open a Pull Request

### Code Standards

**Backend (Python/Django):**
- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings to all functions/classes
- Write tests for new features
- Keep views thin, services fat

**Frontend (TypeScript):**
- Use TypeScript strict mode
- Explicit return types on functions
- Write tests with Vitest
- Follow existing patterns
- Update relevant READMEs

### Pull Request Checklist
- [ ] Backend tests pass (`python manage.py test`)
- [ ] Frontend tests pass (`npm test`)
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Code follows project style
- [ ] Commit messages are clear

---

## Deployment

### Production Checklist

**Security:**
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use strong `SECRET_KEY`
- [ ] Enable HTTPS
- [ ] Configure CSRF settings
- [ ] Set up CORS if using API

**Database:**
- [ ] Use PostgreSQL (not SQLite)
- [ ] Configure connection pooling
- [ ] Set up database backups
- [ ] Run migrations

**Static Files:**
- [ ] Build frontend: `npm run build`
- [ ] Run `collectstatic`
- [ ] Configure CDN (optional)
- [ ] Enable gzip compression

**Docker Production:**
- [ ] Create production Dockerfile stage
- [ ] Use proper secrets management
- [ ] Configure health checks
- [ ] Set up logging
- [ ] Use Docker secrets for sensitive data

**Monitoring:**
- [ ] Set up error tracking (Sentry)
- [ ] Configure logging to files
- [ ] Set up uptime monitoring
- [ ] Configure performance monitoring

### Recommended Hosting
- **PaaS:** Heroku, Railway, Render, PythonAnywhere
- **VPS:** DigitalOcean, Linode, AWS EC2
- **Containerized:** Docker + Kubernetes, AWS ECS, Google Cloud Run

---

## Troubleshooting

### Common Issues

**Problem:** `ModuleNotFoundError: No module named 'X'`  
**Solution:** Install dependencies: `pip install -r requirements.txt`

**Problem:** `django.db.utils.OperationalError: no such table`  
**Solution:** Run migrations: `python manage.py migrate`

**Problem:** YouTube API quota exceeded  
**Solution:** Wait for quota reset (midnight PT) or request increase

**Problem:** Email verification not working  
**Solution:** Check `EMAIL_HOST_*` settings in `.env`

**Problem:** Static files not loading  
**Solution:** Run `python manage.py collectstatic`

---

## Documentation

- **Project Overview:** This file
- **Authentication Module:** [`music_app_auth/README.md`](music_app_auth/README.md)
- **Archive Module:** [`music_app_archive/README.md`](music_app_archive/README.md)
- **Frontend Workspace:** [`music_app_frontend/README.md`](music_app_frontend/README.md)
- **Services Layer:** [`music_app_archive/src/README.md`](music_app_archive/src/README.md)
- **API Integrations:** [`music_app_archive/src/integrations/README.md`](music_app_archive/src/integrations/README.md)

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

- Django Software Foundation
- YouTube Data API
- Bandcamp for JSON-LD structured data
- TypeScript and Vite communities
- Open source community

---

## Contact & Support

- **Issues:** Open an issue on GitHub
- **Discussions:** GitHub Discussions
- **Email:** support@musicapp.example.com

---

**Last Updated:** January 2026  
**Version:** 1.0.0 (Proof of Concept)  
**Maintained By:** Tim Stephens

---

## Quick Links

- [Django Documentation](https://docs.djangoproject.com/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Vite Documentation](https://vitejs.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)