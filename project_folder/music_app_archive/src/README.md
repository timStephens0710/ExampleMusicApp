# Music App Archive - Source Code (`src/`)

This directory contains the business logic, utilities, and external integrations for the Music App Archive Django application. Code here is separated from Django views to promote reusability, testability, and maintainability.

## Philosophy

Following the **"Fat Models, Thin Views, Business Logic in Services"** pattern:

- **Views** (`views.py`) - Handle HTTP requests/responses only
- **Models** (`models.py`) - Database schema and simple model methods
- **Services** (`src/`) - Business logic, complex queries, external integrations

This separation makes code:
- **Reusable** - Functions can be called from views, APIs, management commands
- **Testable** - Business logic isolated from Django request/response cycle
- **Maintainable** - Clear separation of concerns
- **Scalable** - Easy to add new features without bloating views

---

## Directory Structure

```
src/
├── __init__.py              # Package initialization
├── services.py              # Business logic & data operations
├── utils.py                 # Generic utility functions
├── integrations/            # External platform API integrations
│   ├── __init__.py
│   ├── main_integrations.py
│   ├── youtube.py
│   ├── bandcamp.py
│   └── README.md
└── README.md                # This file
```

---

## Module Descriptions

### `services.py`

**Purpose:** Core business logic and complex database operations specific to the music archive domain.

**Key Functions:**

#### `get_playlist(playlist_name, user)`
Retrieves a playlist instance with optimized database query.

**Parameters:**
- `playlist_name` (str): Name of the playlist
- `user` (CustomUser): Owner of the playlist

**Returns:** `Playlist` instance

**Raises:** `Http404` if playlist not found

**Usage:**
```python
from .src.services import get_playlist

playlist = get_playlist('Summer Vibes', request.user)
```

**Query Optimization:**
- Uses `get_object_or_404()` for automatic 404 handling
- Includes `select_related('owner')` to avoid N+1 queries
- Filters by owner to ensure security

---

#### `get_playlist_tracks(playlist)`
Retrieves all tracks in a playlist with complete metadata and streaming links.

**Parameters:**
- `playlist` (Playlist): Playlist instance

**Returns:** List of dictionaries containing track data

**Query Optimization:**
- Uses `select_related('track', 'added_by')` for ForeignKey optimization
- Uses `prefetch_related('track__streaming_links')` for reverse ForeignKey optimization
- Orders by `position` for correct playlist ordering
- **Only 3 database queries** regardless of playlist size (see Performance section below)

**Return Format:**
```python
[
    {
        'position': 1,
        'track_id': 123,
        'track_name': 'Song Name',
        'artist': 'Artist Name',
        'album_name': 'Album Name',
        'genre': 'Electronic',
        'record_label': 'Label Name',
        'mix_page': '',
        'date_added': datetime.datetime(...),
        'added_by': 'username',
        'streaming_links': [
            {
                'platform': 'YouTube',
                'platform_code': 'youtube',
                'url': 'https://youtube.com/...',
                'id': 456
            }
        ],
        'streaming_platform': 'YouTube',  # First link (backward compatibility)
        'link': 'https://youtube.com/...' # First link (backward compatibility)
    },
    # ... more tracks
]
```

**Usage:**
```python
from .src.services import get_playlist, get_playlist_tracks

playlist = get_playlist('My Playlist', request.user)
tracks = get_playlist_tracks(playlist)

context = {
    'playlist': playlist,
    'tracks': tracks,
    'track_count': len(tracks)
}
```

**Performance:**
- **Optimized queries** - No N+1 problems
- **Scales well** - 3 queries for 1 track or 1000 tracks
- **Memory efficient** - Streams data from database

---

### `utils.py`

**Purpose:** Generic utility functions that could be used in any Django project. Platform-agnostic, reusable helpers.

**Key Functions:**

#### `orch_validate_input_string(input_string, name_input_string)`
Validates that an input is a non-empty string.

**Parameters:**
- `input_string` (str): The value to validate
- `name_input_string` (str): Descriptive name for error messages (e.g., "username", "playlist_name")

**Raises:**
- `ValueError` if input is None, empty, or not a string

**Usage:**
```python
from .src.utils import orch_validate_input_string

def my_function(username):
    orch_validate_input_string(username, "username")
    # Proceed knowing username is valid
```

