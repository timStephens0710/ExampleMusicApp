from django.test import TestCase
from unittest.mock import patch, MagicMock, call
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException

from ..src.integrations.youtube import *
from ..src.integrations.bandcamp import *
from ..src.integrations.soundcloud import *
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
        self.bandcamp_url = "https://artist.bandcamp.com/track/song-name"

        self.platform = "bandcamp"
        
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
    @patch('music_app_archive.src.integrations.main_integrations.webdriver.Remote')
    def test_get_soup_with_remote_selenium(self, mock_remote):
        mock_driver = MagicMock()
        mock_driver.page_source = self.mock_bandcamp_html
        mock_remote.return_value = mock_driver
        
        result = get_soup(self.bandcamp_url, self.platform)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, BeautifulSoup)
        self.assertEqual(result.title.string, "Song Name | Artist Name")
        self.assertIsNotNone(result.find('h2', class_='trackTitle'))
        
        mock_remote.assert_called_once()
        self.assertEqual(
            mock_remote.call_args[1]['command_executor'],
            'http://selenium:4444'
        )
        
        mock_driver.execute_script.assert_called()
        mock_driver.get.assert_called_once_with(self.bandcamp_url)
        mock_driver.quit.assert_called_once()
    
    @patch.dict('os.environ', {}, clear=True)
    @patch('selenium.webdriver.chrome.service.Service')
    @patch('webdriver_manager.chrome.ChromeDriverManager')
    @patch('music_app_archive.src.integrations.main_integrations.webdriver.Chrome')
    def test_get_soup_with_local_chrome(self, mock_chrome, mock_driver_manager, mock_service):
        mock_driver = MagicMock()
        mock_driver.page_source = self.mock_bandcamp_html
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = '/fake/path/chromedriver'

        result = get_soup(self.bandcamp_url, self.platform)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, BeautifulSoup)
        self.assertEqual(result.title.string, "Song Name | Artist Name")

        mock_chrome.assert_called_once()
        mock_service.assert_called_once_with('/fake/path/chromedriver')
        mock_driver.quit.assert_called_once()
        
    @patch.dict('os.environ', {'SELENIUM_REMOTE_URL': 'http://selenium:4444'})
    @patch('music_app_archive.src.integrations.main_integrations.webdriver.Remote')
    def test_get_soup_parses_bandcamp_elements(self, mock_remote):
        mock_driver = MagicMock()
        mock_driver.page_source = self.mock_bandcamp_html
        mock_remote.return_value = mock_driver
        
        soup = get_soup(self.bandcamp_url, self.platform)
        
        track_title = soup.find('h2', class_='trackTitle')
        self.assertIsNotNone(track_title)
        self.assertEqual(track_title.get_text(), "Song Name")
        
        track_info = soup.find('div', id='trackInfo')
        self.assertIsNotNone(track_info)
    
    @patch.dict('os.environ', {'SELENIUM_REMOTE_URL': 'http://selenium:4444'})
    @patch('music_app_archive.src.integrations.main_integrations.webdriver.Remote')
    @patch('music_app_archive.src.integrations.main_integrations.time.sleep')
    def test_get_soup_implements_delays(self, mock_sleep, mock_remote):
        mock_driver = MagicMock()
        mock_driver.page_source = self.mock_bandcamp_html
        mock_remote.return_value = mock_driver
        
        get_soup(self.bandcamp_url, self.platform)
        
        self.assertTrue(mock_sleep.called)
        self.assertGreater(mock_sleep.call_count, 1)
    
    @patch.dict('os.environ', {'SELENIUM_REMOTE_URL': 'http://selenium:4444'})
    @patch('music_app_archive.src.integrations.main_integrations.webdriver.Remote')
    def test_get_soup_executes_javascript(self, mock_remote):
        mock_driver = MagicMock()
        mock_driver.page_source = self.mock_bandcamp_html
        mock_remote.return_value = mock_driver
        
        get_soup(self.bandcamp_url, self.platform)
        
        self.assertTrue(mock_driver.execute_script.called)
        
        calls = [str(call) for call in mock_driver.execute_script.call_args_list]
        anti_detection_called = any('webdriver' in str(call) for call in calls)
        self.assertTrue(anti_detection_called, "Anti-detection script should be executed")
        
        scroll_called = any('scrollTo' in str(call) for call in calls)
        self.assertTrue(scroll_called, "Scroll script should be executed")
    
    @patch.dict('os.environ', {'SELENIUM_REMOTE_URL': 'http://selenium:4444'})
    @patch('music_app_archive.src.integrations.main_integrations.webdriver.Remote')
    def test_get_soup_sets_chrome_options(self, mock_remote):
        mock_driver = MagicMock()
        mock_driver.page_source = self.mock_bandcamp_html
        mock_remote.return_value = mock_driver
        
        get_soup(self.bandcamp_url, self.platform)
        
        call_args = mock_remote.call_args
        options = call_args[1]['options']
        
        self.assertIsNotNone(options)
        self.assertTrue(hasattr(options, 'arguments'))
    
    @patch.dict('os.environ', {'SELENIUM_REMOTE_URL': 'http://selenium:4444'})
    @patch('music_app_archive.src.integrations.main_integrations.webdriver.Remote')
    def test_get_soup_driver_cleanup_on_success(self, mock_remote):
        mock_driver = MagicMock()
        mock_driver.page_source = self.mock_bandcamp_html
        mock_remote.return_value = mock_driver
        
        get_soup(self.bandcamp_url, self.platform)
        
        mock_driver.quit.assert_called_once()
    
    @patch.dict('os.environ', {'SELENIUM_REMOTE_URL': 'http://selenium:4444'})
    @patch('music_app_archive.src.integrations.main_integrations.webdriver.Remote')
    def test_get_soup_returns_parseable_html(self, mock_remote):
        mock_driver = MagicMock()
        mock_driver.page_source = self.mock_bandcamp_html
        mock_remote.return_value = mock_driver
        
        soup = get_soup(self.bandcamp_url, self.platform)
        
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
        
        self.mock_missing_section_html = '''
        <html>
            <body>
                <div id="other-section">
                    <h2>Some content</h2>
                </div>
            </body>
        </html>
        '''

        # Pre-built soup objects for orchestrator tests
        self.album_track_soup = BeautifulSoup(self.mock_album_track_html, 'html.parser')
        self.single_track_soup = BeautifulSoup(self.mock_single_track_html, 'html.parser')
        self.missing_section_soup = BeautifulSoup(self.mock_missing_section_html, 'html.parser')

    # --- scrape_bandcamp_page tests (unchanged, soup passed directly) ---

    def test_scrape_bandcamp_page_album_track_positive(self):
        result = scrape_bandcamp_page(self.album_track_soup)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        
        track_name, artist_name, album_name = result
        self.assertEqual(track_name, 'How Are We')
        self.assertEqual(artist_name, 'Horse Vision')
        self.assertEqual(album_name, 'Another Life')

    def test_scrape_bandcamp_page_single_track_positive(self):
        result = scrape_bandcamp_page(self.single_track_soup)
        
        track_name, artist_name, album_name = result
        self.assertEqual(track_name, 'Gangstalker Consulate Remix')
        self.assertEqual(artist_name, 'Consulate96')
        self.assertIsNone(album_name)

    def test_scrape_bandcamp_page_album_with_dash(self):
        soup = BeautifulSoup(self.mock_album_with_dash_html, 'html.parser')
        result = scrape_bandcamp_page(soup)
        
        track_name, artist_name, album_name = result
        self.assertEqual(track_name, 'Test Track')
        self.assertEqual(artist_name, 'Test Artist')
        self.assertEqual(album_name, 'Deluxe Edition')

    def test_scrape_bandcamp_page_missing_name_section(self):
        soup = BeautifulSoup(self.mock_missing_section_html, 'html.parser')
        
        with self.assertRaises(BandCampMetaDataError) as context:
            scrape_bandcamp_page(soup)
        
        self.assertIn("Could not find #name-section", str(context.exception))

    def test_scrape_bandcamp_page_missing_track_title(self):
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
        result = scrape_bandcamp_page(soup)
        
        track_name, artist_name, album_name = result
        self.assertIsNone(track_name)
        self.assertEqual(artist_name, 'Artist')
        self.assertEqual(album_name, 'Album')

    def test_scrape_bandcamp_page_missing_h3(self):
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
        result = scrape_bandcamp_page(soup)
        
        track_name, artist_name, album_name = result
        self.assertEqual(track_name, 'Track Name')
        self.assertIsNone(artist_name)
        self.assertIsNone(album_name)

    def test_scrape_bandcamp_page_whitespace_handling(self):
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
        result = scrape_bandcamp_page(soup)
        
        track_name, artist_name, album_name = result
        self.assertEqual(track_name, 'How Are We')
        self.assertEqual(artist_name, 'Horse Vision')
        self.assertEqual(album_name, 'Another Life')

    # --- orchestrate_bandcamp_meta_data_dictionary tests ---
    # No mock_get_soup needed — soup is passed directly

    def test_orchestrate_bandcamp_meta_data_dictionary_positive(self):
        '''
        Test that orchestrate creates correct metadata dictionary
        '''
        bandcamp_meta_data = orchestrate_bandcamp_meta_data_dictionary(
            self.album_track_soup,
            self.bandcamp_album_track_url
        )
        
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

    def test_orchestrate_bandcamp_single_track(self):
        '''
        Test orchestrate with single track (no album)
        '''
        bandcamp_meta_data = orchestrate_bandcamp_meta_data_dictionary(
            self.single_track_soup,
            self.bandcamp_single_track_url
        )
        
        self.assertEqual(bandcamp_meta_data.get('track_name'), 'Gangstalker Consulate Remix')
        self.assertEqual(bandcamp_meta_data.get('artist'), 'Consulate96')
        self.assertIsNone(bandcamp_meta_data.get('album_name'))
        self.assertEqual(bandcamp_meta_data.get('streaming_platform'), 'bandcamp')

    def test_orchestrate_bandcamp_meta_data_dictionary_negative(self):
        '''
        Test that orchestrate raises BandCampMetaDataError when soup is invalid
        '''
        with self.assertRaises(BandCampMetaDataError) as context:
            orchestrate_bandcamp_meta_data_dictionary(
                self.missing_section_soup,
                self.bandcamp_album_track_url
            )
        
        self.assertIn("Could not find #name-section", str(context.exception))

    def test_orchestrate_handles_scraping_error(self):
        '''
        Test orchestrate raises BandCampMetaDataError on missing name-section
        '''
        with self.assertRaises(BandCampMetaDataError):
            orchestrate_bandcamp_meta_data_dictionary(
                self.missing_section_soup,
                self.bandcamp_album_track_url
            )

    def test_orchestrate_metadata_structure(self):
        '''
        Test that orchestrate returns all expected dictionary keys
        '''
        result = orchestrate_bandcamp_meta_data_dictionary(
            self.album_track_soup,
            self.bandcamp_album_track_url
        )
        
        expected_keys = [
            'track_type', 'track_name', 'artist', 'album_name',
            'purchase_link', 'mix_page', 'record_label', 'genre',
            'streaming_platform', 'streaming_link'
        ]
        for key in expected_keys:
            self.assertIn(key, result)
        
        self.assertEqual(result.get('mix_page'), '')
        self.assertEqual(result.get('record_label'), '')
        self.assertEqual(result.get('genre'), '')


