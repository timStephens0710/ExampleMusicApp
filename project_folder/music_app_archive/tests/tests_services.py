# tests/test_services.py
from django.test import TestCase
from django.http import Http404
from django.contrib.auth import get_user_model


from music_app_archive.src.services import get_playlist, get_playlist_tracks
from music_app_archive.models import Playlist, Track, PlaylistTrack

User = get_user_model()

class TestPlaylistServices(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Th1$Pa$$w0rd'
        )
        self.playlist = Playlist.objects.create(
            playlist_name='Test Playlist',
            owner=self.user
        )
    
    def test_get_playlist_exists(self):
        '''
        Test retrieving an existing playlist
        '''
        playlist = get_playlist('Test Playlist', self.user)
        self.assertEqual(playlist.playlist_name, 'Test Playlist')
        self.assertEqual(playlist.owner, self.user)
    
    def test_get_playlist_not_found(self):
        '''
        Test 404 raised for non-existent playlist
        '''
        
        with self.assertRaises(Http404):
            get_playlist('Non Existent', self.user)
    
    def test_get_playlist_tracks_empty(self):
        '''
        Test empty playlist returns empty list'
        '''
        tracks = get_playlist_tracks(self.playlist)
        self.assertIsNone(tracks)
    
    def test_get_playlist_tracks_with_data(self):
        '''
        Test playlist with tracks returns correct data'
        '''
        track = Track.objects.create(
            track_name='Test Song',
            artist='Test Artist'
        )
        PlaylistTrack.objects.create(
            playlist=self.playlist,
            track=track,
            added_by=self.user
        )
        
        tracks = get_playlist_tracks(self.playlist)
        
        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0]['track_name'], 'Test Song')
        self.assertEqual(tracks[0]['artist'], 'Test Artist')
