import requests
from urllib.parse import urlparse

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

PLATFORM_DOMAINS = {
    'youtube': ['youtube.com', 'youtu.be', 'music.youtube.com', 'm.youtube.com'],
    'bandcamp': ['bandcamp.com'],
}


def orch_validate_input_string(input_string: str, name_input_string: str):
    '''
    Function used to validate an input string to see if it's empty or is type == str.
    '''
    if not input_string:
        logger.error(f"{name_input_string} is None or empty")
        raise ValueError(f"{name_input_string} cannot be None or empty")
    
    if not isinstance(input_string, str):
        logger.error(f"{name_input_string} must be a string, got {type(input_string)}")
        raise ValueError(f"{name_input_string} must be a string, got {type(input_string)}")

def get_hostname(streaming_url: str) -> str:
    '''
    The following function reads in a streaming_url and returns the hostname as a string.
    '''
    try:
        parsed_url = urlparse(streaming_url)
        hostname = parsed_url.hostname
        return str(hostname)
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def check_streaming_link_platform(streaming_link: str) -> str:
    '''
    The following function takes in a streaming link and checks if the hostname matches the 
    platform domains.
    '''
    try:
        #Get host name
        hostname = get_hostname(streaming_link)    
        
        if not hostname:
            return None
        
        for platform, domains in PLATFORM_DOMAINS.items():
            if any(hostname == domain or hostname.endswith(f'.{domain}') 
                for domain in domains):
                return platform
        
        return None
    except Exception:
        return None
    