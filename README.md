# Music App

A Django-based web application for archiving and managing music playlists, with automatic metadata extraction from streaming platforms including YouTube and Bandcamp. The app features secure email-based authentication, playlist and track management, and a Selenium-powered scraping layer for platforms without a public API.

The project is deliberately full-stack in scope, built to demonstrate practical experience across backend web development (Django, PostgreSQL), client-side validation (TypeScript, Vite), infrastructure (Docker, Selenium Grid), and a modern data analytics stack — with a Snowflake data warehouse, dbt transformation layer following medallion architecture, and an Airflow pipeline orchestrating the full extract → load → transform workflow.

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
- [Data Analytics Layer](#data-analytics-layer)
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

The application consists of three main Django modules, a TypeScript frontend workspace, and a data analytics layer built on Snowflake, dbt, and Airflow — each serving a distinct purpose in the system architecture.

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
- **Bandcamp** - Advanced web scraping with Selenium (headless Chrome)
- **SoundCloud** - Planned
- **Nina Protocol** - Planned

### Performance & Optimization
- Optimized database queries (no N+1 problems)
- Transaction-safe operations
- Session-based metadata storage
- Comprehensive error handling
- Selenium-based web scraping with anti-detection measures

### Client-Side Validation (TypeScript)
- Real-time form validation
- Email format validation
- Password strength enforcement (8+ chars, numbers, special chars, uppercase)
- Streaming link validation (YouTube, Bandcamp)
- Form text validation (length limits, mandatory fields)
- Password visibility toggle
- Comprehensive test coverage with Vitest

---

## Project Architecture

The application follows Django's multi-app architecture with clear separation of concerns, extended by a modern data analytics stack:

```
┌──────────────────────────────────────────────────┐
│              music_app_main                      │
│        (Project Configuration)                   │
│  - settings.py, urls.py, wsgi.py                 │ 
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
│ - Login/Logout       │ │ - Streaming links │ │   (Selenium)      │
│ - Password reset     │ │ - Metadata fetch  │ │ - SoundCloud      │
│ - Token management   │ │ - Query optimize  │ │                   │
└──────────────────────┘ └────────┬──────────┘ └───────────────────┘
            │                     │
            │                     │
┌───────────▼──────────┐          │
│ music_app_frontend   │          │
│ (TypeScript/Vite)    │          │
│                      │          │
│ - Form validation    │          │
│ - Client-side logic  │          │
│ - Password toggles   │          │
│ - Type definitions   │          │
│ - Vitest test suite  │          │
└──────────────────────┘          │
                                  │ (source data)
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Data Analytics Layer                        │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │    Airflow       │  │      dbt         │  │   Snowflake   │  │
│  │  (Orchestration) │  │ (Transformation) │  │  (Warehouse)  │  │
│  │                  │  │                  │  │               │  │
│  │  - DAG scheduling│→ │  - RAW → STAGING │→ │  - RAW        │  │
│  │  - Pipeline runs │  │  - STAGING→MARTS │  │  - STAGING    │  │
│  │  - Monitoring    │  │  - Data quality  │  │  - MARTS      │  │
│  │                  │  │    tests         │  │               │  │
│  └──────────────────┘  └──────────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Docker Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose                          │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐  │
│  │   PostgreSQL     │  │  Selenium Grid   │  │  Django   │  │
│  │   Database       │  │  (Chromium)      │  │  Web App  │  │
│  │                  │  │                  │  │           │  │
│  │  Port: 5433      │  │  Port: 4444      │  │ Port: 8000│  │
│  │  Volume: pgdata  │  │  VNC: 7900       │  │ Volume: . │  │
│  │                  │  │  shm: 725mb      │  │           │  │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬────┘  │
│           │                     │                   │       │
│           └─────────────────────┴───────────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │                        │                   │
         │                        │                   │
    [Database]              [WebDriver]         [Application]
    Persistence            Web Scraping           Logic
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
- Selenium remote URL configuration for Docker environments

**Key Files:**
```
music_app_main/
├── settings.py          # Global settings (DB, email, API keys, Selenium)
├── urls.py              # Root URL configuration
├── wsgi.py              # WSGI application entry point
└── asgi.py              # ASGI application entry point (async)
```

**Settings Managed:**
- `DATABASES` - PostgreSQL configuration
- `INSTALLED_APPS` - Registered Django apps
- `MIDDLEWARE` - Request/response processing
- `AUTHENTICATION_BACKENDS` - Custom email-based auth
- `EMAIL_BACKEND` - SMTP configuration
- `STATIC_ROOT` / `MEDIA_ROOT` - File serving
- `SELENIUM_REMOTE_URL` - Selenium WebDriver endpoint
- API keys (YouTube, etc.)

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
- ✓ Password hashing with Argon2
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
- External API integration (YouTube API, Bandcamp Selenium scraping)
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

#### Add Track Flow (with Bandcamp Selenium Integration)
```
User submits streaming URL
    ↓
Detect platform (YouTube, Bandcamp, etc.)
    ↓
Call platform API/scraper
    ↓
├─ YouTube → YouTube API
│              ↓
│          Extract metadata
│
└─ Bandcamp → Selenium WebDriver
               ↓
           Launch headless Chrome
               ↓
           Navigate to URL with anti-detection
               ↓
           Wait for dynamic content
               ↓
           Parse HTML with BeautifulSoup
               ↓
           Extract track metadata
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

**Query Optimization:**
- ✓ `select_related()` for foreign keys
- ✓ `prefetch_related()` for reverse lookups
- ✓ Minimal database queries per request
- ✓ No N+1 query problems
- ✓ Transaction-wrapped operations

**Bandcamp Integration Features:**
- ✓ Selenium WebDriver for JavaScript-rendered content
- ✓ Headless Chrome with anti-detection measures
- ✓ Realistic browser fingerprinting
- ✓ Random delays to mimic human behavior
- ✓ Works in both local and Docker environments
- ✓ Session pooling via Selenium Grid
- ✓ VNC debugging capability (port 7900)

**See:** [`music_app_archive/README.md`](music_app_archive/README.md) for detailed documentation.

---

### 4. `music_app_frontend` - TypeScript Validation Layer

**Purpose:** Client-side validation and interactive UI enhancements.

**Responsibilities:**
- Real-time form validation
- Password strength checking
- Email format validation
- Streaming URL validation
- Interactive UI elements (password visibility toggles)

**Key Validation Functions:**
- `validateEmail()` - Email format checking
- `validatePassword()` - Password strength requirements
- `validateStreamingLink()` - URL platform detection
- `validateAddTrackForm()` - Complete form validation

**Testing:**
- ✓ Vitest unit tests
- ✓ 100% code coverage on validators
- ✓ Edge case handling
- ✓ Fast test execution with Vite

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
   Delete tracks
   Delete playlist(s)
   Share playlist URL (future)
```

---

## Project Structure

```
music_app/
│
├── music_app_main/              # Django project configuration
│   ├── settings.py              # Global settings (includes Selenium config)
│   ├── urls.py                  # Root URL routing
│   └── wsgi.py                  # WSGI entry point
│
├── music_app_auth/              # Authentication module
│   ├── models.py                # CustomUser, OneTimeToken, AppLogging
│   ├── views.py                 # Register, login, verify, password reset
│   ├── backends.py              # Custom email authentication backend
│   ├── tokens.py                # Token generation/validation
│   └── tests/                   # Authentication tests
│
├── music_app_archive/           # Playlist management module
│   ├── models.py                # Playlist, Track, StreamingLink
│   ├── views.py                 # CRUD views
│   ├── forms.py                 # Django forms
│   ├── src/                     # Service layer
│   │   ├── services.py          # Business logic
│   │   ├── integrations/        # Platform integrations
│   │   │   ├── youtube.py       # YouTube API
│   │   │   ├── bandcamp.py      # Selenium scraper with anti-detection
│   │   │   └── README.md        # Integration documentation
│   │   └── utils.py             # Helper functions
│   └── tests/                   # Archive module tests
│
├── music_app_frontend/          # TypeScript validation layer
│   ├── src/
│   │   ├── validators/          # Validation functions
│   │   │   ├── emailValidator.ts
│   │   │   ├── validatePassword.ts
│   │   │   ├── validateStreamingLink.ts
│   │   │   └── validateAddTrackForm.ts
│   │   └── types/               # TypeScript type definitions
│   ├── tests/                   # Vitest unit tests
│   ├── vite.config.ts           # Vite configuration
│   ├── tsconfig.json            # TypeScript configuration
│   └── package.json             # NPM dependencies
│
├── airflow/                         # Pipeline orchestration
│   └── dags/
│       ├── music_app_pipeline.py    # Main ETL DAG (extract → load → dbt run → dbt test)
│       └── README.md                # DAG setup and connection guide
│
├── dbt/                         # Data analytics layer
│   ├── models/
│   │   ├── staging/             # Cleaned & standardised source data
│   │   └── marts/               # Business-ready analytical models
│   ├── tests/                   # dbt data quality tests
│   ├── macros/                  # Reusable SQL macros
│   ├── seeds/                   # Static reference data
│   ├── snapshots/               # Slowly changing dimension tracking
│   └── dbt_project.yml          # dbt project configuration
│
├── static/                      # Static files (CSS, JS, images)
├── staticfiles/                 # Collected static files (production)
├── templates/                   # Global Django templates
│
├── docker-compose.yml           # Multi-container orchestration
├── Dockerfile                   # Django app containerization
├── environment.yml              # Conda environment (Selenium packages)
├── requirements.txt             # Python dependencies (alternative to Conda)
├── .env.dev                     # Development environment variables
├── .env.prod                    # Production environment variables
└── manage.py                    # Django management script
```

---

## Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended for easiest setup)
- OR **Python 3.11.9** + **PostgreSQL 16** (for local development)
- **Node.js 18+** and **npm** (for frontend development)
- **Conda** (optional, for local environment management)

---

### Docker Development (Recommended)

The easiest way to run the application is with Docker Compose, which automatically sets up:
- PostgreSQL database
- Django web application
- Selenium Chrome service for Bandcamp scraping

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/music_app.git
cd music_app
```

#### 2. Create Environment Files

Create `.env.dev` with the following variables:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database (PostgreSQL in Docker)
DATABASE_URL=postgresql://postgres:postgres@db:5432/music_app_db
POSTGRES_DB=music_app_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Selenium Configuration
SELENIUM_REMOTE_URL=http://selenium:4444

# Email Configuration (Google SMTP example)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password

# YouTube API
YOUTUBE_API_KEY=your-youtube-api-key

# Application URLs
SITE_URL=http://localhost:8000
```

#### 3. Build and Start Services

```bash
docker-compose up --build
```

This command will:
- Build the Django application container
- Start PostgreSQL database (port 5433)
- Start Selenium Chrome service (port 4444, VNC on 7900)
- Run database migrations
- Start Django development server (port 8000)

#### 4. Access the Application

- **Web App:** http://localhost:8000
- **Selenium Grid Console:** http://localhost:4444
- **Selenium VNC (debugging):** vnc://localhost:7900 (password: secret)

#### 5. Create Superuser (Optional)

```bash
docker-compose exec web python manage.py createsuperuser
```

#### 6. Stop Services

```bash
docker-compose down
```

To remove volumes (database data):
```bash
docker-compose down -v
```

---

### Local Development (Without Docker)

If you prefer to run services locally:

#### 1. Install PostgreSQL 16

Follow the installation guide for your OS: https://www.postgresql.org/download/

Create database:
```bash
psql -U postgres
CREATE DATABASE music_app_db;
\q
```

#### 2. Install Chrome and ChromeDriver

**Linux:**
```bash
# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb

# ChromeDriver will be auto-managed by webdriver-manager
```

**macOS:**
```bash
brew install --cask google-chrome
# ChromeDriver will be auto-managed by webdriver-manager
```

**Windows:**
Download and install Chrome from: https://www.google.com/chrome/

#### 3. Set Up Python Environment

**Option A: Using Conda (Recommended)**

```bash
# Create environment from environment.yml
conda env create -f environment.yml

# Activate environment
conda activate music_app

# Note: environment.yml includes selenium and webdriver-manager
```

**Option B: Using venv**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
```

#### 4. Configure Environment Variables

Create `.env.dev`:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Local PostgreSQL)
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/music_app_db

