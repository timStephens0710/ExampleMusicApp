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
├── bandcamp.py             # Bandcamp web scraping with Selenium
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
**Bandcamp web scraping integration** using Selenium for dynamic content and HTML parsing.

**Key Functions:**
- `get_soup(bandcamp_url)` - Fetches page with Selenium and returns BeautifulSoup object
- `scrape_bandcamp_page(soup)` - Extracts track, artist, and album from HTML structure
- `orchestrate_bandcamp_meta_data_dictionary(bandcamp_url)` - Complete workflow

**Requirements:**
- Selenium: `pip install selenium`
- BeautifulSoup4: `pip install beautifulsoup4`
- WebDriver Manager: `pip install webdriver-manager` (for local development)
- Chrome/Chromium browser
- **Docker**: Selenium standalone Chrome container (for production/Docker environments)

**Supported URL Formats:**
```
https://artistname.bandcamp.com/track/trackname
https://artistname.bandcamp.com/album/albumname/track/trackname
https://labelname.bandcamp.com/track/trackname
```

**Metadata Extracted:**
- Track name (from `h2.trackTitle`)
- Artist name (from artist link in `#name-section`)
- Album name (from album link in `#name-section`, if available)
- Purchase link (original URL)
- Streaming link (original URL)

**Technical Approach:**
- **Dynamic scraping** with Selenium WebDriver (handles JavaScript-rendered content)
- **Dual environment support**:
  - **Docker**: Uses remote Selenium service (`SELENIUM_REMOTE_URL` environment variable)
  - **Local**: Uses local Chrome with WebDriver Manager
- **Anti-detection measures**:
  - Randomized delays (1-3 seconds)
  - Realistic browser fingerprinting
  - User-agent spoofing
  - JavaScript execution for scrolling
  - Headless Chrome with stealth options
- Parses HTML structure directly from Bandcamp's `#name-section` div
- No official API - relies on web scraping

**Environment Detection:**
```python
# Automatically detects environment based on SELENIUM_REMOTE_URL
if os.getenv('SELENIUM_REMOTE_URL'):
    # Docker environment - uses remote Selenium
    driver = webdriver.Remote(...)
else:
    # Local development - uses local Chrome
    driver = webdriver.Chrome(...)
```

**Scraping Logic:**
The function identifies whether a track is:
1. **Single track** (1 link in h3): Only artist link present
   - Sets artist, leaves album as `None`
2. **Album track** (2+ links in h3): Album link and artist link present
   - Extracts both album and artist
   - Handles album names with " - " separator (e.g., "Album - Deluxe Edition")

**Error Handling:**
- `BandCampMetaDataError` - Custom exception for Bandcamp-specific errors
- Handles:
  - Page not found
  - Missing `#name-section` div
  - Network errors
  - Selenium timeout errors
  - WebDriver errors
  - Parsing failures
- **Resource cleanup**: Always calls `driver.quit()` in finally block

