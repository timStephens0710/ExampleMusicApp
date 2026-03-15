# Music App Archive

`music_app_archive` is the archive / playlist management module for the Music App.  
It lets authenticated users create playlists, add tracks (via streaming links or manual entry), manage streaming links, and view/edit playlists. The app integrates with platform APIs (e.g., YouTube, Bandcamp) to fetch metadata, logs user activity, and uses transactional saves to keep playlist/track/link data consistent.

---

## Table of Contents

- [Features](#features)  
- [High-Level Flow](#high-level-flow)  
- [Key Views (Summary)](#key-views-summary)  
- [Important Models & Forms (Overview)](#important-models--forms-overview)  
- [Integrations & External APIs](#integrations--external-apis)  
- [Error Handling & Logging](#error-handling--logging)  
- [Project Structure](#project-structure)  
- [Templates](#templates)  
- [Requirements](#requirements)  
- [Environment Variables](#environment-variables)  
- [How to Run (Dev)](#how-to-run-dev)  
- [Testing](#testing)  
- [TODO / Improvements](#todo--improvements)
- [Performance Optimization](#performance-optimization)
- [Security Considerations](#security-considerations)


---

## Features

- Authenticated user profile and playlist listing  
- Create playlists with unique names per user (duplicate names handled gracefully)  
- Add streaming links — attempts to fetch metadata from platform APIs  
- Add track + streaming link together in a single transactional operation (atomic)  
- View & edit playlists, displaying track metadata and links  
- **Soft-delete playlists** - Mark playlists as deleted without removing data
- **Soft-delete tracks from playlists** - Remove tracks while preserving data integrity
- Robust handling of platform API failures with fallbacks to manual entry  
- Per-user activity logging through `AppLogging`  
- Form validation and user-friendly messages via Django `messages`  
- Optimized database queries (no N+1 problems)

---

## High-Level Flow

1. **User Profile** - User (authenticated) opens their profile and views playlists  
2. **Create Playlist** - User creates a playlist (must be their own account)  
3. **Add Streaming Link** - User adds a streaming link to the playlist
   - Server calls `orchestrate_platform_api` to fetch metadata
   - If metadata fetch succeeds → metadata stored in session, redirect to step 4
   - If platform errors occur → user warned, can manually fill track form
4. **Add Track Details** - User fills track form (prefilled where metadata exists) and streaming link form
   - Both saved in a single DB transaction (`transaction.atomic()`)
5. **View Playlist** - Playlist track listing shows each track, streaming links, and metadata
6. **Delete Content** - User can delete playlists or remove tracks (soft deletion preserves data)

---

## Key Views (Summary)

> All views require authentication (`@login_required`)

### User & Playlist Management

**`user_profile(request, username)`**  
Render user profile page.

**`user_playlists(request, username)`**  
List all playlists owned by the user.

**`create_playlist(request, username)`**  
Create a new playlist with validation:
- Logged-in user must match `username`
- Unique playlist name per user (handles `IntegrityError`)
- Security check prevents creating playlists for other users

**`delete_playlists(request, username)`** 
Soft-delete one or more playlists owned by the user.

**Method:** `DELETE`  
**URL:** `/<username>/delete_playlists/`

**Request Body:**
```json
{
  "playlist_id": [1, 2, 3]
}
```

**Response (Success):**
```json
{
  "success": true,
  "deleted_count": 3
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "empty playlist_ids_to_be_deleted"
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad request (empty playlist_ids or unexpected error)
- `403` - Forbidden (user doesn't own playlists)
- `404` - User not found

**Security:**
- Validates user owns the playlists
- Only soft-deletes (sets `is_deleted=True`)
- Returns `403 Forbidden` for unauthorized attempts
- Logs all deletion attempts

**Example Usage:**
```javascript
fetch('/johndoe/delete_playlists/', {
  method: 'DELETE',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({
    playlist_id: [5, 12, 23]
  })
})
.then(response => response.json())
.then(data => console.log(data.deleted_count + ' playlists deleted'));
```

### Adding Tracks to Playlists

**`add_streaming_link_to_playlist(request, username, playlist_name)`**  
Submit a streaming link for a playlist:
- Calls `orchestrate_platform_api` to fetch metadata
- Stores `meta_data_dict` in session
- Redirects to `add_track_to_playlist`
- Handles platform-specific errors gracefully

**`add_track_to_playlist(request, username, playlist_name)`**  
Add track with metadata to playlist:
- Uses `meta_data_dict` from session to prefill forms
- Saves three models in single transaction:
  - `Track` (with `created_by`)
  - `StreamingLink` (linked to Track, with `added_by`)
  - `PlaylistTrack` (links Track to Playlist with auto-incremented `position`)
- Handles `IntegrityError` (duplicate tracks/links)
- All saves wrapped in `transaction.atomic()` for consistency

**`delete_playlist_tracks(request, username, playlist_name)`** 
Soft-delete one or more tracks from a specific playlist.

**Method:** `DELETE`  
**URL:** `/<username>/<playlist_name>/delete_tracks/`

**Request Body:**
```json
{
  "playlist_track_id": ["uuid-1", "uuid-2", "uuid-3"]
}
```

**Response (Success):**
```json
{
  "success": true,
  "deleted_count": 3
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "empty playlist_track_ids_to_be_deleted"
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad request (empty IDs or unexpected error)
- `403` - Forbidden (user doesn't own playlist)
- `404` - User not found

**Security:**
- Validates user owns the playlist via `playlist__owner`
- Only soft-deletes (sets `is_deleted=True`)
- Returns `403 Forbidden` for unauthorized attempts
- Logs all deletion attempts with playlist and track details

**Example Usage:**
```javascript
fetch('/johndoe/summer-vibes/delete_tracks/', {
  method: 'DELETE',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({
    playlist_track_id: [
      'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
      'b2c3d4e5-f6a7-8901-bcde-f12345678901'
    ]
  })
})
.then(response => response.json())
.then(data => console.log(data.deleted_count + ' tracks removed'));
```

### Viewing & Editing

**`view_edit_playlist(request, username, playlist_name)`**  
Display playlist contents with optimized queries:
- Uses `select_related()` and `prefetch_related()` to avoid N+1 queries
- Builds `list_of_tracks` with complete metadata
- Only 3 database queries regardless of playlist size

---

## Important Models & Forms (Overview)

### Models

**`CustomUser`** (from `music_app_auth`)  
User model with email authentication and verification.

**`Playlist`**  
```python
Fields:
- playlist_name (CharField)
- slug (SlugField, auto-generated)
- owner (FK to CustomUser)
- playlist_type (CharField: 'tracks', 'liked', 'mixes', 'samples')
- description (CharField)
- date_created, date_updated (DateTimeField)
- is_private (CharField: 'public', 'private')
- is_deleted (BooleanField)  # Soft deletion flag

Constraints:
- Unique: (owner, playlist_name)
- Unique: (owner, slug)
```

**`Track`**  
```python
Fields:
- track_type (CharField: 'track', 'mix', 'sample')
- track_name, artist, album_name (CharField)
- mix_page, record_label, genre (CharField)
- purchase_link (URLField)
- created_by (FK to CustomUser)
- date_added (DateTimeField)
```

**`StreamingLink`**  
```python
Fields:
- track (FK to Track)
- streaming_platform (CharField: 'youtube', 'bandcamp')
- streaming_link (URLField, unique)
- added_by (FK to CustomUser)
- created_at (DateTimeField)

Constraints:
- Unique: streaming_link
- Unique: (track, streaming_platform)
```

**`PlaylistTrack`** (Junction Table)  
```python
Fields:
- id (UUIDField, primary key)
- playlist (FK to Playlist)
- track (FK to Track)
- added_by (FK to CustomUser)
- position (PositiveIntegerField, auto-incremented)
- is_deleted (BooleanField)  # Soft deletion flag
- added_at (DateTimeField)

Constraints:
- Unique: (playlist, track)
- Unique: (playlist, position)
```

**`AppLogging`** (from `music_app_auth`)  
Logs user actions for auditing.

---

### Forms

**`CreatePlaylist`**  
Fields: `playlist_name`, `playlist_type`, `description`, `is_private`  
Filters out 'liked' type from user-facing options.

**`AddStreamingLink`**  
Fields: `track_type`, `streaming_link`  
Validates URL belongs to supported platform.

**`AddTrackToPlaylist`**  
Fields: `track_type`, `track_name`, `artist`, `album_name`, `mix_page`, `record_label`, `genre`, `purchase_link`

**`AddStreamingLinkToTrack`**  
Fields: `streaming_platform`, `streaming_link`  
Validates URL matches selected platform.

---

## Integrations & External APIs

### Overview

The `src/integrations/` module handles fetching track metadata from streaming platforms.

### Main Function

**`orchestrate_platform_api(streaming_link, track_type)`**

Central integration function that:
1. Detects platform (YouTube, Bandcamp, etc.) from URL
2. Calls platform-specific connector
3. Returns standardized `meta_data_dict` for form pre-filling

**Returns:**
```python
{
    'track_type': 'track',
    'track_name': 'Song Name',
    'artist': 'Artist Name',
    'album_name': 'Album Name',
    'streaming_platform': 'youtube',
    'streaming_link': 'https://...',
    # ... other fields
}
```

**Raises:**
- `YouTubeMetaDataError` - YouTube API failures
- `BandCampMetaDataError` - Bandcamp scraping failures
- `ValueError` - Invalid/unsupported URLs

---

### Supported Platforms

| Platform | Status | Method | API Key Required |
|----------|--------|--------|-----------------|
| YouTube | Implemented | Official API | Yes |
| YouTube Music | Implemented | Official API | Yes |
| Bandcamp | Implemented | HTML scraping | No |

---

### Platform Details

**YouTube Integration** (`src/integrations/youtube.py`)
- Uses YouTube Data API v3
- Requires API key in `YOUTUBE_API_KEY` setting
- Free tier: 10,000 quota units/day
- Extracts: track name, artist (from channel), description
- Limitations: No album info, genre limited

**Bandcamp Integration** (`src/integrations/bandcamp.py`)
- Web scraping using BeautifulSoup
- Extracts JSON-LD structured data
- No API key required
- Extracts: track name, artist, album, purchase link
- Fragile: Breaks if Bandcamp changes page structure

See [`src/integrations/README.md`](src/integrations/README.md) for detailed integration documentation.

---

## Error Handling & Logging

### Error Handling Strategy

**View Layer:**
- Uses Django `messages` for user-facing feedback
- Catches platform-specific exceptions gracefully
- Provides fallback to manual entry on API failures
- Security checks prevent unauthorized actions
- JSON error responses for API endpoints

**Service Layer:**
- Uses `get_object_or_404()` for automatic 404 handling
- Validates inputs with custom validators
- Returns `None` for graceful degradation

**Integration Layer:**
- Raises custom exceptions (`YouTubeMetaDataError`, `BandCampMetaDataError`)
- Comprehensive logging of all operations
- Handles rate limits and network errors

---

### Logging

All views use Python's `logging` module:

```python
import logging
logger = logging.getLogger(__name__)

# Example usage
logger.info("User created playlist")
logger.warning("API quota exceeded")
logger.error("Failed to save track")
logger.exception("Unexpected error")  # Includes stack trace
```

**User Actions Logged:**
- Playlist creation
- Playlist deletion (with IDs and username)
- Track additions
- Track deletion from playlists (with IDs and playlist name)
- Streaming link submissions
- API failures
- Database errors

**Deletion Logging Examples:**
```python
logger.info(f"The following playlists by {username} have been deleted: {playlist_ids}")
logger.info(f"The following tracks from {playlist_name} by {username} have been deleted: {track_ids}")
logger.exception(f"Unexpected error deleting playlist(s): {playlist_ids}: {error}")
```

**AppLogging Model:**
```python
AppLogging.objects.create(
    user_id=user.id,
    log_text="User added track 'Song Name' to playlist 'My Playlist'"
)
```

---

### Transaction Safety

Database operations use `transaction.atomic()`:

```python
with transaction.atomic():
    new_track.save()              # Rolled back if any step fails
    new_streaming_link.save()     # Rolled back if any step fails
    PlaylistTrack.objects.create(...) # Rolled back if any step fails
```

**Benefits:**
- All-or-nothing saves (no partial data)
- Prevents orphaned records
- Database consistency guaranteed

**Soft Deletion Strategy:**
- Playlists and tracks marked as deleted (`is_deleted=True`)
- Data preserved for auditing and recovery
- Can be filtered out in queries with `.filter(is_deleted=False)`
- No cascade deletion prevents accidental data loss

---

## Project Structure

```
music_app_archive/
├── migrations/              # Database migrations
│   └── ...
│
├── src/                    # Business logic and integrations
│   ├── __init__.py
│   ├── services.py        # Business logic (get_playlist, get_playlist_tracks)
│   ├── utils.py           # Generic utilities (validation, URL parsing)
│   │
│   └── integrations/      # External platform API integrations
│       ├── __init__.py
│       ├── main_integrations.py  # Orchestrator (routes URLs to platforms)
│       ├── youtube.py            # YouTube Data API v3 integration
│       ├── bandcamp.py           # Bandcamp web scraping
│       └── README.md             # Integration documentation
│
├── templates/              # HTML templates
│   ├── user_profile.html
│   ├── user_playlists.html
│   ├── create_playlist.html
│   ├── add_link.html
│   ├── add_track.html
│   ├── view_edit_playlist.html
│   └── ...
│
├── static/                 # CSS, JavaScript, images
│   └── ...
│
├── tests/                  # Test suite
│   ├── test_integrations.py
│   ├── test_models.py
│   ├── test_views.py
│   └── test_services.py
│
├── models.py              # Database models
├── forms.py               # Django forms
├── views.py               # View controllers
├── urls.py                # URL routing
├── admin.py               # Django admin configuration
├── apps.py                # App configuration
└── README.md              # This file
```

---

## Templates

Templates referenced in the views:

### User & Playlist Views
- **`user_profile.html`** - User profile page
- **`user_playlists.html`** - List of user's playlists

### Playlist Management
- **`create_playlist.html`** - Playlist creation form
- **`add_link.html`** - Streaming link submission form
- **`add_track.html`** - Track metadata and streaming link forms
- **`view_edit_playlist.html`** - Playlist viewer/editor

### Template Requirements

**All templates should:**
- Display Django `messages` for user feedback
- Include CSRF tokens in forms
- Render form errors properly
- Use responsive design (mobile-friendly)

**`view_edit_playlist.html` context:**
```python
{
    'playlist': Playlist instance,
    'username': 'username',
    'playlist_name': 'playlist_name',
    'list_of_tracks': [
        {
            'position': 1,
            'track_name': 'Song',
            'artist': 'Artist',
            'streaming_links': [...],
            # ... more fields
        },
        # ... more tracks
    ]
}
```

---

## Requirements

### Core Dependencies

```bash
# External API integrations
google-api-python-client>=2.70.0  # YouTube Data API
requests==2.32.3                  # HTTP requests
beautifulsoup4==4.14.2            # Web scraping (Bandcamp)

```

### Install Dependencies

```bash
# Or using conda
conda env create -f environment.yml
conda activate music_app
```

---

### Getting API Keys

**YouTube Data API v3:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project
3. Enable YouTube Data API v3
4. Create credentials → API Key
5. Add key to `YOUTUBE_API_KEY` setting

---

## Environment Variables

Required environment variables:

```bash
# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key_here

# Django Settings
SECRET_KEY=your_secret_key_here
DEBUG=True  # Set to False in production
```

---

## How to Run (Dev)

### 1. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Create Superuser
```bash
python manage.py createsuperuser
```

### 3. Run Development Server
```bash
python manage.py runserver
```

App available at: **http://127.0.0.1:8000/**

### 4. Access Admin Panel
Navigate to: **http://127.0.0.1:8000/admin/**

---

## Testing

### Run Tests

```bash
# Run all tests
python manage.py test music_app_archive

# Run specific test file
python manage.py test music_app_archive.tests.test_views

# Run specific test class
python manage.py test music_app_archive.tests.test_views.CreatePlaylistTest

# Run with verbose output
python manage.py test music_app_archive -v 2

# Run with coverage
coverage run --source='.' manage.py test music_app_archive
coverage report
coverage html  # Generate HTML report
```

### Test Structure

```python
tests/
├── test_models.py        # Model tests (Playlist, Track, etc.)
├── test_views.py         # View tests (create_playlist, add_track, delete, etc.)
├── test_forms.py         # Form validation tests
├── test_services.py      # Service layer tests
├── test_integrations.py  # API integration tests
└── test_utils.py         # Utility function tests
```
---

## TODO / Improvements

### High Priority
- **Continue To Implement TypeScript** - dramatically improve the front-end
- **SoundCloud integration** - Add SoundCloud API support
- **Fix get_playlist_tracks bug** - currently doesn't work as intended when called in the view
- **Track reordering** - Drag-and-drop to update position
- **Duplicate prevention** - Pre-check before DB save

### Medium Priority
- **Pagination** - For playlists with 100+ tracks
- **Search functionality** - Search within playlists
- **Playlist sharing** - Share playlists with other users
- **Bulk operations UI** - Select multiple items for deletion

### Low Priority / Future
- **Background tasks** - Move API calls to Celery for async processing
- **Playlist export** - Export to JSON/CSV/M3U
- **Collaborative playlists** - Multiple users editing same playlist

---

## Performance Optimization

### Current Optimizations
- `select_related()` for ForeignKey relationships
- `prefetch_related()` for reverse ForeignKey relationships
- Only 3 queries for playlist view (any size)
- Session-based metadata storage (reduces API calls)
- Soft deletion (faster than hard deletion)
- Bulk updates for deletion (`update()` instead of `save()`)

### Recommended for Production
- Redis caching for API responses
- CDN for static files
- Database query caching
- Async task queue (Celery)
- Rate limiting on API endpoints
- Database indexing on `is_deleted` fields

---

## Security Considerations

### Authentication & Authorization
- Authentication required for all views (`@login_required`)
- User can only modify their own playlists (ownership checks)
- Ownership verified via `playlist__owner` for nested operations
- Returns `403 Forbidden` for unauthorized attempts

### Data Protection
- CSRF protection on all forms
- Database transactions prevent partial saves
- Input validation on all forms
- URL validation prevents malicious links
- API keys stored in environment variables (not in code)
- Soft deletion preserves audit trail

### API Security
- JSON validation on DELETE endpoints
- Empty array validation prevents no-op requests
- Comprehensive error logging without exposing internals
- Generic error messages to users (detailed logs for admins)

### Password Security
- Passwords secured using **Argon2**, the winner of the Password Hashing Competition
- Argon2 is specifically designed to resist brute-force attacks, GPU cracking, and ASIC attacks by being intentionally slow and memory-intensive
- Makes it computationally infeasible for attackers to crack passwords even if the database is compromised

---