# Selenium Configuration (leave empty for local ChromeDriver)
SELENIUM_REMOTE_URL=

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password

# YouTube API
YOUTUBE_API_KEY=your-youtube-api-key

# Application URLs
SITE_URL=http://localhost:8000
```

#### 5. Run Migrations

```bash
python manage.py migrate
```

#### 6. Create Superuser

```bash
python manage.py createsuperuser
```

#### 7. Run Development Server

```bash
python manage.py runserver
```

Access at: http://localhost:8000

---

## Environment Setup

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-abc123...` |
| `DEBUG` | Debug mode (True/False) | `True` |
| `ALLOWED_HOSTS` | Allowed host domains | `localhost,127.0.0.1` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SELENIUM_REMOTE_URL` | Selenium WebDriver endpoint (Docker) | `http://selenium:4444` (leave empty for local) |
| `EMAIL_HOST` | SMTP server | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_HOST_USER` | Email username | `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Email password/app password | `your-app-password` |
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | `AIzaSyD...` |
| `SITE_URL` | Full site URL | `http://localhost:8000` |

### Docker-Specific Configuration

The `docker-compose.yml` defines three services:

#### 1. PostgreSQL Database (`db`)
```yaml
services:
  db:
    image: postgres:16
    ports:
      - "5433:5432"  # External:Internal
    environment:
      - POSTGRES_DB=music_app_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
```