**Limitations:**
- **Slower than API calls**: 3-5 seconds per request due to page load times
- **Fragile**: Breaks if Bandcamp changes page structure
- **No streaming URLs**: Only returns purchase links (Bandcamp doesn't provide streaming)
- **Detection risk**: Anti-bot measures may block requests if too frequent
- **Requires browser**: Selenium needs Chrome/Chromium installed
- Custom domains may not work consistently
- Requires maintenance when site updates

**Performance Considerations:**
- Each scrape takes ~3-5 seconds (page load + delays)
- Resource-intensive (launches browser instance)
- Not suitable for high-volume batch processing
- Consider caching results to minimize repeated scrapes

---

## Platform Support Status
Currently supported:
* Bandcamp (Selenium web scraping)
* YouTube (Official API)

Coming soon:
* SoundCloud
* Nina Protocol

---

## Configuration

### Environment Variables Required
```python
# settings.py or .env

# YouTube Data API v3
YOUTUBE_API_KEY =  "this should be stored in your .env.dev file"

# Selenium (automatically set in Docker Compose)
SELENIUM_REMOTE_URL = 'http://selenium:4444'  # For Docker environment only
```

### Docker Setup for Bandcamp Scraping

The Bandcamp integration requires a Selenium container in Docker:

**docker-compose.yml:**
```yaml
services:
  selenium:
    container_name: selenium_chrome
    image: selenium/standalone-chromium:latest
    restart: always
    shm_size: 512mb
    ports:
      - "4444:4444"
      - "7900:7900"  # VNC for debugging (optional)
    environment:
      - SE_NODE_MAX_SESSIONS=5
      - SE_NODE_SESSION_TIMEOUT=300

  web:
    # ... your Django service
    depends_on:
      - selenium
    environment:
      - SELENIUM_REMOTE_URL=http://selenium:4444
```

**Starting the services:**
```bash
docker compose up -d
```

### Local Development Setup

For local development without Docker:

1. **Install Chrome/Chromium:**
```bash
   # macOS
   brew install --cask google-chrome
   
   # Ubuntu/Debian
   sudo apt-get install chromium-browser
```

2. **Install Python dependencies:**
```bash
   pip install selenium beautifulsoup4 webdriver-manager
```

3. **No SELENIUM_REMOTE_URL needed** - automatically uses local Chrome

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
- Missing `#name-section` element
- Network errors
- Selenium timeout errors
- WebDriver connection failures
- Parsing failures
- Chrome/Chromium not available

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
    'album_name': 'Album Name',      # or None if not available (singles)
    'mix_page': '',                   # Optional
    'record_label': '',               # Optional
    'genre': '',                      # Optional
    'purchase_link': 'https://...',  # Bandcamp provides this
    'streaming_platform': 'bandcamp', # 'youtube', 'youtube_music', 'bandcamp'
    'streaming_link': 'https://...'  # Original URL
}
```

**Platform-specific notes:**
- **YouTube**: No `purchase_link`, `album_name` is empty string
- **Bandcamp**: `purchase_link` and `streaming_link` are the same (original URL)
- **Bandcamp singles**: `album_name` is `None` for tracks not part of an album

---

## Troubleshooting

### YouTube API Not Working

**Problem:** "YouTube API key not configured"  
**Solution:** Ensure `YOUTUBE_API_KEY` is set in settings or environment variables

**Problem:** "Quota exceeded"  
**Solution:** Wait for quota reset (midnight PT) or request quota increase

**Problem:** "Video not found"  
**Solution:** Video may be private, deleted, or region-restricted

---

### Bandcamp Scraping Fails

**Problem:** "Could not find #name-section"  
**Solution:** 
- Check if URL is valid Bandcamp page
- Bandcamp may have changed page structure (requires code update)
- Try a different Bandcamp URL to confirm
- Check Selenium logs: `docker compose logs selenium`

**Problem:** "Service chromedriver unexpectedly exited. Status code was: 127"  
**Solution:**
- Ensure Selenium container is running: `docker compose ps`
- Restart Selenium: `docker compose restart selenium`
- Check `SELENIUM_REMOTE_URL` is set correctly in environment

**Problem:** "WebDriver error" or "Connection refused"  
**Solution:**
- **Docker**: Ensure Selenium container is running and accessible
- **Local**: Ensure Chrome/Chromium is installed
- Check network connectivity between containers
- Verify port 4444 is not blocked

**Problem:** "Timeout waiting for page load"  
**Solution:**
- Network may be slow
- Bandcamp may be down or blocking requests
- Increase timeout in code (currently 10 seconds)
- Check if too many requests triggered anti-bot measures

**Problem:** Scraping is very slow  
**Solution:**
- Expected: 3-5 seconds per request is normal
- For batch operations, implement caching or rate limiting
- Consider running Selenium container on more powerful hardware

---

### Selenium Container Issues

**Check if Selenium is running:**
```bash
docker compose ps selenium
```

**View Selenium logs:**
```bash
docker compose logs -f selenium
```

**Test Selenium connectivity:**
```bash
# From web container
docker compose exec web curl http://selenium:4444/status
```

**Access Selenium VNC (visual debugging):**
1. Open browser to `http://localhost:7900`
2. Password: `secret`
3. Watch the browser in action

**Restart Selenium:**
```bash
docker compose restart selenium
```

---

## Performance & Best Practices

### Bandcamp Scraping

**Best Practices:**
1. **Cache results** - Don't scrape the same URL repeatedly
2. **Rate limiting** - Add delays between multiple requests
3. **Error handling** - Always handle `BandCampMetaDataError`
4. **Resource cleanup** - Selenium driver is cleaned up automatically in `finally` block
5. **Monitoring** - Log scraping failures for debugging

**Performance Tips:**
- Each scrape: ~3-5 seconds (unavoidable due to page load)
- For bulk operations: Use background tasks (Celery, Django Q)
- Implement caching layer to store previously scraped metadata
- Consider database caching with TTL (time-to-live)

**Anti-Detection:**
- Don't scrape too frequently from same IP
- Random delays are built-in (1-3 seconds)
- User-agent rotation not implemented (may need for heavy use)
- Consider using proxies for high-volume scraping

### YouTube API

**Best Practices:**
1. **Monitor quota usage** - Track daily usage to avoid hitting limits
2. **Cache responses** - Store metadata to reduce API calls
3. **Handle rate limits** - Implement exponential backoff for 403 errors
4. **Batch requests** - When possible, batch multiple video lookups

---

## Testing

Refer to the README in the 'tests' folder

---

## Future Enhancements

### Known Limitations
- Bandcamp: No album art extraction
- YouTube: No album information from API
- Both: No genre information reliably available
- Both: Limited to public/accessible content only