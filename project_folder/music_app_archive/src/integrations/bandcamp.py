from bs4 import BeautifulSoup

import time
import random
import logging
import os

from ..custom_exceptions import BandCampMetaDataError


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def scrape_bandcamp_page(soup: BeautifulSoup) -> list:
    '''
    Scrape bandcamp HTML to get the following:
        - track_name
        - artist_name
        - album_name
    '''
    #Anchor to specific section in the HTML page
    name_section = soup.find("div", id="name-section")
    if not name_section:
        raise BandCampMetaDataError("Could not find #name-section")

    #Get track_name
    track_tag = name_section.find("h2", class_="trackTitle")
    track_name = track_tag.get_text(strip=True) if track_tag else None

    #Links inside the h3
    h3 = name_section.find("h3")
    links = h3.find_all("a") if h3 else []

    #Initialise variables
    album_name = None
    artist_name = None

    #Get album & artist names
    if len(links) == 1:
        #Only artist aka could be a single release
        artist_name = links[0].get_text(strip=True)

    elif len(links) >= 2:
        raw_album_text = links[0].get_text(strip=True)
        artist_name = links[1].get_text(strip=True)

        if " - " in raw_album_text:
            album_name = raw_album_text.split(" - ", 1)[1].strip()
        else:
            album_name = raw_album_text.strip()
    
    bandcamp_page_information = [track_name, artist_name, album_name]
    return bandcamp_page_information


def orchestrate_bandcamp_meta_data_dictionary(soup: BeautifulSoup, bandcamp_url: str) -> dict:
    '''
    The following function is the orchestration module to generate the meta_data_dictionary for 
    Bandcamp links.

    Order of operations:
        - It gets the soup object
        - Scrapes the BandCamp HTML to get the meta data
        - Generate the meta data dictionary
    '''
    try:
        # #Get Bandcamp Soup object
        # bandcamp_soup = get_soup(bandcamp_url)

        #Scrape BandCamp page to get song information
        bandcamp_page_information = scrape_bandcamp_page(soup)

        #Generate bandcamp_meta_data_dict
        bandcamp_meta_data_dict = {
        'track_type': "track" ,
        'track_name': bandcamp_page_information[0],
        'artist': bandcamp_page_information[1],
        'album_name': bandcamp_page_information[2],
        'purchase_link': bandcamp_url,
        'mix_page': "",
        'record_label': "",
        'genre': "",           
        'streaming_platform': "bandcamp",
        'streaming_link': bandcamp_url,
        }
        return bandcamp_meta_data_dict
    except BandCampMetaDataError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error orchestrating Bandcamp metadata for {bandcamp_url}: {e}")
        raise BandCampMetaDataError(f"Failed to extract Bandcamp metadata: {str(e)}") from e