from django.test import TestCase
from unittest.mock import patch, MagicMock

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

        # Mock the chain build().videos().list().execute() to return fake_response
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


class BandcampIntegrationTest(TestCase):
    '''
    Test the Bandcamp integration functions that works with bandcamp.py module.
    '''
    def setUp(self):
        self.bandcamp_track_url = "https://horsevision.bandcamp.com/track/how-are-we"
        self.empty_url = ""

    def test_extract_jsonld_data_postive(self):
        bandcamp_jsonldata = extract_jsonld_from_bandcamp(self.bandcamp_track_url)
        self.assertIsNotNone(bandcamp_jsonldata)

    def test_extract_jsonld_data_negative(self):
        with self.assertRaises(BandCampMetaDataError):
            bandcamp_jsonldata = extract_jsonld_from_bandcamp(self.empty_url)

    def test_bandcamp_meta_data_dictionary_positive(self):
        bandcamp_jsonldata = extract_jsonld_from_bandcamp(self.bandcamp_track_url)
        bandcamp_meta_data = generate_bandcamp_meta_data_dictionary(bandcamp_jsonldata, self.bandcamp_track_url)
        self.assertEqual(bandcamp_meta_data.get('track_name'), 'How Are We')
        self.assertEqual(bandcamp_meta_data.get('artist'), 'Horse Vision')
        self.assertEqual(bandcamp_meta_data.get('album_name'), 'Another Life')
        self.assertEqual(bandcamp_meta_data.get('streaming_link'), bandcamp_meta_data.get('purchase_link'))

    def test_orchestrate_bandcamp_meta_data_dictionary_positive(self):
        bandcamp_meta_data = orchestrate_bandcamp_meta_data_dictionary(self.bandcamp_track_url)
        self.assertEqual(bandcamp_meta_data.get('track_name'), 'How Are We')
        self.assertEqual(bandcamp_meta_data.get('artist'), 'Horse Vision')
        self.assertEqual(bandcamp_meta_data.get('album_name'), 'Another Life')
        self.assertEqual(bandcamp_meta_data.get('streaming_link'), bandcamp_meta_data.get('purchase_link'))

    def test_orchestrate_bandcamp_meta_data_dictionary_negative(self):
        with self.assertRaises(BandCampMetaDataError):
            bandcamp_meta_data = extract_jsonld_from_bandcamp(self.empty_url)


class MainIntegrationTest(TestCase):
    '''
    Test the Main integration functions that orchestrate the respective streaming platlform API's
    '''
    def setUp(self):
        self.bandcamp_track_url = "https://horsevision.bandcamp.com/track/how-are-we"
        self.track_type = 'track'
        self.empty_url = ""
        
    def test_orchestrate_platform_api_positive(self):
        meta_data_dict = orchestrate_platform_api(self.bandcamp_track_url, self.track_type)
        self.assertEqual(meta_data_dict.get('streaming_platform'), 'bandcamp')
        self.assertEqual(meta_data_dict.get('track_type'), 'track')
        self.assertEqual(meta_data_dict.get('track_name'), 'How Are We')
        self.assertEqual(meta_data_dict.get('artist'), 'Horse Vision')
        self.assertEqual(meta_data_dict.get('album_name'), 'Another Life')
        self.assertEqual(meta_data_dict.get('streaming_link'), meta_data_dict.get('purchase_link'))


    def test_orchestrate_platform_api_negative(self):
        '''
        '''
        with self.assertRaises(ValueError):
            meta_data_dict = orchestrate_platform_api(self.empty_url, self.track_type)