#### 2. Selenium Chrome (`selenium`)
```yaml
  selenium:
    image: selenium/standalone-chromium:latest
    shm_size: 725mb  # Prevent Chrome crashes
    ports:
      - "4444:4444"  # WebDriver endpoint
      - "7900:7900"  # VNC for debugging
    environment:
      - SE_NODE_MAX_SESSIONS=5
      - SE_NODE_SESSION_TIMEOUT=300
```

**VNC Debugging:** Connect to `vnc://localhost:7900` (password: `secret`) to watch Chrome sessions in real-time.

#### 3. Django Web Application (`web`)
```yaml
  web:
    build:
      context: .
      target: backend-dev
    command: >
      bash -c "python manage.py migrate
      && python manage.py runserver 0.0.0.0:8000"
    ports:
      - "8000:8000"
    volumes:
      - .:/project_folder
      - static_volume:/project_folder/staticfiles
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/music_app_db
      - SELENIUM_REMOTE_URL=http://selenium:4444
    depends_on:
      db:
        condition: service_healthy
      selenium:
        condition: service_started
```

### Bandcamp Scraper Configuration

The Bandcamp integration (`bandcamp.py`) automatically detects the environment:

**Docker Environment:**
- Uses `SELENIUM_REMOTE_URL` environment variable
- Connects to Selenium Grid service
- Shares session pool across requests

