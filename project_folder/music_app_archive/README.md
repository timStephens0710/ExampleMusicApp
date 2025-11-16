# Music App Archive

`music_app_archive` is the archive / playlist management module for the Music App.  
It lets authenticated users create playlists, add tracks (via streaming links or manual entry), manage streaming links, and view/edit playlists. The app integrates with platform APIs (e.g., YouTube, Bandcamp) to fetch metadata, logs user activity, and uses transactional saves to keep playlist/track/link data consistent.

---

## Table of contents

- [Features](#features)  
- [High-level flow](#high-level-flow)  
- [Key views (summary)](#key-views-summary)  
- [Important models & forms (overview)](#important-models--forms-overview)  
- [Integrations & external APIs](#integrations--external-apis)  
- [Error handling & logging](#error-handling--logging)  
- [Project structure](#project-structure)  
- [Templates](#templates)  
- [Requirements](#requirements)  
- [Environment variables](#environment-variables)  
- [How to run (dev)](#how-to-run-dev)  
- [Testing & notes](#testing--notes)  
- [TODO / improvements](#todo--improvements)

---

## Features

- Authenticated user profile and playlist listing.  
- Create playlists with unique names per user (duplicate names handled gracefully).  
- Add streaming links — attempts to fetch metadata from platform APIs.  
- Add track + streaming link together in a single transactional operation (atomic).  
- View & edit playlists, displaying track metadata and links.  
- Robust handling of platform API failures with fallbacks to manual entry.  
- Per-user activity logging through `AppLogging`.  
- Form validation and user-friendly messages via Django `messages`.

---

## High-level flow

1. User (authenticated) opens their profile and views playlists.  
2. User creates a playlist (must be their own account).  
3. User adds a streaming link to the playlist — server calls `orchestrate_platform_api` to fetch metadata.  
   - If metadata fetch succeeds → metadata stored in the session and user is redirected to `add_track_to_playlist`.  
   - If platform errors occur (e.g., `YouTubeMetaDataError`, `BandCampMetaDataError`) → user is warned and can manually fill the track form; minimal metadata saved in session.  
4. User fills the track form (prefilled where metadata exists) and a streaming link form; both are saved inside a single DB transaction.  
5. Playlist track listing shows each track, its streaming links and metadata.

---

## Key views (summary)

> All views require authentication (use `@login_required`)

- `user_profile(request, username)`  
  Render user profile.

- `user_playlists(request, username)`  
  List playlists owned by the user.

- `create_playlist(request, username)`  
  Create a playlist. Enforces:
  - logged-in user must match `username`
  - unique playlist name per user (handles `IntegrityError`)

- `add_streaming_link_to_playlist(request, username, playlist_name)`  
  Submit a streaming link for a playlist; orchestration fetches metadata from platform API via `orchestrate_platform_api`. Stores `meta_data_dict` in session and redirects to `add_track_to_playlist`.

- `add_track_to_playlist(request, username, playlist_name)`  
  Use `meta_data_dict` from session to prefill forms `AddTrackToPlaylist` and `AddStreamingLinkToTrack`. Saves:
  - `Track` (with `created_by`)
  - `StreamingLink` (linked to `Track`, with `added_by`)
  - `PlaylistTrack` (linking `Track` to playlist with `added_by`)
  All saved inside `transaction.atomic()` to ensure consistency. Handles `IntegrityError` (duplicates) and other DB issues gracefully.

- `view_edit_playlist(request, username, playlist_name)`  
  Display playlist contents and metadata. Uses `select_related` and `prefetch_related` to avoid N+1 queries and builds a `list_of_tracks` for the template.

---

## Important models & forms (overview)

**Models**

- `CustomUser` (from `music_app_auth`) — owner/created_by checks.  
- `Playlist` — fields: `playlist_name`, `owner` (FK), `is_deleted`, `date_created`. Unique constraint expected on `(owner, playlist_name)`.  
- `Track` — fields: `track_name`, `artist`, `album_name`, `mix_page`, `record_label`, `genre`, `purchase_link`, `created_by`.  
- `StreamingLink` — fields: `streaming_platform`, `streaming_link`, `track` (FK), `added_by`. Unique constraint on streaming link likely enforced.  
- `PlaylistTrack` — fields: `playlist` (FK), `track` (FK), `added_by`, `position`, `added_at`.  
- `AppLogging` (from `music_app_auth`) — logs user actions.

**Forms**

- `CreatePlaylist` — playlist creation form.  
- `AddStreamingLink` — takes `track_type`, `streaming_link`.  
- `AddTrackToPlaylist` — track metadata form.  
- `AddStreamingLinkToTrack` — streaming link form to attach to a track.

---

## Integrations & external APIs

- `orchestrate_platform_api(streaming_link, track_type)` — central integration function that:
  - Detects platform (YouTube, Bandcamp, etc.) from the URL, calls platform-specific connectors, and returns a `meta_data_dict` used to pre-fill forms.  
  - May raise `YouTubeMetaDataError`, `BandCampMetaDataError` for platform-specific failures, or `ValueError` for invalid/unsupported URLs.

**Notes**

- Provide API keys/credentials for services (YouTube Data API, any other service) via environment variables (see [Environment variables](#environment-variables)).  
- Integrations should handle rate limits & unexpected failures gracefully — views already implement fallback to manual entry.

---

## Error handling & logging

- Views use `logger` to log warnings/errors (`logger.warning`, `logger.exception`, `logger.info`).  
- User-facing messages use Django `messages` to display helpful messages in the UI.  
- Integrations raise domain-specific exceptions (e.g., `YouTubeMetaDataError`) which are caught and handled by the view with a descriptive message and fallback behavior.  
- Database operations that change multiple models run inside `transaction.atomic()` to guarantee atomicity; `IntegrityError` is caught to report duplicates.

---

## Project structure

music_app_archive/
├─ admin.py 
├─ apps.py
├─ models.py # Playlist, Track, StreamingLink, PlaylistTrack
├─ forms.py # CreatePlaylist, AddStreamingLink, AddTrackToPlaylist, AddStreamingLinkToTrack
├─ views.py # The views provided
├─ urls.py # URL patterns for the views
├─ templates/ #HTML templates
├─ migrations/
├─ src/
│ ├─ integrations/
│ │ └─ main_integrations.py
│ │ └─ bandcamp.py
│ │ └─ youtube.py
│ └─ custom_exceptions.py
│ └─ services.py
│ └─ utils.py
├─ static/
├─ tests/
│ ├─ test_integrations.py
│ ├─ test_models.py
│ ├─ test_views.py


---

## Templates

Templates referenced in the views:

- `user_profile.html`  
- `user_playlists.html`  
- `create_playlist.html`  
- `add_link.html` (form for streaming link)  
- `add_track.html` (form for track + streaming link)  
- `view_edit_playlist.html` (playlist editor/viewer)

Templates should display `messages` and iterate over `list_of_tracks` (see `view_edit_playlist` context structure). Ensure CSRF tokens and proper form error rendering.

---

## Requirements
- Additional libs for integrations (e.g., `google-api-python-client` for YouTube) — pin to `requirements.txt`

Install dependencies:
- Refer to environment.yml

---

## Testing

Run the test suite:

```bash
# Run all tests
python manage.py test music_app_archive

# Run specific test file
python manage.py test music_app_archive.tests.test_views

# Run with coverage
coverage run --source='.' manage.py test music_app_archive
coverage report
```

---


## TODO / improvements
* UI for removing tracks from playlists and reordering (update position).

* Make the bandcamp.py more robust. As the code breaks if Bandcamp changes page structure

* Pre-check to prevent duplicate tracks in the same playlist before DB save.

* Add soundcloud API

* Add pagination for long playlists.

* Move heavy integration work to background tasks (Celery) if synchronous fetches become slow.