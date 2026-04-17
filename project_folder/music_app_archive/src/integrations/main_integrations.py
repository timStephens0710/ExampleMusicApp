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


from .bandcamp import orchestrate_bandcamp_meta_data_dictionary
from .soundcloud import orchestrate_soundcloud_meta_data_dictionary
from .youtube import orchestrate_get_youtube_meta_data_dict

from ..custom_exceptions import BandCampMetaDataError, YouTubeMetaDataError, OrchestratePlatformMetaDataError, SoundcloudMetaDataError
from ..utils import check_streaming_link_platform,  orch_validate_input_string


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_soup(music_platform_url: str, platform: str) -> BeautifulSoup:
    '''
    Fetch a Bandcamp or Soundcloud page using Selenium and return a BeautifulSoup object.

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
        driver.get(music_platform_url)
        
        #Wait for the page to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            #Additional wait for JavaScript to execute
            time.sleep(random.uniform(2, 3))
        except TimeoutException:
            logger.warning(f"Timeout waiting for page load: {music_platform_url}")
        
        #Scroll to simulate human behavior
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(random.uniform(0.5, 1))
        
        #Get page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        
        logger.info(f"Successfully fetched {platform} page: {music_platform_url}")
        return soup
        
    except TimeoutException as e:
        logger.error(f"Timeout loading {platform} URL {music_platform_url}: {e}")
        raise
    except WebDriverException as e:
        logger.error(f"WebDriver error fetching {platform} URL {music_platform_url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching {platform} URL {music_platform_url}: {e}")
        raise
    finally:
        #Always close the browser
        if driver:
            driver.quit()


def orchestrate_platform_api(streaming_url: str, track_type: str) -> dict:
    '''
    
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
        if platform == 'youtube' or platform == 'youtube.music':
            meta_data_dict = orchestrate_get_youtube_meta_data_dict(streaming_url, track_type)
        elif platform == 'bandcamp':
            soup = get_soup(streaming_url, platform)
            meta_data_dict = orchestrate_bandcamp_meta_data_dictionary(soup, streaming_url)
        elif platform == 'soundcloud':
                meta_data_dict =  orchestrate_soundcloud_meta_data_dictionary(streaming_url, track_type)
        logger.info(f"Successfully extracted metadata from {platform} for: {streaming_url}")
        return meta_data_dict
    except YouTubeMetaDataError as e:
        logger.error(f"YouTube metadata error for {streaming_url}: {str(e)}")
        raise
    except BandCampMetaDataError as e:
        logger.error(f"Bandcamp metadata error for {streaming_url}: {str(e)}")
        raise
    except SoundcloudMetaDataError as e:
        logger.error(f"Soundcloud metadata error for {streaming_url}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in orchestrate_platform_api for {streaming_url}: {str(e)}")
        raise ValueError(f"Failed to extract metadata: {str(e)}") from e
    