class SoundcloudIntegrationTest(TestCase):
    '''
    Test the Soundcloud integration functions in soundcloud.py
    '''
    def setUp(self):
        self.soundcloud_url = "https://soundcloud.com/resident-advisor/ex-795-avalon-emerson"
        self.soundcloud_track_url = "https://soundcloud.com/scissorandthread/drowning-reiling-hull-dub-1"
        self.mix_track_type = "mix"
        self.track_track_type = "track"
        self.mock_access_token = "mock_access_token_123"

        self.mock_token_response = {
            "access_token": self.mock_access_token
        }

        # Mock response for a mix
        self.mock_mix_response = {
            "title": "EX.795 Avalon Emerson",
            "user": {
                "username": "Resident Advisor",
                "permalink": "resident-advisor",
            }
        }

        # Mock response for a track
        self.mock_track_response = {
            "title": "Drowning (Reiling Hull Dub)",
            "user": {
                "username": "Scissor & Thread",
                "permalink": "scissorandthread",
            },
            "purchase_url": "https://scissorandthread.bandcamp.com",
            "label_name": "Scissor & Thread",
            "tag_list": "dub techno"
        }

    def _mock_requests(self, mock_post, mock_get, track_response=None):
        '''
        Helper to set up standard token + resolve mocks.
        Defaults to mix response unless track_response is provided.
        '''
        mock_token = MagicMock()
        mock_token.json.return_value = self.mock_token_response
        mock_post.return_value = mock_token

        mock_resolve = MagicMock()
        mock_resolve.json.return_value = track_response or self.mock_mix_response
        mock_get.return_value = mock_resolve

    # --- get_soundcloud_metadata tests ---

    @patch('music_app_archive.src.integrations.soundcloud.requests.get')
    @patch('music_app_archive.src.integrations.soundcloud.requests.post')
    def test_get_soundcloud_metadata_positive(self, mock_post, mock_get):
        '''
        Test get_soundcloud_metadata returns the full response dict
        '''
        self._mock_requests(mock_post, mock_get)

        result = get_soundcloud_metadata(self.soundcloud_url)

        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("title"), "EX.795 Avalon Emerson")
        self.assertEqual(result.get("user", {}).get("username"), "Resident Advisor")

    @patch('music_app_archive.src.integrations.soundcloud.requests.get')
    @patch('music_app_archive.src.integrations.soundcloud.requests.post')
    def test_get_soundcloud_metadata_calls_token_endpoint(self, mock_post, mock_get):
        '''
        Test that the OAuth token endpoint is called correctly
        '''
        self._mock_requests(mock_post, mock_get)

        get_soundcloud_metadata(self.soundcloud_url)

        mock_post.assert_called_once_with(
            "https://api.soundcloud.com/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": settings.SOUNDCLOUD_CLIENT_ID,
                "client_secret": settings.SOUNDCLOUD_CLIENT_SECRET
            }
        )

    @patch('music_app_archive.src.integrations.soundcloud.requests.get')
    @patch('music_app_archive.src.integrations.soundcloud.requests.post')
    def test_get_soundcloud_metadata_calls_resolve_endpoint(self, mock_post, mock_get):
        '''
        Test that the resolve endpoint is called with correct params and auth header
        '''
        self._mock_requests(mock_post, mock_get)

        get_soundcloud_metadata(self.soundcloud_url)

        mock_get.assert_called_once_with(
            "https://api.soundcloud.com/resolve",
            params={"url": self.soundcloud_url},
            headers={"Authorization": f"OAuth {self.mock_access_token}"}
        )

    @patch('music_app_archive.src.integrations.soundcloud.requests.get')
    @patch('music_app_archive.src.integrations.soundcloud.requests.post')
    def test_get_soundcloud_metadata_token_failure(self, mock_post, mock_get):
        '''
        Test that a token request HTTP failure raises SoundcloudMetaDataError
        '''
        mock_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")

        with self.assertRaises(SoundcloudMetaDataError) as context:
            get_soundcloud_metadata(self.soundcloud_url)

        self.assertIn("HTTP error fetching SoundCloud metadata", str(context.exception))
        mock_get.assert_not_called()

    @patch('music_app_archive.src.integrations.soundcloud.requests.get')
    @patch('music_app_archive.src.integrations.soundcloud.requests.post')
    def test_get_soundcloud_metadata_resolve_failure(self, mock_post, mock_get):
        '''
        Test that a resolve request HTTP failure raises SoundcloudMetaDataError
        '''
        mock_token = MagicMock()
        mock_token.json.return_value = self.mock_token_response
        mock_post.return_value = mock_token

        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")

        with self.assertRaises(SoundcloudMetaDataError) as context:
            get_soundcloud_metadata(self.soundcloud_url)

        self.assertIn("HTTP error fetching SoundCloud metadata", str(context.exception))

    @patch('music_app_archive.src.integrations.soundcloud.requests.get')
    @patch('music_app_archive.src.integrations.soundcloud.requests.post')
    def test_get_soundcloud_metadata_missing_access_token(self, mock_post, mock_get):
        '''
        Test that a missing access token in the token response raises SoundcloudMetaDataError
        '''
        mock_token = MagicMock()
        mock_token.json.return_value = {}
        mock_post.return_value = mock_token

        with self.assertRaises(SoundcloudMetaDataError) as context:
            get_soundcloud_metadata(self.soundcloud_url)

        self.assertIn("Failed to retrieve SoundCloud access token", str(context.exception))
        mock_get.assert_not_called()

    @patch('music_app_archive.src.integrations.soundcloud.requests.get')
    @patch('music_app_archive.src.integrations.soundcloud.requests.post')
    def test_get_soundcloud_metadata_unexpected_error(self, mock_post, mock_get):
        '''
        Test that an unexpected error raises SoundcloudMetaDataError
        '''
        mock_post.side_effect = Exception("Unexpected error")

        with self.assertRaises(SoundcloudMetaDataError) as context:
            get_soundcloud_metadata(self.soundcloud_url)

        self.assertIn("Failed to fetch SoundCloud metadata", str(context.exception))

    # --- orchestrate_soundcloud_meta_data_dictionary tests (mix) ---

    @patch('music_app_archive.src.integrations.soundcloud.get_soundcloud_metadata')
    def test_orchestrate_soundcloud_mix_positive(self, mock_get_metadata):
        '''
        Test that orchestrate returns correct metadata dictionary for a mix
        '''
        mock_get_metadata.return_value = self.mock_mix_response

        result = orchestrate_soundcloud_meta_data_dictionary(self.soundcloud_url, self.mix_track_type)

        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('track_type'), "mix")
        self.assertEqual(result.get('track_name'), "EX.795 Avalon Emerson")
        self.assertEqual(result.get('mix_page'), "Resident Advisor")
        self.assertEqual(result.get('streaming_platform'), "soundcloud")
        self.assertEqual(result.get('streaming_link'), self.soundcloud_url)

    @patch('music_app_archive.src.integrations.soundcloud.get_soundcloud_metadata')
    def test_orchestrate_soundcloud_mix_metadata_structure(self, mock_get_metadata):
        '''
        Test that orchestrate returns all expected keys for a mix
        '''
        mock_get_metadata.return_value = self.mock_mix_response

        result = orchestrate_soundcloud_meta_data_dictionary(self.soundcloud_url, self.mix_track_type)

        expected_keys = ['track_type', 'track_name', 'artist', 'mix_page', 'streaming_platform', 'streaming_link']
        for key in expected_keys:
            self.assertIn(key, result)

    # --- orchestrate_soundcloud_meta_data_dictionary tests (track) ---

    @patch('music_app_archive.src.integrations.soundcloud.get_soundcloud_metadata')
    def test_orchestrate_soundcloud_track_positive(self, mock_get_metadata):
        '''
        Test that orchestrate returns correct metadata dictionary for a track
        '''
        mock_get_metadata.return_value = self.mock_track_response

        result = orchestrate_soundcloud_meta_data_dictionary(self.soundcloud_track_url, self.track_track_type)

        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('track_type'), "track")
        self.assertEqual(result.get('track_name'), "Drowning (Reiling Hull Dub)")
        self.assertEqual(result.get('artist'), "Scissor & Thread")
        self.assertEqual(result.get('purchase_link'), "https://scissorandthread.bandcamp.com")
        self.assertEqual(result.get('record_label'), "Scissor & Thread")
        self.assertEqual(result.get('genre'), "dub techno")
        self.assertEqual(result.get('streaming_platform'), "soundcloud")
        self.assertEqual(result.get('streaming_link'), self.soundcloud_track_url)

    @patch('music_app_archive.src.integrations.soundcloud.get_soundcloud_metadata')
    def test_orchestrate_soundcloud_track_metadata_structure(self, mock_get_metadata):
        '''
        Test that orchestrate returns all expected keys for a track
        '''
        mock_get_metadata.return_value = self.mock_track_response

        result = orchestrate_soundcloud_meta_data_dictionary(self.soundcloud_track_url, self.track_track_type)

        expected_keys = ['track_type', 'track_name', 'artist', 'streaming_platform', 'streaming_link', 'purchase_link', 'record_label', 'genre']
        for key in expected_keys:
            self.assertIn(key, result)

    @patch('music_app_archive.src.integrations.soundcloud.get_soundcloud_metadata')
    def test_orchestrate_soundcloud_track_missing_optional_fields(self, mock_get_metadata):
        '''
        Test graceful handling when optional track fields are missing from response
        '''
        mock_get_metadata.return_value = {
            "title": "Drowning (Reiling Hull Dub)",
            "user": {"username": "Scissor & Thread"},
            "purchase_url": None,
            "label_name": None,
            "tag_list": None
        }

        result = orchestrate_soundcloud_meta_data_dictionary(self.soundcloud_track_url, self.track_track_type)

        self.assertEqual(result.get('track_name'), "Drowning (Reiling Hull Dub)")
        self.assertEqual(result.get('artist'), "Scissor & Thread")
        self.assertIsNone(result.get('purchase_link'))
        self.assertIsNone(result.get('record_label'))
        self.assertIsNone(result.get('genre'))

    # --- shared orchestrate tests ---

    @patch('music_app_archive.src.integrations.soundcloud.get_soundcloud_metadata')
    def test_orchestrate_soundcloud_negative(self, mock_get_metadata):
        '''
        Test that a generic exception is wrapped in SoundcloudMetaDataError
        '''
        mock_get_metadata.side_effect = Exception("Connection error")

        with self.assertRaises(SoundcloudMetaDataError) as context:
            orchestrate_soundcloud_meta_data_dictionary(self.soundcloud_url, self.mix_track_type)

        self.assertIn("Failed to extract Soundcloud metadat", str(context.exception))

    @patch('music_app_archive.src.integrations.soundcloud.get_soundcloud_metadata')
    def test_orchestrate_soundcloud_propagates_soundcloud_error(self, mock_get_metadata):
        '''
        Test that a SoundcloudMetaDataError from get_soundcloud_metadata is propagated directly
        '''
        mock_get_metadata.side_effect = SoundcloudMetaDataError("HTTP error fetching SoundCloud metadata: 401")

        with self.assertRaises(SoundcloudMetaDataError) as context:
            orchestrate_soundcloud_meta_data_dictionary(self.soundcloud_url, self.mix_track_type)

        self.assertIn("HTTP error fetching SoundCloud metadata", str(context.exception))

    @patch('music_app_archive.src.integrations.soundcloud.get_soundcloud_metadata')
    def test_orchestrate_soundcloud_passes_url(self, mock_get_metadata):
        '''
        Test that orchestrate passes the correct URL to get_soundcloud_metadata
        '''
        mock_get_metadata.return_value = self.mock_mix_response

        orchestrate_soundcloud_meta_data_dictionary(self.soundcloud_url, self.mix_track_type)

        mock_get_metadata.assert_called_once_with(self.soundcloud_url)

        