**Local Environment:**
- Uses `webdriver-manager` to auto-download ChromeDriver
- Runs Chrome locally
- No additional setup required

**Anti-Detection Features:**
- Headless mode with `--headless=new`
- Realistic User-Agent strings
- Disables automation flags
- Random delays to mimic human behavior
- Window scrolling simulation

---

## Running the Application

### Development Server

**Docker:**
```bash
docker-compose up
```

**Local:**
```bash
python manage.py runserver
```

### Database Migrations

**Docker:**
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

**Local:**
```bash
python manage.py makemigrations
python manage.py migrate
```

### Create Superuser

**Docker:**
```bash
docker-compose exec web python manage.py createsuperuser
```

**Local:**
```bash
python manage.py createsuperuser
```

### Collect Static Files (Production)

**Docker:**
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

**Local:**
```bash
python manage.py collectstatic --noinput
```

### Django Shell

**Docker:**
```bash
docker-compose exec web python manage.py shell
```

**Local:**
```bash
python manage.py shell
```

### View Logs

**Docker:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f selenium
docker-compose logs -f db
```

---

## Frontend Development

### Setup

```bash
cd music_app_frontend
npm install
```

### Development

```bash
# Build TypeScript
npm run build

# Watch mode (auto-rebuild on changes)
npm run dev

