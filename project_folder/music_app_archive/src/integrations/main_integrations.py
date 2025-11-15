from .bandcamp import orchestrate_bandcamp_meta_data_dictionary
from .youtube import orchestrate_get_youtube_meta_data_dict

from ..custom_exceptions import BandCampMetaDataError, YouTubeMetaDataError, OrchestratePlatformMetaDataError
from ..utils import check_streaming_link_platform,  orch_validate_input_string


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def orchestrate_platform_api(streaming_url: str, track_type: str) -> dict:
    '''
    #TODO soundcloud next
    '''
    #Validate inputs
    orch_validate_input_string(streaming_url, 'streaming_url')
    orch_validate_input_string(track_type, 'track_type')

    try:
        #Leverage check_streaming_link_platform() to determine the platform
        platform = check_streaming_link_platform(streaming_url)

        if not platform:
            logger.error(f"Unsupported platform for streaming_url: {streaming_url}")
            raise ValueError(f"Unsupported platform for streaming_url: {streaming_url}")

        logger.info(f"The following platform, {platform}, has been detected.")
        
        #Choose which streaming platform
        if platform == 'youtube' or platform == "youtube.music":
            meta_data_dict = orchestrate_get_youtube_meta_data_dict(streaming_url, track_type)
        elif platform == 'bandcamp':
            meta_data_dict = orchestrate_bandcamp_meta_data_dictionary(streaming_url)
        logger.info(f"Successfully extracted metadata from {platform} for: {streaming_url}")
        return meta_data_dict
    except YouTubeMetaDataError as e:
        logger.error(f"YouTube metadata error for {streaming_url}: {str(e)}")
        raise
    except BandCampMetaDataError as e:
        logger.error(f"Bandcamp metadata error for {streaming_url}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in orchestrate_platform_api for {streaming_url}: {str(e)}")
        raise ValueError(f"Failed to extract metadata: {str(e)}") from e
    