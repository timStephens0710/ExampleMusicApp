from django.test import TestCase
from unittest.mock import patch, MagicMock, call
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException

from ..src.integrations.youtube import *
from ..src.integrations.bandcamp import *
from ..src.integrations.main_integrations import *


class YouTubeIntegrationTest(TestCase):
    '''
    Test the YouTube integration functions that work with the Google API
    '''
    def setUp(self):
        self.youtube_url = "https://www.youtube.com/watch?v=zYta6v1wZiI&list=LL&index=1"
        self.youtube_music_url = "https://music.youtube.com/watch?v=xvmaOOKTiKE&si=RbOKDeoX1mB4n2p-"
        self.youtube_channel_title = "Noel Gallagher - Topic"
        self.youtube_music_channel_title = "The Velvet Underground - Topic"
    
    def test_extract_youtube_video_id_from_url_positive(self):
        #Test youtube
        video_id = extract_youtube_video_id_from_url(self.youtube_url)
        self.assertEqual(video_id, "zYta6v1wZiI")

    def test_extract_youtube_music_video_id_from_url_positive(self):
        #Test youtube music
        video_id = extract_youtube_video_id_from_url(self.youtube_music_url)
        self.assertEqual(video_id, "xvmaOOKTiKE")

    def test_extract_youtube_video_id_from_url_negative(self):
        #Test invalid url music
        video_id = extract_youtube_video_id_from_url("https://maps.google.com/")
        self.assertIsNone(video_id)

    def test_get_artist_from_youtube_channel_title_positive(self):
        artist = get_artist_from_channel_title(self.youtube_channel_title)
        self.assertEqual(artist, "Noel Gallagher")

    def test_get_artist_from_youtube_music_channel_title_positive(self):
        artist = get_artist_from_channel_title(self.youtube_music_channel_title)
        self.assertEqual(artist, "The Velvet Underground")

    def test_get_get_youtube_platform_positive(self):
        streaming_platform=get_youtube_platform(self.youtube_music_url)
        self.assertEqual(streaming_platform, "youtube_music")

    @patch("music_app_archive.src.integrations.youtube.build")
    def test_get_youtube_metadata_positive(self, mock_build):
        #Prepare fake API return
        fake_response = {
            "items": [
                {
                    "snippet": {
                        "title": "If I Had A Gun…",
                        "channelTitle": "Noel Gallagher",
                        "description": "A sample description"
                    }
                }
            ]
        }

        #Mock the chain build().videos().list().execute() to return fake_response
        mock_client = MagicMock()
        mock_client.videos.return_value.list.return_value.execute.return_value = fake_response
        mock_build.return_value = mock_client
        #Generate meta_data_dict
        video_id = extract_youtube_video_id_from_url(self.youtube_url)
        meta_data_dict = get_youtube_metadata_dict(video_id)

        #Check the meta_data_dict
        self.assertEqual(meta_data_dict["track_name"], "If I Had A Gun…")
        self.assertIsNotNone(meta_data_dict["description"])
        self.assertEqual(meta_data_dict["artist"], "Noel Gallagher")


