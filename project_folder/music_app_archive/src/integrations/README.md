# Music Platform Integrations

This folder contains all external music platform API integrations for automatically extracting track metadata from streaming URLs.

## Overview

When a user submits a streaming link (YouTube, Bandcamp, etc.), these integrations fetch track information (title, artist, album, etc.) to pre-fill the add track form.

## Architecture

```
src/integrations/
├── __init__.py              # Exports public API
├── main_integrations.py     # Orchestrator - routes URLs to correct platform
├── youtube.py              # YouTube Data API v3 integration
├── bandcamp.py             # Bandcamp web scraping (JSON-LD)
└── README.md               # This file
```

## File Descriptions

### `main_integrations.py`
**Main orchestration layer** that routes streaming URLs to the appropriate platform handler.

**Key Function:**
- `orchestrate_platform_api(streaming_url, track_type)` - Main entry point

**What it does:**
1. Detects which platform the URL belongs to
2. Routes to the appropriate integration (YouTube, Bandcamp, etc.)
3. Returns standardized metadata dictionary
4. Handles unsupported platforms gracefully

**Usage:**
```python
from .src.integrations import orchestrate_platform_api

metadata = orchestrate_platform_api(
    streaming_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    track_type="track"
)
# Returns: {
#   'track_name': '...',
#   'artist': '...',
#   'streaming_platform': 'youtube',
#   ...
# }
```

---

### `youtube.py`
**YouTube Data API v3 integration** for fetching metadata from YouTube and YouTube Music videos.

**Key Functions:**
- `extract_youtube_video_id_from_url(youtube_url)` - Extracts video ID from various URL formats
- `get_youtube_metadata(video_id)` - Calls YouTube API for metadata
- `get_youtube_platform(youtube_url)` - Determines if URL is YouTube or YouTube Music
- `orchestrate_get_youtube_meta_data_dict(youtube_url, track_type)` - Complete workflow

**Requirements:**
- YouTube Data API v3 key (stored in `settings.YOUTUBE_API_KEY`)
- Google API Python client: `pip install google-api-python-client`

**Supported URL Formats:**
```
https://www.youtube.com/watch?v=VIDEO_ID
https://youtu.be/VIDEO_ID
https://music.youtube.com/watch?v=VIDEO_ID
https://m.youtube.com/watch?v=VIDEO_ID
```

**Metadata Extracted:**
- Track name (from video title)
- Artist (parsed from channel name)
- Description
- Album name (not available - empty)
- Genre (not available - empty)

**API Quota:**
- Free tier: 10,000 units/day
- Cost per video lookup: ~1-3 units
- Effectively: ~3,000-10,000 requests/day

**Error Handling:**
- `YouTubeMetaDataError` - Custom exception for YouTube-specific errors
- Handles: API quota exceeded, video not found, network errors, invalid video IDs

---

### `bandcamp.py`
**Bandcamp web scraping integration** using JSON-LD structured data extraction.

**Key Functions:**
- `extract_jsonld_from_bandcamp(bandcamp_url)` - Scrapes and parses JSON-LD from page
- `generate_bandcamp_meta_data_dictionary(jsonld_data, bandcamp_url)` - Normalizes data
- `orchestrate_bandcamp_meta_data_dictionary(bandcamp_url)` - Complete workflow

**Requirements:**
- BeautifulSoup4: `pip install beautifulsoup4`
- Requests: `pip install requests`

**Supported URL Formats:**
```
https://artistname.bandcamp.com/track/trackname
https://artistname.bandcamp.com/album/albumname
https://labelname.bandcamp.com/track/trackname
```

**Metadata Extracted:**
- Track name
- Artist name
- Album name
- Purchase link

**Technical Approach:**
- Scrapes HTML from Bandcamp pages
- Extracts `<script type="application/ld+json">` tag
- Parses JSON-LD structured data (schema.org format)
- No official API - relies on web scraping

**Error Handling:**
- `BandCampMetaDataError` - Custom exception for Bandcamp-specific errors
- Handles: Page not found, JSON-LD missing, network errors, parsing failures

**Limitations:**
- Fragile - breaks if Bandcamp changes page structure
- No streaming URLs (only metadata)
- Custom domains may not work
- Requires maintenance when site updates

---

## Platform Support Status
Currently supported:
* Bandcamp
* YouTube

Coming soon:
* Soundcloud
* Nina Protocol


---

## Configuration

### Environment Variables Required

```python
# settings.py or .env

# YouTube Data API v3
YOUTUBE_API_KEY = 'your_google_api_key_here'
```

### Getting a YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **YouTube Data API v3**
4. Create credentials → API Key
5. Add key to your environment variables
6. (Optional) Restrict key to YouTube Data API only

**Cost:** Free tier includes 10,000 quota units/day (sufficient for small projects)

---

## Error Handling

### Custom Exceptions

All integrations use custom exceptions for clear error handling:

```python
# Base exception (optional, for catching all platform errors)
class MetadataExtractionError(Exception):
    """Base exception for all metadata extraction errors"""
    pass

# Platform-specific exceptions
class YouTubeMetaDataError(MetadataExtractionError):
    """YouTube API errors"""
    pass

class BandCampMetaDataError(MetadataExtractionError):
    """Bandcamp scraping errors"""
    pass
```

### Error Scenarios Handled

**YouTube:**
- Invalid video ID
- Video not found or private
- API quota exceeded (403)
- Network errors
- Missing API key

**Bandcamp:**
- Invalid URL
- Page not found (404)
- JSON-LD data missing
- Network errors
- Parsing failures

**General:**
- Unsupported platform
- Invalid URL format
- Unexpected errors

---

## Data Format

### Standardized Metadata Dictionary

All integrations return a consistent format:

```python
{
    'track_type': 'track',           # or 'mix', 'sample'
    'track_name': 'Song Name',
    'artist': 'Artist Name',
    'album_name': 'Album Name',      # or '' if not available
    'mix_page': '',                   # Optional
    'record_label': '',               # Optional
    'genre': '',                      # Optional
    'purchase_link': '',              # Optional (Bandcamp provides this)
    'streaming_platform': 'youtube',  # 'youtube', 'youtube_music', 'bandcamp'
    'streaming_link': 'https://...'  # Original URL
}
```

---

## Troubleshooting

### YouTube API Not Working

**Problem:** "YouTube API key not configured"
**Solution:** Ensure `YOUTUBE_API_KEY` is set in settings or environment variables

**Problem:** "Quota exceeded"
**Solution:** Wait for quota reset (midnight PT) or request quota increase

**Problem:** "Video not found"
**Solution:** Video may be private, deleted, or region-restricted

### Bandcamp Scraping Fails

**Problem:** "No JSON-LD script tag found"
**Solution:** 
- Check if URL is valid Bandcamp page
- Bandcamp may have changed page structure (requires code update)
- Try a different Bandcamp URL to confirm

**Problem:** "Network timeout"
**Solution:** Increase timeout or check internet connection

---