# Type checking
npm run type-check
```

### Testing

```bash
# Run tests
npm test

# Watch mode
npm run test:watch

# Coverage report
npm run test:coverage
```

### Integration with Django

The compiled TypeScript is served as static files:

1. TypeScript compiles to `dist/`
2. Django serves from `staticfiles/` after `collectstatic`
3. Templates reference via `{% static 'frontend/...' %}`

---

## Testing

### Backend Tests

```bash
# Run all Django tests
python manage.py test

# Specific app
python manage.py test music_app_auth
python manage.py test music_app_archive

# With verbosity
python manage.py test --verbosity=2

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
    └── test_integrations/
        ├── test_youtube.py
        └── test_bandcamp.py        # Tests Selenium scraper

Frontend Tests:
└── music_app_frontend/tests/
    ├── emailValidator.test.ts
    ├── validatePassword.test.ts
    ├── validateStreamingLink.test.ts
    └── validateAddTrackForm.test.ts
```

### Testing Bandcamp Integration

```python
# In Django shell or test
from music_app_archive.src.integrations.bandcamp import (
    get_soup,
    scrape_bandcamp_page,
    orchestrate_bandcamp_meta_data_dictionary
)

# Test scraping
url = "https://artist.bandcamp.com/track/song-name"
metadata = orchestrate_bandcamp_meta_data_dictionary(url)
print(metadata)
# Output: {
#     'track_type': 'track',
#     'track_name': 'Song Name',
#     'artist': 'Artist Name',
#     'album_name': 'Album Name',
#     'streaming_platform': 'bandcamp',
#     'streaming_link': 'https://...',
#     ...
# }
```

---

## Technology Stack

### Data Analytics
- **Snowflake** - Cloud data warehouse (RAW / STAGING / MARTS schemas)
- **dbt Cloud** - SQL-based data transformation and modelling
- **Apache Airflow** - Pipeline orchestration (extract → load → dbt run → dbt test)

### Backend
- **Django 4.2.20** - Web framework
- **Python 3.11.9** - Programming language
- **PostgreSQL 16** - Production database
- **Django ORM** - Database abstraction
- **Selenium 4.40.0** - Browser automation for web scraping
- **BeautifulSoup 4.14.2** - HTML parsing
- **webdriver-manager 4.0.2** - Automatic ChromeDriver management

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
- **Selenium Grid** - Distributed browser testing

### External Services
- **YouTube Data API v3** - Video metadata
- **Google SMTP** - Email sending
- **Bandcamp** - Web scraping with Selenium (headless Chrome)

### Development Tools
- **Django Debug Toolbar** - Development debugging
- **Coverage.py** - Backend test coverage
- **Vitest** - Frontend test coverage
- **Git** - Version control
- **VNC** - Selenium session debugging

---

## API Integrations

### Supported Platforms

| Platform | Status | Method | Technology | Documentation |
|----------|--------|--------|-----------|--------------|
| YouTube |  Live | Official API | REST API | [YouTube API Docs](https://developers.google.com/youtube/v3) |
| YouTube Music |  Live | Official API | REST API | Same as YouTube |
| Bandcamp |  Live | Web Scraping | Selenium + BeautifulSoup | Custom implementation |
| Nina Protocol |  Planned | Official API | REST API | Custom developed |
| SoundCloud |  Planned | Web Scraping | Selenium | API deprecated |

### Integration Architecture

```
User submits URL
       ↓
orchestrate_platform_api()
       ↓
detect_streaming_platform()
       ↓
    ┌──┴──────────────────────┐
    │                         │
    ▼                         ▼