class TestGetSoup(TestCase):
    '''
    Test cases for the get_soup function
    '''
    
    def setUp(self):
        '''
        Set up test fixtures
        '''
        self.bandcamp_url = "https://artist.bandcamp.com/track/song-name"
        
        #Sample HTML that mimics a Bandcamp page
        self.mock_bandcamp_html = '''
        <html>
            <head>
                <title>Song Name | Artist Name</title>
            </head>
            <body>
                <div id="trackInfo">
                    <h2 class="trackTitle">Song Name</h2>
                    <h3><span class="fromAlbum">from <a href="/album/album-name">Album Name</a></span></h3>
                    <div id="name-section">
                        <h3><span>by <a href="/artist">Artist Name</a></span></h3>
                    </div>
                </div>
            </body>
        </html>
        '''
    
    @patch.dict('os.environ', {'SELENIUM_REMOTE_URL': 'http://selenium:4444'})
    @patch('music_app_archive.src.integrations.bandcamp.webdriver.Remote')
    def test_get_soup_with_remote_selenium(self, mock_remote):
        '''
        Test get_soup successfully returns BeautifulSoup when using remote Selenium
        '''
        #Setup mock driver
        mock_driver = MagicMock()
        mock_driver.page_source = self.mock_bandcamp_html
        mock_remote.return_value = mock_driver
        
        #Get soup object
        result = get_soup(self.bandcamp_url)
        
        #Assert - verify we got a BeautifulSoup object
        self.assertIsNotNone(result)
        self.assertIsInstance(result, BeautifulSoup)
        
        #Assert - verify content is correct
        self.assertEqual(result.title.string, "Song Name | Artist Name")
        self.assertIsNotNone(result.find('h2', class_='trackTitle'))
        
        #Assert - verify Remote was called with correct URL
        mock_remote.assert_called_once()
        self.assertEqual(
            mock_remote.call_args[1]['command_executor'],
            'http://selenium:4444'
        )
        
        #Assert - verify driver methods were called
        mock_driver.execute_script.assert_called()
        mock_driver.get.assert_called_once_with(self.bandcamp_url)
        mock_driver.quit.assert_called_once()
    
    @patch.dict('os.environ', {}, clear=True)  #No SELENIUM_REMOTE_URL
    @patch('selenium.webdriver.chrome.service.Service')
    @patch('webdriver_manager.chrome.ChromeDriverManager')
    @patch('music_app_archive.src.integrations.bandcamp.webdriver.Chrome')
    def test_get_soup_with_local_chrome(self, mock_chrome, mock_driver_manager, mock_service):
        '''
        Test get_soup successfully returns BeautifulSoup when using local Chrome
        '''
        #Setup mocks
        mock_driver = MagicMock()
        mock_driver.page_source = self.mock_bandcamp_html
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = '/fake/path/chromedriver'

        #Execute
        result = get_soup(self.bandcamp_url)

        #Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, BeautifulSoup)
        self.assertEqual(result.title.string, "Song Name | Artist Name")

        #Verify Chrome was used instead of Remote
        mock_chrome.assert_called_once()
        mock_service.assert_called_once_with('/fake/path/chromedriver')
        mock_driver.quit.assert_called_once()
        
    @patch.dict('os.environ', {'SELENIUM_REMOTE_URL': 'http://selenium:4444'})
    @patch('music_app_archive.src.integrations.bandcamp.webdriver.Remote')
    def test_get_soup_parses_bandcamp_elements(self, mock_remote):
        '''
        Test that get_soup correctly parses Bandcamp-specific elements
        '''
        #Setup
        mock_driver = MagicMock()
        mock_driver.page_source = self.mock_bandcamp_html
        mock_remote.return_value = mock_driver
        
        #Get soup object
        soup = get_soup(self.bandcamp_url)
        
        #Assert - check for Bandcamp-specific elements
        track_title = soup.find('h2', class_='trackTitle')
        self.assertIsNotNone(track_title)
        self.assertEqual(track_title.get_text(), "Song Name")
        
        track_info = soup.find('div', id='trackInfo')
        self.assertIsNotNone(track_info)
    
    @patch.dict('os.environ', {'SELENIUM_REMOTE_URL': 'http://selenium:4444'})
    @patch('music_app_archive.src.integrations.bandcamp.webdriver.Remote')
    @patch('music_app_archive.src.integrations.bandcamp.time.sleep')
    def test_get_soup_implements_delays(self, mock_sleep, mock_remote):
        '''
        Test that get_soup includes random delays for anti-detection
        '''
        #Setup
        mock_driver = MagicMock()
        mock_driver.page_source = self.mock_bandcamp_html
        mock_remote.return_value = mock_driver
        
        #Get soup object
        get_soup(self.bandcamp_url)
        
        #Assert - verify sleep was called (for delays)
        self.assertTrue(mock_sleep.called)
        #Should be called multiple times for different delays
        self.assertGreater(mock_sleep.call_count, 1)
    
    @patch.dict('os.environ', {'SELENIUM_REMOTE_URL': 'http://selenium:4444'})
    @patch('music_app_archive.src.integrations.bandcamp.webdriver.Remote')
    def test_get_soup_executes_javascript(self, mock_remote):
        '''
        Test that get_soup executes JavaScript for anti-detection and scrolling
        '''
        #Setup
        mock_driver = MagicMock()
        mock_driver.page_source = self.mock_bandcamp_html
        mock_remote.return_value = mock_driver
        
        #Get soup object
        get_soup(self.bandcamp_url)
        
        #Assert - verify execute_script was called
        self.assertTrue(mock_driver.execute_script.called)
        
        #Check for anti-detection script
        calls = [str(call) for call in mock_driver.execute_script.call_args_list]
        anti_detection_called = any('webdriver' in str(call) for call in calls)
        self.assertTrue(anti_detection_called, "Anti-detection script should be executed")
        
        #Check for scroll script
        scroll_called = any('scrollTo' in str(call) for call in calls)
        self.assertTrue(scroll_called, "Scroll script should be executed")
    
    @patch.dict('os.environ', {'SELENIUM_REMOTE_URL': 'http://selenium:4444'})
    @patch('music_app_archive.src.integrations.bandcamp.webdriver.Remote')
    def test_get_soup_sets_chrome_options(self, mock_remote):
        '''
        Test that get_soup configures Chrome options correctly
        '''
        #Setup
        mock_driver = MagicMock()
        mock_driver.page_source = self.mock_bandcamp_html
        mock_remote.return_value = mock_driver
        
        #Get soup object
        get_soup(self.bandcamp_url)
        
        #Assert - verify options were passed
        call_args = mock_remote.call_args
        options = call_args[1]['options']
        
        #Check that options object exists
        self.assertIsNotNone(options)
        
        #Verify headless mode and other arguments are in the options
        self.assertTrue(hasattr(options, 'arguments'))
    
    @patch.dict('os.environ', {'SELENIUM_REMOTE_URL': 'http://selenium:4444'})
    @patch('music_app_archive.src.integrations.bandcamp.webdriver.Remote')
    def test_get_soup_driver_cleanup_on_success(self, mock_remote):
        '''
        Test that driver is properly cleaned up after successful execution
        '''
        #Setup
        mock_driver = MagicMock()
        mock_driver.page_source = self.mock_bandcamp_html
        mock_remote.return_value = mock_driver
        
        #Get soup object
        get_soup(self.bandcamp_url)
        
        #Assert - verify quit was called
        mock_driver.quit.assert_called_once()
    
    @patch.dict('os.environ', {'SELENIUM_REMOTE_URL': 'http://selenium:4444'})
    @patch('music_app_archive.src.integrations.bandcamp.webdriver.Remote')
    def test_get_soup_returns_parseable_html(self, mock_remote):
        '''
        Test that returned BeautifulSoup can actually parse HTML content
        '''
        #Setup
        mock_driver = MagicMock()
        mock_driver.page_source = self.mock_bandcamp_html
        mock_remote.return_value = mock_driver
        
        #Get soup object
        soup = get_soup(self.bandcamp_url)
        
        #Assert - test various BeautifulSoup operations work
        self.assertTrue(soup.find('body'))
        self.assertTrue(soup.find_all('a'))
        self.assertEqual(len(soup.find_all('h2')), 1)
        self.assertEqual(len(soup.find_all('h3')), 2)


