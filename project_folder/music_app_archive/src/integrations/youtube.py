from urllib.parse import urlparse, parse_qs
import re

from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..utils import orch_validate_input_string
from ..custom_exceptions import YouTubeMetaDataError

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def extract_youtube_video_id_from_url(youtube_url: str) -> str:
    '''
    Extract a YouTube video id from a variety of URL formats.
    Returns the 11-char video id or None if it cannot be extracted.
    '''
    #validate youtube_url
    orch_validate_input_string(youtube_url, 'youtube_url')

    try:
        parsed_url = urlparse(youtube_url)
    except Exception as exc:
        logger.exception("Failed to parse URL %r: %s", youtube_url, exc)
        return None

    hostname = parsed_url.hostname or ""
    hostname = hostname.lower()

    # Standard watch URL: youtube.com/watch?v=VIDEO_ID
    if hostname in ("www.youtube.com", "youtube.com", "music.youtube.com"):
        query_params = parse_qs(parsed_url.query)
        vid = query_params.get("v", [None])[0]
        if vid and re.match(r"^[A-Za-z0-9_-]{11}$", vid):
            return vid
        logger.debug("No valid 'v' param found in URL %r", youtube_url)
        return None

    #Shortened URL: youtu.be/VIDEO_ID
    if hostname == "youtu.be":
        path = (parsed_url.path or "").lstrip("/")
        if path and re.match(r"^[A-Za-z0-9_-]{11}$", path):
            return path
        logger.debug("Short youtu.be URL did not contain a valid id: %r", youtube_url)
        return None

    #Some embedded urls: /embed/VIDEO_ID
    if "/embed/" in parsed_url.path:
        candidate = parsed_url.path.split("/embed/")[-1].split("/")[0]
        if re.match(r"^[A-Za-z0-9_-]{11}$", candidate):
            return candidate

    logger.debug("extract_youtube_video_id_from_url: unsupported hostname %r in URL %r", hostname, youtube_url)
    return None


def get_artist_from_channel_title(channel_title: str) -> str:
    '''
    Derive an artist string from a channel title.
    Safe if input is None or not in expected format.
    Returns None if no reliable artist can be extracted.
    '''
    #Validate channel_title
    orch_validate_input_string(channel_title, "channel_title")

    try:
        #Prefer the first token split by ' - ' or '|' or '•'
        for sep in [" - ", " | ", "•", "-"]:
            if sep in channel_title:
                artist = channel_title.split(sep)[0].strip()
                if artist:
                    return artist
        #Fallback: use the whole title trimmed
        return channel_title.strip() or None
    except Exception as exc:
        logger.exception("Unexpected error parsing channel title %r: %s", channel_title, exc)
        return None

def get_youtube_platform(youtube_url: str) -> str:
    '''
    Return 'youtube_music' or 'youtube' based on hostname.
    Falls back to 'youtube' if detection fails.
    '''
    #Validate url
    orch_validate_input_string(youtube_url, "youtube_url")

    try:
        parsed = urlparse(youtube_url)
        hostname = (parsed.hostname or "").lower()
        if "music.youtube.com" in hostname:
            return "youtube_music"
        return "youtube"
    except Exception as exc:
        logger.exception("get_youtube_platform: failed to parse url %r: %s", youtube_url, exc)
        return "youtube"


def get_youtube_metadata_dict(video_id: str) -> dict:
    '''
    Retrieve YouTube metadata for a given video_id using the YouTube Data API.
    Raises YouTubeMetaDataError on failure. Returns a normalized dict on success.
    '''
    #Validate video_id
    orch_validate_input_string(video_id, "video_id")
    #basic sanity check of ID shape
    if not re.match(r"^[A-Za-z0-9_-]{11}$", video_id):
        raise YouTubeMetaDataError(f"video_id does not look valid: {video_id}")

    try:
        youtube = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)
    except Exception as exc:
        logger.exception("Failed to build YouTube client: %s", exc)
        raise YouTubeMetaDataError("Failed to initialize YouTube client") from exc
    
    try:
        response = youtube.videos().list(part="snippet", id=video_id).execute()
    except HttpError as exc:
        logger.exception("YouTube API HttpError for id=%s: %s", video_id, exc)
        raise YouTubeMetaDataError(f"YouTube API error: {exc}") from exc
    except Exception as exc:
        logger.exception("Unexpected error calling YouTube API for id=%s: %s", video_id, exc)
        raise YouTubeMetaDataError("Unexpected error calling YouTube API") from exc
    

    #Extract snippet from the response
    items = response["items"]
    if not items:
        # sometimes response contains an 'error' payload rather than raising HttpError
        logger.debug("YouTube returned no items for id=%s. Response: %r", video_id, response)
        raise YouTubeMetaDataError(f"No video found for id={video_id}")
    
    item=items[0]
    snippet = item["snippet"]

    #Get the title out relevant fields
    track_name = snippet.get("title")
    #Get the artist from channel title
    channel_title = snippet.get("channelTitle")
    artist = get_artist_from_channel_title(channel_title) if channel_title else None
    #Get description
    description = snippet.get("description")

    #Create meta_data_dict
    meta_data_dict = {
        "track_name": track_name,
        "artist": artist,
        "description": description,
        'album_name': "",
        'mix_page': "",
        'record_label': "",
        'genre': "",           
        'purchase_link': ""
    }
    return meta_data_dict


def orchestrate_get_youtube_meta_data_dict(youtube_url: str, track_type: str) -> dict:
    '''
    High-level orchestrator: extract id, fetch metadata, and update the dict.
    Raises ValueError or YouTubeMetadataError if something goes wrong.
    '''
    #Validate youtube_url
    orch_validate_input_string(youtube_url, "youtube_url")

    #Extract video ID
    youtube_video_id = extract_youtube_video_id_from_url(youtube_url)
    if not youtube_video_id:
        raise ValueError("Could not extract a valid YouTube video id from the URL")

    try:
        #Generate meta_data_dict
        meta_data_dict =  get_youtube_metadata_dict(youtube_video_id)
        #Add streaming_platform to meta_data_dict
        streaming_platform = get_youtube_platform(youtube_url)
        meta_data_dict.update({"streaming_platform": streaming_platform})
        #Add url to meta_data_dict
        meta_data_dict.update({"track_type": track_type})
        meta_data_dict.update({"streaming_link": youtube_url})
        return meta_data_dict
    except YouTubeMetaDataError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error orchestrating YouTube metadata for {youtube_url}: {e}")
        raise YouTubeMetaDataError(f"Failed to extract YouTube metadata: {str(e)}") from e