YouTube API          Bandcamp Selenium Scraper
    │                         │
    │                    Launch Chrome
    │                         ↓
    │                 Navigate with anti-detection
    │                         ↓
    │                  Parse HTML (BeautifulSoup)
    │                         ↓
    │                  Extract metadata
    │                         │
    └────────┬────────────────┘
             ↓
    Standardized metadata dict
             ↓
    Store in session
             ↓
    Pre-fill form
```

### Bandcamp Scraping Details

**Technology Stack:**
- **Selenium WebDriver** - Browser automation
- **Chrome (Headless)** - JavaScript rendering
- **BeautifulSoup** - HTML parsing
- **webdriver-manager** - Automatic driver downloads

**Anti-Detection Measures:**
1. Realistic User-Agent strings
2. Disabled automation flags (`webdriver` property)
3. Random delays (1-3 seconds)
4. Scrolling simulation
5. Realistic window sizes (1920x1080)

**Environment Detection:**
```python
selenium_url = os.getenv('SELENIUM_REMOTE_URL')

if selenium_url:
    # Docker: Use remote Selenium Grid
    driver = webdriver.Remote(
        command_executor=selenium_url,
        options=chrome_options
    )
else:
    # Local: Use webdriver-manager
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
```

**Error Handling:**
- Timeout handling (10s page load)
- WebDriver exception catching
- Graceful fallback to manual entry
- Comprehensive logging

See [`music_app_archive/src/integrations/README.md`](music_app_archive/src/integrations/README.md) for detailed integration documentation.

---

## Data Analytics Layer

The data analytics layer extends the Music App into a full modern data stack, enabling analysis of music listening behaviour, playlist trends, and track metadata at scale.

### Architecture

Data flows from the Django/PostgreSQL application through a three-layer Snowflake data warehouse, orchestrated by Airflow and transformed by dbt:

```
Django App (PostgreSQL)
        │
        │ (Airflow extracts & loads)
        ▼
┌───────────────────────────────────────────────┐
│              Snowflake (MUSIC_APP_DB)         │
│                                               │
│  RAW          →   STAGING      →   MARTS      │
│  Raw source       Cleaned &        Business-  │
│  data as-is       standardised     ready      │
│                   models          analytics   │
└───────────────────────────────────────────────┘
        ▲
        │ (dbt transforms)
