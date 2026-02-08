from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import random
import logging
import os

from ..custom_exceptions import BandCampMetaDataError
from ..utils import orch_validate_input_string


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_soup(bandcamp_url: str) -> BeautifulSoup:
    '''
    Fetch a Bandcamp page using Selenium and return a BeautifulSoup object.

    This function:
    - uses headless Chrome with realistic browser fingerprinting
    - implements anti-detection measures
    - waits for dynamic content to load
    - adds random delays to mimic human behavior
    - works in both local dev and Docker environments
    '''
    driver = None
    
    try:
        #Configure Chrome options for stealth
        chrome_options = Options()
        
        #Headless mode
        chrome_options.add_argument('--headless=new')
        
        #Essential arguments to avoid detection
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        #Realistic window size
        chrome_options.add_argument('--window-size=1920,1080')
        
        #Set realistic user agent
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/122.0.0.0 Safari/537.36'
        )
        
        #Additional privacy/security options
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--lang=en-GB')
        
        #Check if we should use remote Selenium (Docker) or local
        selenium_url = os.getenv('SELENIUM_REMOTE_URL')
        
        if selenium_url:
            #Running in Docker - use remote Selenium service
            logger.info(f"Using remote Selenium at {selenium_url}")
            driver = webdriver.Remote(
                command_executor=selenium_url,
                options=chrome_options
            )
        else:
            #Running locally - use local Chrome
            logger.info("Using local Chrome WebDriver")
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
        
        #Override navigator.webdriver flag (anti-detection)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        #Add random delay before loading
        time.sleep(random.uniform(1, 2))
        
        #Load the page
        driver.get(bandcamp_url)
        
        #Wait for the page to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            #Additional wait for JavaScript to execute
            time.sleep(random.uniform(2, 3))
        except TimeoutException:
            logger.warning(f"Timeout waiting for page load: {bandcamp_url}")
        
        #Scroll to simulate human behavior
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(random.uniform(0.5, 1))
        
        #Get page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        
        logger.info(f"Successfully fetched Bandcamp page: {bandcamp_url}")
        return soup
        
    except TimeoutException as e:
        logger.error(f"Timeout loading Bandcamp URL {bandcamp_url}: {e}")
        raise
    except WebDriverException as e:
        logger.error(f"WebDriver error fetching Bandcamp URL {bandcamp_url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching Bandcamp URL {bandcamp_url}: {e}")
        raise
    finally:
        #Always close the browser
        if driver:
            driver.quit()

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


def orchestrate_bandcamp_meta_data_dictionary(bandcamp_url: str) -> dict:
    '''
    The following function is the orchestration module to generate the meta_data_dictionary for 
    Bandcamp links.

    Order of operations:
        - It gets the soup object
        - Scrapes the BandCamp HTML to get the meta data
        - Generate the meta data dictionary
    '''
    try:
        #Get Bandcamp Soup object
        bandcamp_soup = get_soup(bandcamp_url)

        #Scrape BandCamp page to get song information
        bandcamp_page_information = scrape_bandcamp_page(bandcamp_soup)

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