class MainIntegrationTest(TestCase):
    def setUp(self):
        self.bandcamp_track_url = "https://horsevision.bandcamp.com/track/how-are-we"
        self.track_type = 'track'
        self.empty_url = ""
        
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

    @patch('music_app_archive.src.integrations.main_integrations.get_soup')
    @patch('music_app_archive.src.integrations.main_integrations.orchestrate_bandcamp_meta_data_dictionary')
    def test_orchestrate_platform_api_positive(self, mock_bandcamp_orchestrate, mock_get_soup):
        '''
        Test orchestrate_platform_api successfully routes to Bandcamp
        '''
        mock_soup = MagicMock()
        mock_get_soup.return_value = mock_soup
        mock_bandcamp_orchestrate.return_value = self.mock_bandcamp_metadata
        
        meta_data_dict = orchestrate_platform_api(self.bandcamp_track_url, self.track_type)
        
        self.assertEqual(meta_data_dict.get('streaming_platform'), 'bandcamp')
        self.assertEqual(meta_data_dict.get('track_name'), 'How Are We')
        self.assertEqual(meta_data_dict.get('artist'), 'Horse Vision')
        self.assertEqual(meta_data_dict.get('album_name'), 'Another Life')
        
        #Verify get_soup was called, then its result passed to the orchestrator
        mock_get_soup.assert_called_once_with(self.bandcamp_track_url, 'bandcamp')
        mock_bandcamp_orchestrate.assert_called_once_with(mock_soup, self.bandcamp_track_url)

    def test_orchestrate_platform_api_negative(self):
        with self.assertRaises(ValueError):
            orchestrate_platform_api(self.empty_url, self.track_type)