**Why useful:**
- Consistent validation across codebase
- Clear error messages
- Fail-fast principle
- DRY (Don't Repeat Yourself)

---

#### `get_hostname(streaming_url)`
Extracts the hostname from a URL string.

**Parameters:**
- `streaming_url` (str): Full URL

**Returns:** Hostname as string (e.g., `'youtube.com'`) or `None` if extraction fails

**Usage:**
```python
from .src.utils import get_hostname

hostname = get_hostname('https://www.youtube.com/watch?v=abc123')
# Returns: 'www.youtube.com'
```

**Error Handling:**
- Returns `None` on failure (graceful degradation)
- Logs errors for debugging
- Doesn't crash on malformed URLs

---

#### `check_streaming_link_platform(streaming_link)`
Detects which streaming platform a URL belongs to.

**Parameters:**
- `streaming_link` (str): Full streaming URL

**Returns:** Platform name (`'youtube'`, `'bandcamp'`, etc.) or `None` if unsupported

**Supported Platforms:**
```python
PLATFORM_DOMAINS = {
    'youtube': ['youtube.com', 'youtu.be', 'music.youtube.com', 'm.youtube.com'],
    'bandcamp': ['bandcamp.com'],
}
```

Coming soon:
* Soundcloud
* Nina


**Usage:**
```python
from .src.utils import check_streaming_link_platform

platform = check_streaming_link_platform('https://youtube.com/watch?v=123')
# Returns: 'youtube'

platform = check_streaming_link_platform('https://horsevision.bandcamp.com/track/how-are-we')
# Returns: 'bandcamp'

platform = check_streaming_link_platform('https://unknown-site.com')
# Returns: None
```

**Security:**
- Exact domain matching (prevents fake-youtube.com attacks)
- Handles subdomains correctly (music.youtube.com)
- Returns `None` for unsupported platforms

---

### `integrations/`

External music platform API integrations for fetching track metadata.

See [`integrations/README.md`](./integrations/README.md) for detailed documentation.

**Quick Summary:**
- **YouTube** - Official API integration
- **Bandcamp** - HTML scraping adopted Selenium to avoid Bandcamp blocking us
- **Main Orchestrator** - Routes URLs to correct platform

---

## Design Patterns

### Separation of Concerns

```
┌─────────────┐
│   Views     │ ← Handle HTTP requests/responses
└──────┬──────┘
       │ calls
       ↓
┌─────────────┐
│  Services   │ ← Business logic & complex queries
└──────┬──────┘
       │ uses
       ↓
┌─────────────┐
│   Models    │ ← Database schema
└─────────────┘
```

### Example Flow

**Bad (Everything in View):**
```python
# views.py - Too much logic in view
def view_playlist(request, username, playlist_name):
    user = get_object_or_404(CustomUser, username=username)
    playlist = get_object_or_404(Playlist, ...)
    
    # 50+ lines of query logic here
    playlist_tracks = PlaylistTrack.objects.filter(...)...
    
    list_of_tracks = []
    for track in playlist_tracks:
        # Complex data processing
        ...
    
    return render(request, 'playlist.html', {'tracks': list_of_tracks})
```

**Good (Logic in Services):**
```python
# views.py - Thin view
from .src.services import get_playlist, get_playlist_tracks

def view_playlist(request, username, playlist_name):
    user = get_object_or_404(CustomUser, username=username)
    playlist = get_playlist(playlist_name, user)
    tracks = get_playlist_tracks(playlist)
    
    return render(request, 'playlist.html', {'tracks': tracks})

# src/services.py - ✅ Business logic isolated
def get_playlist_tracks(playlist):
    # Complex query and data processing here
    ...
```

**Benefits:**
- Views are readable and maintainable
- Services can be tested independently
- Logic can be reused in APIs, management commands, etc.

---

## Performance Optimization

### Query Optimization Example

**Without Optimization (N+1 Problem):**
```python
# BAD - 201 queries for 100 tracks!
playlist_tracks = PlaylistTrack.objects.filter(playlist=playlist)

for pt in playlist_tracks:  # 1 query
    track = pt.track          # 100 queries (one per track)
    for link in track.streaming_links.all():  # 100 queries (one per track)
        print(link.url)

# Total: 201 database queries
```

**With Optimization (My Approach):**
```python
# GOOD - 3 queries for any number of tracks!
playlist_tracks = PlaylistTrack.objects.filter(
    playlist=playlist
).select_related(
    'track',       # JOIN Track table
    'added_by'     # JOIN User table
).prefetch_related(
    'track__streaming_links'  # Separate query for all links
).order_by('position')

for pt in playlist_tracks:
    track = pt.track                        # No query - already loaded
    for link in track.streaming_links.all():  # No query - already loaded
        print(link.url)

# Total: 3 database queries
```

**Performance Impact:**
| Playlist Size | Without Optimization | With Optimization | Improvement |
|--------------|---------------------|-------------------|-------------|
| 10 tracks    | 21 queries          | 3 queries         | 7x faster   |
| 100 tracks   | 201 queries         | 3 queries         | 67x faster  |
| 1000 tracks  | 2001 queries        | 3 queries         | 667x faster |

---

## Error Handling

### Services Layer

Services use Django's built-in error handling:

```python
from django.shortcuts import get_object_or_404

def get_playlist(playlist_name, user):
    # Raises Http404 automatically if not found
    playlist = get_object_or_404(Playlist, playlist_name=playlist_name, owner=user)
    return playlist
```

### Utils Layer

Utils return `None` for graceful degradation:

```python
def get_hostname(streaming_url):
    try:
        # Try to extract hostname
        return hostname
    except Exception:
        # Return None instead of crashing
        return None
```

**Philosophy:**
- **Services**: Raise exceptions (views handle them)
- **Utils**: Return `None` (caller decides what to do)

---

## Logging

All modules use Python's `logging` module:

```python
import logging
logger = logging.getLogger(__name__)

# In functions:
logger.info("Successfully fetched playlist tracks")
logger.warning("Platform not supported")
logger.error("Failed to extract hostname")
```


## Best Practices

### 1. Keep Services Domain-Specific

**DO:** Put music-archive-specific logic in `services.py`
```python
def get_playlist_tracks(playlist):  # Music domain-specific
    ...
```

**DON'T:** Put generic utilities in `services.py`
```python
def format_date(date):  # Generic utility - belongs in utils.py
    ...
```

### 2. Keep Utils Generic

**DO:** Put reusable utilities in `utils.py`
```python
def validate_input_string(value, name):  # Could be used anywhere
    ...
```

**DON'T:** Put domain logic in `utils.py`
```python
def get_user_playlists(user):  # Domain-specific - belongs in services.py
    ...
```

### 3. Optimize Database Queries

Always use:
- `select_related()` for ForeignKey relationships
- `prefetch_related()` for reverse ForeignKey and ManyToMany
- `only()` or `defer()` if you only need specific fields

### 4. Document Return Formats

Always document what functions return, especially complex data structures:

```python
def get_playlist_tracks(playlist):
    """
    Returns: List of dictionaries containing:
        - position (int): Track position in playlist
        - track_name (str): Name of track
        - artist (str): Artist name
        ...
    """
```

### 5. Write Tests

Every service function should have corresponding tests:
- Happy path (success case)
- Edge cases (empty data)
- Error cases (not found)

---

## File Organization Guidelines

```
src/
├── services.py          # Business logic specific to music archive
│   └── Functions that:
│       - Query multiple models
│       - Process domain data
│       - Coordinate complex operations
│
├── utils.py            # Generic utilities
│   └── Functions that:
│       - Could work in any Django project
│       - Don't know about your models
│       - Are purely functional
│
└── integrations/       # External API integrations
    └── Platform-specific:
        - API clients
        - Data fetching
        - External service coordination
```

---

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'src'`

**Solution:** Import with relative imports:
```python
# In views.py
from .src.services import get_playlist  # Correct

# Not:
from src.services import get_playlist   # Wrong
```

### Circular Import Errors

**Problem:** `ImportError: cannot import name 'X' from partially initialized module`

**Solution:** Move imports inside functions:
```python
def get_playlist_tracks(playlist):
    from ..models import PlaylistTrack  # Import inside function
    ...
```

### Query Performance Issues

**Problem:** Slow page loads with large playlists

**Solution:** Check if using `select_related()` and `prefetch_related()`:
```python
# Use Django Debug Toolbar to see query count
# Should be ~3 queries, not 100+
```

---
