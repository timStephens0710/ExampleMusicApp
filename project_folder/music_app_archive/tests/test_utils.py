from django.test import TestCase
from music_app_archive.src.utils import (
    orch_validate_input_string,
    get_hostname,
    check_streaming_link_platform
)

class TestUtils(TestCase):
    def test_validate_input_string_valid(self):
        '''
        Test validation passes for valid string
        '''
        try:
            orch_validate_input_string('test', 'test_param')
        except ValueError:
            self.fail('Validation should not raise ValueError for valid string')
    
    def test_validate_input_string_none(self):
        '''
        Test validation fails for None
        '''
        with self.assertRaises(ValueError):
            orch_validate_input_string(None, 'test_param')
    
    def test_validate_input_string_empty(self):
        '''
        Test validation fails for empty string
        '''
        with self.assertRaises(ValueError):
            orch_validate_input_string('', 'test_param')
    
    def test_get_hostname_youtube(self):
        '''
        Test hostname extraction from YouTube URL
        '''
        hostname = get_hostname('https://www.youtube.com/watch?v=123')
        self.assertEqual(hostname, 'www.youtube.com')
    
    def test_check_platform_youtube(self):
        '''
        Test YouTube platform detection
        '''
        platform = check_streaming_link_platform('https://youtube.com/watch?v=123')
        self.assertEqual(platform, 'youtube')
    
    def test_check_platform_bandcamp(self):
        '''
        Test Bandcamp platform detection
        '''
        platform = check_streaming_link_platform('https://artist.bandcamp.com/track/song')
        self.assertEqual(platform, 'bandcamp')
    
    def test_check_platform_unsupported(self):
        '''
        Test unsupported platform returns None
        '''
        platform = check_streaming_link_platform('https://unsupported.com')
        self.assertIsNone(platform)