```

### Snowflake Setup

The warehouse is configured with a dedicated role and cost-efficient compute:

| Resource | Name | Notes |
|---|---|---|
| Database | `MUSIC_APP_DB` | Main analytics database |
| Warehouse | `MUSIC_APP_WH` | X-Small, auto-suspends after 60s |
| Role | `MUSIC_APP_ROLE` | Dedicated least-privilege role |
| Schemas | `RAW`, `STAGING`, `MARTS` | Medallion architecture |

### dbt Project Structure

dbt handles all transformations from RAW through to business-ready mart models:

```
dbt/
├── models/
│   ├── staging/                    # One model per source table
│   │   ├── stg_tracks.sql
│   │   ├── stg_playlists.sql
│   │   ├── stg_streaming_links.sql
│   │   ├── stg_users.sql
│   │   ├── stg_sources.yml               # Raw data postgreSQL data sources
│   │   └── _staging.yml                  # Staging model documentation & tests
│   └── marts/                            # Business-ready analytical models
│       ├── mart_playlist_type.sql         
│       ├── mart_playlist_visibility.sql.  
│       ├── mart_streaming_links.sql      
│       ├── mart_summary_stats.sql        
│       ├── mart_track_purchase_link.sql  
│       ├── mart_track_type.sql           
│       └── mart_schema.yml               # Mart model documentation & tests
├── tests/                          # Custom singular tests
├── macros/                         # Reusable SQL macros
├── seeds/                          # Static reference data (CSV)
├── snapshots/                      # Slowly changing dimension tracking
├── dbt_project.yml                 # Project configuration
└── README.md                       # Detailed README of the dbt folder
```

### Medallion Architecture

**RAW** — Data lands here exactly as it comes from the source. Never modified, acts as the single source of truth.

**STAGING** — dbt cleans and standardises the raw data: renaming columns to snake_case, casting data types, deduplicating records, and applying basic business logic.

**MARTS** — Final analytical models that answer business questions, e.g. how many users, playlists and tracks. As well as breakdowns of playlists and tracks.

### Data Quality

dbt's built-in testing framework is used to ensure data integrity across all models:

```yaml
# Example tests on stg_tracks
- not_null: [track_id, track_name, artist]
- unique: [track_id]
```

### Orchestration (Airflow)

Apache Airflow orchestrates the end-to-end pipeline via a manually triggered DAG. The DAG connects to dbt Cloud via API and polls until each job completes before proceeding.

```
DAG: music_app_pipeline
│
├── extract_from_postgres    # Pull data from Django PostgreSQL DB via XCom
├── load_to_snowflake_raw    # Full refresh load into Snowflake RAW schema
├── trigger_dbt_run          # RAW → STAGING → MARTS transformations
└── trigger_dbt_test         # Data quality validation across all models
```

Each task only runs if the previous one succeeds. The DAG is currently set to manual trigger (`schedule_interval=None`) — it can be switched to a cron schedule without any other changes.

**Required Airflow setup** (Admin → Connections & Variables):

| Type | Key | Purpose |
|---|---|---|
| Connection | `postgres_music_app` | Django PostgreSQL database |
| Connection | `snowflake_music_app` | Snowflake data warehouse |
| Connection | `dbt_cloud` | dbt Cloud API token (stored in `password` field) |
| Variable | `DBT_ACCOUNT_ID` | dbt Cloud account ID |
| Variable | `DBT_JOB_ID` | dbt Cloud job to trigger |

See [`airflow/dags/README.md`](airflow/dags/README.md) for full setup instructions.

### Development Environment

dbt Cloud is connected to:
- **Snowflake** via the `MUSIC_APP_ROLE` and `MUSIC_APP_WH`
- **GitHub** repo (`/dbt` subdirectory) for version-controlled models
- **Development schema** `dbt_tstephens` for personal sandbox development

---

## Development Roadmap

### Phase 1: Core Features ✅
- [x] User authentication with email verification
- [x] Basic playlist CRUD
- [x] YouTube integration
- [x] Bandcamp integration (upgraded to Selenium)
- [x] Manual track entry
- [x] Query optimization
- [x] TypeScript frontend validation
- [x] Docker development environment
- [x] Selenium Grid integration
- [x] Anti-detection web scraping

### Phase 2: Data Analytics Layer ✅
- [x] Snowflake account setup (database, schemas, warehouse, role)
- [x] dbt Cloud connected to Snowflake and GitHub
- [x] dbt project initialised with medallion architecture (RAW / STAGING / MARTS)
- [x] Build staging models (stg_tracks, stg_playlists, stg_streaming_links)
- [x] Build mart models
- [x] Add dbt data quality tests (not_null, unique, accepted_values)
- [x] Load seed data into Snowflake RAW and execture dbt run and dbt test
- [x] Load source data from Django PostgreSQL into Snowflake RAW
- [x] Add dbt model documentation
- [x] Set up Apache Airflow for pipeline orchestration
- [x] Build Airflow DAG to extract → load → transform on a schedule

### Phase 3: Enhanced Features (In Progress) 🔄
- [x] Update Python version
- [x] Fix Bandcamp API
- [x] Update password security with Argon 2
- [x] Track deletion from playlists
- [x] Track deletion from playlists
- [ ] Improve YouTube API
- [ ] Refactor deletePlaylists/deletePlaylistTrack ts modules into one
- [ ] If song link exists, pull metadata from table
- [ ] SoundCloud API integration
- [ ] Implement TypeScript to show relevent fields for Soundcloud mix
- [ ] Track reordering (drag-and-drop)
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
- Handle Selenium exceptions properly

**Frontend (TypeScript):**
- Use TypeScript strict mode
- Explicit return types on functions
- Write tests with Vitest
- Follow existing patterns
- Update relevant READMEs

### Selenium/Scraping Guidelines
- Always add random delays
- Use realistic User-Agent strings
- Implement proper error handling
- Test both Docker and local environments
- Document anti-detection measures
- Respect rate limits

### Pull Request Checklist
- [ ] Backend tests pass (`python manage.py test`)
- [ ] Frontend tests pass (`npm test`)
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Code follows project style
- [ ] Commit messages are clear
- [ ] Selenium tests work in Docker

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
- [ ] Secure Selenium Grid endpoint

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
- [ ] Optimize Selenium Grid configuration
- [ ] Set appropriate session limits

**Selenium Configuration:**
- [ ] Limit concurrent sessions (`SE_NODE_MAX_SESSIONS`)
- [ ] Set session timeouts
- [ ] Configure appropriate `shm_size`
- [ ] Monitor resource usage
- [ ] Implement request queuing if needed

**Monitoring:**
- [ ] Set up error tracking (Sentry)
- [ ] Configure logging to files
- [ ] Set up uptime monitoring
- [ ] Configure performance monitoring
- [ ] Monitor Selenium Grid health

### Recommended Hosting
- **PaaS:** Heroku, Railway, Render, PythonAnywhere
- **VPS:** DigitalOcean, Linode, AWS EC2
- **Containerized:** Docker + Kubernetes, AWS ECS, Google Cloud Run

**Note:** Ensure hosting supports Docker Compose or provides Selenium Grid services.

---

## Troubleshooting

### Common Issues

**Problem:** `ModuleNotFoundError: No module named 'X'`  
**Solution:** Install dependencies: `conda env create -f environment.yml` or `pip install -r requirements.txt`

**Problem:** `django.db.utils.OperationalError: no such table`  
**Solution:** Run migrations: `python manage.py migrate`

**Problem:** YouTube API quota exceeded  
**Solution:** Wait for quota reset (midnight PT) or request increase

**Problem:** Email verification not working  
**Solution:** Check `EMAIL_HOST_*` settings in `.env`

**Problem:** Static files not loading  
**Solution:** Run `python manage.py collectstatic`

**Problem:** Selenium connection refused  
**Solution (Docker):** Ensure Selenium service is running: `docker-compose ps`  
**Solution (Local):** Check Chrome installation: `google-chrome --version`

**Problem:** `TimeoutException` when scraping Bandcamp  
**Solution:** 
- Check internet connection
- Verify Bandcamp URL is valid
- Increase timeout in `bandcamp.py`
- Check if Bandcamp has blocked the IP

**Problem:** Chrome crashes in Docker  
**Solution:** Increase `shm_size` in `docker-compose.yml` (currently 725mb)

**Problem:** Can't connect to VNC for debugging  
**Solution:** Ensure port 7900 is exposed and use password `secret`

**Problem:** webdriver-manager fails to download ChromeDriver  
**Solution:** Check internet connection or manually download from [ChromeDriver downloads](https://chromedriver.chromium.org/downloads)

---

## Documentation

- **Project Overview:** This file
- **Authentication Module:** [`music_app_auth/README.md`](music_app_auth/README.md)
- **Archive Module:** [`music_app_archive/README.md`](music_app_archive/README.md)
- **Frontend Workspace:** [`music_app_frontend/README.md`](music_app_frontend/README.md)
- **Services Layer:** [`music_app_archive/src/README.md`](music_app_archive/src/README.md)
- **API Integrations:** [`music_app_archive/src/integrations/README.md`](music_app_archive/src/integrations/README.md)
- **Airflow DAG:** [`airflow/dags/README.md`](airflow/dags/README.md)
- **dbt Project:** [`dbt/README.md`](dbt/README.md)

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

- Django Software Foundation
- YouTube Data API
- Bandcamp for their structured HTML
- Selenium WebDriver project
- TypeScript and Vite communities
- Open source community

---

## Contact & Support

- **Issues:** Open an issue on GitHub
- **Discussions:** GitHub Discussions

---

**Last Updated:** February 2026  
**Version:** 1.1.0 (Enhanced with Selenium Integration)  
**Maintained By:** Tim Stephens

---

## Quick Links

- [Django Documentation](https://docs.djangoproject.com/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Vite Documentation](https://vitejs.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager)
