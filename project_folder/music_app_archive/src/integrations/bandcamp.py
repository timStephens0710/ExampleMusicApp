import requests
from bs4 import BeautifulSoup
import json

from ..custom_exceptions import BandCampMetaDataError
from ..utils import orch_validate_input_string


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def extract_jsonld_from_bandcamp(bandcamp_url: str)-> dict:
    '''
    Extract JSON-LD structured data from a Bandcamp url.
    '''
    try:
        #1. Fetch the page
        response = requests.get(bandcamp_url, timeout=10)
        response.raise_for_status()  # Raise error for bad status codes
        
        # 2. Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        #3. Find the script tag with JSON-LD
        # Look for: <script type="application/ld+json">
        jsonld_script = soup.find('script', {'type': 'application/ld+json'})
        
        if not jsonld_script:
            logger.error("No JSON-LD script tag found")
            raise BandCampMetaDataError(f"No JSON-LD script tag found")
        
        #4. Extract the text content from the script tag
        jsonld_text = jsonld_script.string
        
        #5. Parse the JSON string into a Python dictionary
        jsonld_data = json.loads(jsonld_text)
        
        return jsonld_data
    except requests.RequestException as e:
        logger.error(f"Error fetching URL {bandcamp_url}: {e}")
        raise BandCampMetaDataError(f"Failed to fetch Bandcamp page: {str(e)}") from e
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from {bandcamp_url}: {e}")
        raise BandCampMetaDataError(f"Invalid JSON-LD format: {str(e)}") from e
    except BandCampMetaDataError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error extracting JSON-LD from {bandcamp_url}: {e}")
        raise BandCampMetaDataError(f"Unexpected error: {str(e)}") from e
    

def generate_bandcamp_meta_data_dictionary(jsonld_data: json, bandcamp_url: str) -> dict:
    '''
    #TODO build in checker for URL in case user submits the album link instead of a track link.
    '''
    #Validate bandcamp_url
    orch_validate_input_string(bandcamp_url, 'bandcamp_url')

    #Check jsonld_data
    if not jsonld_data or not isinstance(jsonld_data, dict):
        logger.error("generate_bandcamp_meta_data_dictionary: invalid jsonld_data for %s", bandcamp_url)
        raise BandCampMetaDataError("No JSON-LD data provided")
    
    #Generate bandcamp_meta_data_dict
    try:
        bandcamp_meta_data_dict = {
        'track_type': "track" ,
        'track_name': jsonld_data.get('name', 'Uknown track'),
        'artist': jsonld_data.get('byArtist', {}).get('name', 'Uknown artist'),
        'album_name': jsonld_data.get('inAlbum', {}).get('name'),
        'purchase_link': bandcamp_url,
        'mix_page': "",
        'record_label': "",
        'genre': "",           
        'streaming_platform': "bandcamp",
        'streaming_link': bandcamp_url,

        }
        logger.info(f"Successfully extracted Bandcamp metadata from: {bandcamp_url}")
        return bandcamp_meta_data_dict
    except Exception as e:
        logger.error(f"Failed to generate metadata dictionary for {bandcamp_url}: {str(e)}")
        raise BandCampMetaDataError(f"Failed to generate metadata: {str(e)}") from e

def orchestrate_bandcamp_meta_data_dictionary(bandcamp_url: str) -> dict:
    '''
    High-level orchestrator: validate input, extract JSON-LD, normalize dict.
    Raises BandcampMetadataError on failure.
    '''
    orch_validate_input_string(bandcamp_url, "bandcamp_url")

    try:
        jsonld_data = extract_jsonld_from_bandcamp(bandcamp_url)
        if not jsonld_data:
            logger.error("orchestrate_bandcamp_meta_data_dictionary: no JSON-LD for %s", bandcamp_url)
            raise BandCampMetaDataError("No structured JSON-LD metadata found on the page")

        bandcamp_meta_data_dict = generate_bandcamp_meta_data_dictionary(jsonld_data, bandcamp_url)
        return bandcamp_meta_data_dict
    except BandCampMetaDataError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error orchestrating Bandcamp metadata for {bandcamp_url}: {e}")
        raise BandCampMetaDataError(f"Failed to extract Bandcamp metadata: {str(e)}") from e

