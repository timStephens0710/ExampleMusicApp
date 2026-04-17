from bs4 import BeautifulSoup
import requests

from django.conf import settings

from ..custom_exceptions import SoundcloudMetaDataError


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_soundcloud_metadata(soundcloud_url: str) -> dict:
    '''
    Use SoundCloud API to get get a response json
    '''
    try:
        # Get OAuth access token using client credentials
        token_response = requests.post("https://api.soundcloud.com/oauth2/token", data={
            "grant_type": "client_credentials",
            "client_id": settings.SOUNDCLOUD_CLIENT_ID,
            "client_secret": settings.SOUNDCLOUD_CLIENT_SECRET
        })
        token_response.raise_for_status()
        access_token = token_response.json().get("access_token")

        if not access_token:
            raise SoundcloudMetaDataError("Failed to retrieve SoundCloud access token")

        # Resolve the URL to a track object using OAuth token
        resolve_endpoint = "https://api.soundcloud.com/resolve"
        headers = {"Authorization": f"OAuth {access_token}"}
        params = {"url": soundcloud_url}

        response = requests.get(resolve_endpoint, params=params, headers=headers)
        response.raise_for_status()
        soundcloud_metadata = response.json()

        return soundcloud_metadata

    except SoundcloudMetaDataError:
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching SoundCloud metadata for {soundcloud_url}: {e}")
        raise SoundcloudMetaDataError(f"HTTP error fetching SoundCloud metadata: {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error fetching SoundCloud metadata for {soundcloud_url}: {e}")
        raise SoundcloudMetaDataError(f"Failed to fetch SoundCloud metadata: {str(e)}") from e
    

def orchestrate_soundcloud_meta_data_dictionary(soundcloud_url: str, track_type: str) -> dict:
    '''
    The following function is the orchestration module to generate the meta_data_dictionary for 
    Soundcloud links.

    Order of operations:
        - Get the response JSON via the SoundCloud API
        - Generates the metadata_dict based on the track_type
    '''
    try:
        #Get the information via the API
        soundcloud_response = get_soundcloud_metadata(soundcloud_url)

        #Extract metadat from soundcloud_response and generate soundcloud_metadata_dict based on track_type
        if track_type == "mix":
            soundcloud_metadata_dict = {
                'track_type': track_type,
                'track_name':  soundcloud_response.get("title"),
                'artist': soundcloud_response.get("metadata_artist"),
                'mix_page': soundcloud_response.get("user", {}).get("username"),
                'streaming_platform': "soundcloud",
                'streaming_link': soundcloud_url
            }
        else:
            soundcloud_metadata_dict = {
                'track_type': track_type,
                'track_name': soundcloud_response.get("title"),
                'artist': soundcloud_response.get("user", {}).get("username"),
                'streaming_platform': "soundcloud",
                'streaming_link': soundcloud_url,
                'purchase_link': soundcloud_response.get("purchase_url"),
                'record_label': soundcloud_response.get("label_name"),
                'genre': soundcloud_response.get("tag_list")
            }
                
        return soundcloud_metadata_dict

    except SoundcloudMetaDataError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error orchestrating Soundcloud metadata for {soundcloud_url}: {e}")
        raise SoundcloudMetaDataError(f"Failed to extract Soundcloud metadat: {str(e)}") from e
