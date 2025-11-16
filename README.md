# Music App

A Django-based web application for managing music playlists with automatic metadata extraction from streaming platforms. The app provides secure user authentication, playlist creation/management, and integration with external music platforms (YouTube, Bandcamp, etc.) to automatically fetch track information.

**Please note** the music_app_auth & music_app_archive are currently POC. The main reason for this project is to learn TypeScript. I'm now prioritising the implementation of TypeScript. Also as a **POC** everything is run locally. I will also add a docker file in the next iteration.



---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Project Architecture](#project-architecture)
- [Module Descriptions](#module-descriptions)
- [High-Level User Flow](#high-level-user-flow)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Environment Setup](#environment-setup)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Technology Stack](#technology-stack)
- [API Integrations](#api-integrations)
- [Development Roadmap](#development-roadmap)

---

## Overview

**Music App** is a personal music archiving tool that allows users to:
- Create and manage playlists
- Store links to music from multiple streaming platforms
- Automatically fetch track metadata (title, artist, album, etc.)
- Organize tracks by type (tracks, mixes, samples)
- Share playlists publicly or keep them private

The application consists of three main Django modules, each serving a distinct purpose in the system architecture.

---

## Key Features

### Authentication & User Management
- Email-based registration with verification
- Secure token-based email verification
- Password reset functionality
- One-time use tokens for security
- Comprehensive activity logging

### Playlist Management
- Create unlimited playlists
- Add tracks from multiple streaming platforms
- Automatic metadata extraction from YouTube, Bandcamp, and more
- Manual entry fallback if metadata unavailable
- Track positioning and ordering
- Public/private playlist visibility

### Platform Integrations
- **YouTube** - Official API integration
- **YouTube Music** - Official API integration
- **Bandcamp** - Web scraping (JSON-LD)
- **SoundCloud** - Planned
- **Nina** - Planned

### Performance & Optimization
- Optimized database queries (no N+1 problems)
- Transaction-safe operations
- Session-based metadata storage
- Comprehensive error handling

---

## Project Architecture

The application follows Django's multi-app architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────┐
│              music_app_main                     │
│        (Project Configuration)                  │
│  - settings.py, urls.py, wsgi.py                │
│  - Database configuration                       │
│  - Middleware & authentication backends         │
└───────────┬─────────────────────────────────────┘
            │
            ├─────────────────┬─────────────────────┐
            │                 │                     │
┌───────────▼─────────┐ ┌─────▼─────────────┐ ┌─────▼──────────────┐
│  music_app_auth     │ │ music_app_archive │ │   Third-Party      │
│  (Authentication)   │ │ (Playlist Mgmt)   │ │   Platforms        │
│                     │ │                   │ │                    │
│ - User registration │ │ - Playlists       │ │ - YouTube API      │
│ - Email verification│ │ - Tracks          │ │ - Bandcamp         │
│ - Login/Logout      │ │ - Streaming links │ │ - SoundCloud       │
│ - Password reset    │ │ - Metadata fetch  │ │ - Nina.            │
│ - Token management  │ │ - Query optimize  │ │                    │
└─────────────────────┘ └───────────────────┘ └────────────────────┘
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
- `DATABASES` - SQLite configuration
- `INSTALLED_APPS` - Registered Django apps
- `MIDDLEWARE` - Request/response processing
- `AUTHENTICATION_BACKENDS` - Custom email-based auth
- `EMAIL_BACKEND` - SMTP configuration
- `STATIC_ROOT` / `MEDIA_ROOT` - File serving
- API keys (YouTube, Spotify, etc.)

**High-Level Process:**
1. Receives HTTP request
2. Routes to appropriate app (auth or archive)
3. Applies middleware (auth, CSRF, sessions)
4. Returns HTTP response
5. Serves static files in development

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
- Tokens expire after single use
- Time-limited tokens (configurable)
- Email verification required
- Password hashing (Django default)
- CSRF protection on all forms
- Activity logging for auditing

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
- **Future:** SoundCloud, Nina

**See:** [`music_app_archive/README.md`](music_app_archive/README.md) for detailed documentation.

---

## High-Level User Flow

### Complete User Journey

```
1. REGISTRATION
   User visits site → Register → Verify email → Account active
   
2. LOGIN
   Login page → Email + password → Authenticated
   
3. CREATE PLAYLIST
   Profile → Create playlist → Name + type + privacy → Save
   
4. ADD TRACKS
   Playlist → Add link → Paste URL (YouTube/Bandcamp)
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
├── environment.yml               # Conda environment (alternative)
├── .env                          # Environment variables (not in git)
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
│   │   ├── custom_exceptions.py
│   │   └── django_error_utils.py
│   ├── common/                  # Shared utilities
│   │   ├── backends.py          # Email authentication backend
│   │   ├── utils.py             # Token generation
│   │   ├── validators.py        # Custom validators
│   │   └── send_email.py        # Email sending
│   ├── views/                   # View controllers
│   │   ├── app_views.py
│   │   └── main_views.py
│   ├── tests/                   # Test suite
│   ├── templates/               # HTML templates
│   ├── models.py                # CustomUser, OneTimeToken, AppLogging
│   ├── forms.py                 # Django forms
│   ├── urls.py                  # URL patterns
│   ├── admin.py                 # Admin configuration
│   └── README.md                # Auth module docs
│
├── music_app_archive/           # Playlist management module
│   ├── migrations/
│   ├── src/                     # Business logic
│   │   ├── services.py          # Business operations
│   │   ├── utils.py             # Generic utilities
│   │   └── integrations/        # External APIs
│   │       ├── main_integrations.py  # Orchestrator
│   │       ├── youtube.py            # YouTube API
│   │       ├── bandcamp.py           # Bandcamp scraper
│   │       └── README.md             # Integration docs
│   ├── tests/                   # Test suite
│   ├── templates/               # HTML templates
│   ├── static/                  # CSS, JS, images
│   ├── models.py                # Playlist, Track, StreamingLink
│   ├── forms.py                 # Django forms
│   ├── views.py                 # View controllers
│   ├── urls.py                  # URL patterns
│   ├── admin.py                 # Admin configuration
│   └── README.md                # Archive module docs
│
├── templates/                   # Global templates
│   ├── base.html               # Base template
│   └── error_page.html         # Error page
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

### Prerequisites

- Python 3.8+
- pip or conda
- SQLite
- Git

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/music-app.git
cd music-app
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Or using conda
conda env create -f environment.yml
conda activate music_app
```

### 3. Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env with your settings
nano .env
```

Required variables:
```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/music_app_db

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# API Keys
YOUTUBE_API_KEY=your-youtube-api-key
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

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

### Development

```bash
# Start development server
python manage.py runserver

# Run on specific port
python manage.py runserver 8080

# Run on all interfaces
python manage.py runserver 0.0.0.0:8000
```

---

## Testing

### Run All Tests

```bash
# All apps
python manage.py test

# Specific app
python manage.py test music_app_auth
python manage.py test music_app_archive

```

### Test Structure

```
tests/
├── music_app_auth/
│   ├── test_models.py          # User, Token tests
│   ├── test_views.py           # Auth flow tests
│   └── test_email_backend.py  # Email auth tests
│
└── music_app_archive/
    ├── test_models.py          # Playlist, Track tests
    ├── test_views.py           # View tests
    ├── test_services.py        # Business logic tests
    ├── test_integrations.py    # API integration tests
    └── test_utils.py           # Utility function tests
```

---

## Technology Stack

### Backend
- **Django 4.0+** - Web framework
- **Python 3.8+** - Programming language
- **SQLite** - Primary database as currently operating in DEV for the POC
- **Django ORM** - Database abstraction

### Frontend
- **HTML5/CSS3** - Markup and styling
- **JavaScript** - Client-side interactivity
- **Bootstrap** - CSS framework (optional)
- **TypeScript** - Planned for enhanced forms

### External Services
- **YouTube Data API v3** - Video metadata
- **Google SMTP** - Email sending
- **Bandcamp** - Web scraping for metadatam that I created myself.

### Development Tools
- **Django Debug Toolbar** - Development debugging
- **Git** - Version control
- **VS Code/PyCharm** - IDE

---

## API Integrations

### Supported Platforms

| Platform | Status | Method | Documentation |
|----------|--------|--------|--------------|
| YouTube | Live | Official API | [YouTube API Docs](https://developers.google.com/youtube/v3) |
| YouTube Music | Live | Official API | Same as YouTube |
| Bandcamp | Live | Web Scraping | Custom JSON-LD parser |
| SoundCloud | 🔄 Planned | Web Scraping | API deprecated |
| Nina | 🔄 Planned | Web Scraping | Custom JSON-LD parser |

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

### Phase 1: Core Features (Current - POC)
- [x] User authentication with email verification
- [x] Basic playlist CRUD
- [x] YouTube integration
- [x] Bandcamp integration
- [x] Manual track entry
- [x] Query optimization

### Phase 2: Enhanced Features (In Progress)
- [ ] TypeScript integration
- [ ] Dockerise the project
- [ ] SoundCloud integration
- [ ] Track reordering (drag-and-drop)
- [ ] Track deletion from playlists
- [ ] Playlist search functionality
- [ ] User profile customization

### Phase 3: Advanced Features (Planned)
- [ ] Collaborative playlists


---

### Code Standards
- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings to all functions/classes
- Write tests for new features
- Keep views thin, services fat
- Use Django best practices
- Log important operations
- Handle errors gracefully


---

## Troubleshooting

### Common Issues

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
- **Services Layer:** [`music_app_archive/src/README.md`](music_app_archive/src/README.md)
- **API Integrations:** [`music_app_archive/src/integrations/README.md`](music_app_archive/src/integrations/README.md)

---

## Acknowledgments

- Django Software Foundation
- YouTube Data API
- Bandcamp for JSON-LD structured data
- Open source community

---