class BandcampIntegrationTest(TestCase):
    '''
    Test the Bandcamp integration functions that works with bandcamp.py module.
    '''
    def setUp(self):
        self.bandcamp_album_track_url = "https://horsevision.bandcamp.com/track/how-are-we"
        self.bandcamp_single_track_url = "https://consulate96.bandcamp.com/track/gangstalker-consulate-remix"
        self.empty_url = ""
        
        #Mock HTML for album track (2 links: album + artist)
        self.mock_album_track_html = '''
        <html>
            <head><title>How Are We | Horse Vision</title></head>
            <body>
                <div id="name-section">
                    <h2 class="trackTitle">How Are We</h2>
                    <h3>
                        <span class="fromAlbum">
                            from 
                            <a href="/album/another-life">Another Life</a>
                        </span>
                        by 
                        <a href="/artist/horse-vision">Horse Vision</a>
                    </h3>
                </div>
            </body>
        </html>
        '''
        
        #Mock HTML for single track (1 link: artist only)
        self.mock_single_track_html = '''
        <html>
            <head><title>Gangstalker Consulate Remix | Consulate96</title></head>
            <body>
                <div id="name-section">
                    <h2 class="trackTitle">Gangstalker Consulate Remix</h2>
                    <h3>
                        by 
                        <a href="/artist/consulate96">Consulate96</a>
                    </h3>
                </div>
            </body>
        </html>
        '''
        
        #Mock HTML for album track with "Album - Title" format
        self.mock_album_with_dash_html = '''
        <html>
            <body>
                <div id="name-section">
                    <h2 class="trackTitle">Test Track</h2>
                    <h3>
                        <span class="fromAlbum">
                            from 
                            <a href="/album/test">Another Life - Deluxe Edition</a>
                        </span>
                        by 
                        <a href="/artist/test">Test Artist</a>
                    </h3>
                </div>
            </body>
        </html>
        '''
        
        #Mock HTML missing name-section
        self.mock_missing_section_html = '''
        <html>
            <body>
                <div id="other-section">
                    <h2>Some content</h2>
                </div>
            </body>
        </html>
        '''

    def test_scrape_bandcamp_page_album_track_positive(self):
        '''
        Test scraping a track that's part of an album (2 links)
        '''
        #Setup
        soup = BeautifulSoup(self.mock_album_track_html, 'html.parser')
        
        #Execute
        result = scrape_bandcamp_page(soup)
        
        #Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        
        track_name, artist_name, album_name = result
        self.assertEqual(track_name, 'How Are We')
        self.assertEqual(artist_name, 'Horse Vision')
        self.assertEqual(album_name, 'Another Life')

    def test_scrape_bandcamp_page_single_track_positive(self):
        '''
        Test scraping a single track (1 link: artist only)
        '''
        #Setup
        soup = BeautifulSoup(self.mock_single_track_html, 'html.parser')
        
        #Execute
        result = scrape_bandcamp_page(soup)
        
        #Assert
        track_name, artist_name, album_name = result
        self.assertEqual(track_name, 'Gangstalker Consulate Remix')
        self.assertEqual(artist_name, 'Consulate96')
        self.assertIsNone(album_name)  #No album for single tracks

    def test_scrape_bandcamp_page_album_with_dash(self):
        '''
        Test scraping album name with ' - ' separator
        '''
        #Setup
        soup = BeautifulSoup(self.mock_album_with_dash_html, 'html.parser')
        
        #Execute
        result = scrape_bandcamp_page(soup)
        
        #Assert
        track_name, artist_name, album_name = result
        self.assertEqual(track_name, 'Test Track')
        self.assertEqual(artist_name, 'Test Artist')
        self.assertEqual(album_name, 'Deluxe Edition')  #Text after " - "

    def test_scrape_bandcamp_page_missing_name_section(self):
        '''
        Test that scrape raises error when #name-section is missing
        '''
        #Setup
        soup = BeautifulSoup(self.mock_missing_section_html, 'html.parser')
        
        #Execute & Assert
        with self.assertRaises(BandCampMetaDataError) as context:
            scrape_bandcamp_page(soup)
        
        self.assertIn("Could not find #name-section", str(context.exception))

    def test_scrape_bandcamp_page_missing_track_title(self):
        '''
        Test scraping when track title is missing
        '''
        #Setup - HTML with no trackTitle
        html = '''
        <html>
            <body>
                <div id="name-section">
                    <h3>
                        <a href="/album/test">Album</a>
                        <a href="/artist/test">Artist</a>
                    </h3>
                </div>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        #Execute
        result = scrape_bandcamp_page(soup)
        
        #Assert
        track_name, artist_name, album_name = result
        self.assertIsNone(track_name)
        self.assertEqual(artist_name, 'Artist')
        self.assertEqual(album_name, 'Album')

    def test_scrape_bandcamp_page_missing_h3(self):
        '''
        Test scraping when h3 tag is missing
        '''
        #Setup
        html = '''
        <html>
            <body>
                <div id="name-section">
                    <h2 class="trackTitle">Track Name</h2>
                </div>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        #Execute
        result = scrape_bandcamp_page(soup)
        
        #Assert
        track_name, artist_name, album_name = result
        self.assertEqual(track_name, 'Track Name')
        self.assertIsNone(artist_name)
        self.assertIsNone(album_name)

    @patch('music_app_archive.src.integrations.bandcamp.get_soup')
    def test_orchestrate_bandcamp_meta_data_dictionary_positive(self, mock_get_soup):
        '''
        Test that orchestrate creates correct metadata dictionary
        '''
        #Setup mock
        mock_soup = BeautifulSoup(self.mock_album_track_html, 'html.parser')
        mock_get_soup.return_value = mock_soup
        
        #Execute
        bandcamp_meta_data = orchestrate_bandcamp_meta_data_dictionary(
            self.bandcamp_album_track_url
        )
        
        #Assert
        self.assertIsInstance(bandcamp_meta_data, dict)
        self.assertEqual(bandcamp_meta_data.get('track_name'), 'How Are We')
        self.assertEqual(bandcamp_meta_data.get('artist'), 'Horse Vision')
        self.assertEqual(bandcamp_meta_data.get('album_name'), 'Another Life')
        self.assertEqual(
            bandcamp_meta_data.get('streaming_link'), 
            bandcamp_meta_data.get('purchase_link')
        )
        self.assertEqual(
            bandcamp_meta_data.get('streaming_link'),
            self.bandcamp_album_track_url
        )
        self.assertEqual(bandcamp_meta_data.get('streaming_platform'), 'bandcamp')
        self.assertEqual(bandcamp_meta_data.get('track_type'), 'track')
        
        #Verify get_soup was called with correct URL
        mock_get_soup.assert_called_once_with(self.bandcamp_album_track_url)

    @patch('music_app_archive.src.integrations.bandcamp.get_soup')
    def test_orchestrate_bandcamp_single_track(self, mock_get_soup):
        '''
        Test orchestrate with single track (no album)
        '''
        #Setup mock
        mock_soup = BeautifulSoup(self.mock_single_track_html, 'html.parser')
        mock_get_soup.return_value = mock_soup
        
        #Execute
        bandcamp_meta_data = orchestrate_bandcamp_meta_data_dictionary(
            self.bandcamp_single_track_url
        )
        
        #Assert
        self.assertEqual(bandcamp_meta_data.get('track_name'), 'Gangstalker Consulate Remix')
        self.assertEqual(bandcamp_meta_data.get('artist'), 'Consulate96')
        self.assertIsNone(bandcamp_meta_data.get('album_name'))
        self.assertEqual(bandcamp_meta_data.get('streaming_platform'), 'bandcamp')

    @patch('music_app_archive.src.integrations.bandcamp.get_soup')
    def test_orchestrate_bandcamp_meta_data_dictionary_negative(self, mock_get_soup):
        '''
        Test that orchestrate raises error when get_soup fails
        '''
        #Setup mock to raise error
        mock_get_soup.side_effect = Exception("Connection error")
        
        #Execute & Assert
        with self.assertRaises(BandCampMetaDataError) as context:
            orchestrate_bandcamp_meta_data_dictionary(self.bandcamp_album_track_url)
        
        self.assertIn("Failed to extract Bandcamp metadata", str(context.exception))

    @patch('music_app_archive.src.integrations.bandcamp.get_soup')
    def test_orchestrate_handles_scraping_error(self, mock_get_soup):
        '''
        Test orchestrate handles errors from scrape_bandcamp_page
        '''
        #Setup mock with invalid HTML
        mock_soup = BeautifulSoup(self.mock_missing_section_html, 'html.parser')
        mock_get_soup.return_value = mock_soup
        
        #Execute & Assert
        with self.assertRaises(BandCampMetaDataError):
            orchestrate_bandcamp_meta_data_dictionary(self.bandcamp_album_track_url)

    @patch('music_app_archive.src.integrations.bandcamp.get_soup')
    def test_orchestrate_metadata_structure(self, mock_get_soup):
        '''
        Test that orchestrate returns all expected dictionary keys
        '''
        #Setup mock
        mock_soup = BeautifulSoup(self.mock_album_track_html, 'html.parser')
        mock_get_soup.return_value = mock_soup
        
        #Execute
        result = orchestrate_bandcamp_meta_data_dictionary(self.bandcamp_album_track_url)
        
        #Assert - check all expected keys exist
        expected_keys = [
            'track_type', 'track_name', 'artist', 'album_name',
            'purchase_link', 'mix_page', 'record_label', 'genre',
            'streaming_platform', 'streaming_link'
        ]
        for key in expected_keys:
            self.assertIn(key, result)
        
        #Assert - check empty fields are empty strings
        self.assertEqual(result.get('mix_page'), '')
        self.assertEqual(result.get('record_label'), '')
        self.assertEqual(result.get('genre'), '')

    def test_scrape_bandcamp_page_whitespace_handling(self):
        '''
        Test that scraping properly strips whitespace
        '''
        #Setup - HTML with extra whitespace
        html = '''
        <html>
            <body>
                <div id="name-section">
                    <h2 class="trackTitle">  How Are We  </h2>
                    <h3>
                        from 
                        <a href="/album/test">  Another Life  </a>
                        by 
                        <a href="/artist/test">  Horse Vision  </a>
                    </h3>
                </div>
            </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        #Execute
        result = scrape_bandcamp_page(soup)
        
        #Assert - all whitespace should be stripped
        track_name, artist_name, album_name = result
        self.assertEqual(track_name, 'How Are We')
        self.assertEqual(artist_name, 'Horse Vision')
        self.assertEqual(album_name, 'Another Life')


class MainIntegrationTest(TestCase):
    '''
    Test the Main integration functions that orchestrate the respective streaming platform API's
    '''
    def setUp(self):
        self.bandcamp_track_url = "https://horsevision.bandcamp.com/track/how-are-we"
        self.track_type = 'track'
        self.empty_url = ""
        
        #Mock bandcamp_meta_data_dictionary 
        self.mock_bandcamp_metadata = {
            'track_type': 'track',
            'track_name': 'How Are We',
            'artist': 'Horse Vision',
            'album_name': 'Another Life',
            'purchase_link': self.bandcamp_track_url,
            'streaming_link': self.bandcamp_track_url,
            'streaming_platform': 'bandcamp',
            'mix_page': '',
            'record_label': '',
            'genre': '',
        }
    
    @patch('music_app_archive.src.integrations.main_integrations.orchestrate_bandcamp_meta_data_dictionary')
    def test_orchestrate_platform_api_positive(self, mock_bandcamp_orchestrate):
        '''
        Test orchestrate_platform_api successfully routes to Bandcamp
        '''
        #Setup mock
        mock_bandcamp_orchestrate.return_value = self.mock_bandcamp_metadata
        
        #Generate meta_data_dict
        meta_data_dict = orchestrate_platform_api(self.bandcamp_track_url, self.track_type)
        
        #Assert
        self.assertEqual(meta_data_dict.get('streaming_platform'), 'bandcamp')
        self.assertEqual(meta_data_dict.get('track_type'), 'track')
        self.assertEqual(meta_data_dict.get('track_name'), 'How Are We')
        self.assertEqual(meta_data_dict.get('artist'), 'Horse Vision')
        self.assertEqual(meta_data_dict.get('album_name'), 'Another Life')
        self.assertEqual(meta_data_dict.get('streaming_link'), meta_data_dict.get('purchase_link'))
        
        #Verify Bandcamp orchestration was called
        mock_bandcamp_orchestrate.assert_called_once_with(self.bandcamp_track_url)

    def test_orchestrate_platform_api_negative(self):
        '''
        Test orchestrate_platform_api raises error for empty URL
        '''
        #Execute & Assert
        with self.assertRaises(ValueError):
            meta_data_dict = orchestrate_platform_api(self.empty_url, self.track_type)