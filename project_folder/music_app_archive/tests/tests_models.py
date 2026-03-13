from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from ..models import *

User = get_user_model()


# Create your tests here.
class UserPlaylistsTest(TestCase):
    '''
    The fillowing test case contains positve and negative test cases for the Playlist model.
    '''
    def setUp(self):
        self.user_1 = User.objects.create_user(
            email="test1@user.com",
            password="Meep!234",
            username="simple_john"
        )

        self.user_2 = User.objects.create_user(
            email="test2@user.com",
            password="Meep!234",
            username="critical_jack"
        )

        self.positive_playlist_1 = Playlist.objects.create(
            playlist_name = 'test_playlist_1',
            owner = self.user_1,
            playlist_type = 'track',
            is_private = 'public'
        )

        self.positive_playlist_2 = Playlist.objects.create(
            playlist_name = 'test_playlist_1',
            owner = self.user_2,
            playlist_type = 'track',
            is_private = 'public'        
            )


    def test_create_playlist_positve(self):
        self.assertEqual(self.positive_playlist_1.playlist_name, 'test_playlist_1')
        self.assertEqual(self.positive_playlist_1.owner.username, 'simple_john')
        self.assertEqual(self.positive_playlist_1.is_private, 'public')

    def test_same_owner_different_playlist_names_positive(self):
        test_playlist_3 = Playlist.objects.create(
            playlist_name = 'minimal tech house',
            owner = self.user_1,
            playlist_type = 'track',
            is_private = 'private'
        )

        test_playlist_4 = Playlist.objects.create(
            playlist_name = 'movie samples',
            owner = self.user_1,
            playlist_type = 'samples',
            is_private = 'private'
        )

        self.assertEqual(Playlist.objects.filter(owner=self.user_1).count(), 3)
        self.assertEqual(test_playlist_4.playlist_type, 'samples')
        self.assertNotEqual(self.positive_playlist_1.slug, test_playlist_3.slug)
        self.assertNotEqual(self.positive_playlist_2.slug, test_playlist_4.slug)

    def test_same_playlist_name_different_users(self):
        self.assertEqual(Playlist.objects.count(), 2)
        self.assertNotEqual(self.positive_playlist_1.id, self.positive_playlist_2.id)
        self.assertEqual(self.positive_playlist_1.playlist_name, self.positive_playlist_2.playlist_name)

    def test_different_owners_can_have_same_slug(self):
        '''
        
        '''
        self.assertEqual(Playlist.objects.count(), 2)
        self.assertEqual(self.positive_playlist_1.slug, self.positive_playlist_2.slug)
        self.assertEqual(self.positive_playlist_1.slug, 'test_playlist_1')


    def test_unique_playlist_name_constraint(self):
        with self.assertRaises(IntegrityError) as context:
            Playlist.objects.create(
            playlist_name = 'test_playlist_1',
            owner = self.user_1,
            playlist_type = 'track',
            is_private = 'public'
        )
            
        self.assertIn('violates', str(context.exception).lower())

    def test_case_sensitivity_playlist_names(self):
        '''
        
        '''
        with self.assertRaises(IntegrityError):
                Playlist.objects.create(
                    playlist_name='Test_playlist_1',  # Different case but same slug
                    owner=self.user_1,
                    playlist_type = 'track',
                    is_private = 'public'
                    )

    def test_slug_generation_with_special_characters(self):
        '''
        
        '''
        special_characters_playlist = Playlist.objects.create(
            playlist_name='80\'s & 90\'s Hits!',
            owner=self.user_1,
            playlist_type='track'
        )
        self.assertEqual(special_characters_playlist.slug, '80s-90s-hits')

        with self.assertRaises(IntegrityError):
            Playlist.objects.create(
                playlist_name='80s & 90s Hits',  # Different chars but same slug
                owner=self.user_1,
                playlist_type='mixes'
            )            

    def test_str_representation(self):
        '''
        
        '''
        self.assertEqual(str(self.positive_playlist_1), 'test_playlist_1 by simple_john')

    def test_invalid_playlist_type(self):
        '''
        
        '''
        with self.assertRaises(ValidationError):
            invalid_playlist = Playlist(
            playlist_name = 'invalid',
            owner = self.user_1,
            playlist_type = 'nothing',
            is_private = 'public'
            )
            invalid_playlist.full_clean()


class TrackTest(TestCase):
    '''
    Test cases:
        - two different track types being successfully added
    '''
    def setUp(self):
        self.user_1 = User.objects.create_user(
            email="test1@user.com",
            password="Meep!234",
            username="simple_john"
        )

        self.simple_track = Track.objects.create(
            track_type='track',
            track_name='Another Life',
            artist='Horse Vision',
            album_name='Another Name',
            created_by=self.user_1,
            purchase_link='https://horsevision.bandcamp.com/album/another-life'
        )

        Track.objects.create(
            track_type='mix',
            track_name='Motion Ward with JS and Saigey @ The Lot Radio 11-03-2023',
            artist='Motion Ward',
            mix_page = 'Lot Radio',
            created_by=self.user_1
        )

        Track.objects.create(
            track_type='sample',
            track_name='All Due Respect',
            artist='The Wire',
            created_by=self.user_1
        )

    def test_track_positive(self):
        '''
        
        '''
        self.assertEqual(Track.objects.count(), 3)

        #Pull out a specific row
        sample_object = Track.objects.get(track_type='sample')
        self.assertEqual(sample_object.artist, 'The Wire')
        self.assertIsNotNone(sample_object.date_added)
            
    def test_str_representation(self):
        '''
        
        '''
        self.assertEqual(str(self.simple_track), 'Another Life by Horse Vision')

    def invalid_track_type(self):
        '''
        
        '''
        with self.assertRaises(ValidationError):
            invalid_track = Track(
                track_type='vinyl',
                track_name='Another Life',
                artist='Horse Vision',
                album_name='Another Name',
                created_by=self.user_1,
                purchase_link='https://horsevision.bandcamp.com/album/another-life'
            )
            invalid_track.clean()

    def test_ordering_by_date_added(self):
        '''
        
        '''
        tracks = list(Track.objects.all())

        # Most recent should be first
        self.assertEqual(tracks[0].track_name, 'All Due Respect')
        self.assertEqual(tracks[1].track_name, 'Motion Ward with JS and Saigey @ The Lot Radio 11-03-2023')
        self.assertEqual(tracks[2].track_name, 'Another Life')
 

class StreamlingLinkTest(TestCase):
    '''

    '''
    def setUp(self):
        self.user_1 = User.objects.create_user(
            email="test1@user.com",
            password="Meep!234",
            username="simple_john"
        )

        self.simple_track_bc = Track.objects.create(
            track_type='track',
            track_name='Chemicals',
            artist='Horse Vision',
            album_name='Another Name',
            created_by=self.user_1,
            purchase_link='https://horsevision.bandcamp.com/album/another-life'
        )

        self.streaming_track_bc = StreamingLink.objects.create(
            track=self.simple_track_bc,
            streaming_platform='bandcamp',
            streaming_link='https://horsevision.bandcamp.com/track/chemicals-2'
        )

        self.streaming_track_yt = StreamingLink.objects.create(
            track=self.simple_track_bc,
            streaming_platform='youtube',
            streaming_link='https://www.youtube.com/watch?v=ATRDAcYzyGI'
        )

        self.soundcloud_mix = Track.objects.create(
            track_type='mix',
            track_name='Motion Ward with JS and Saigey @ The Lot Radio 11-03-2023',
            artist='Motion Ward',
            mix_page = 'Lot Radio',
            created_by=self.user_1
        )

        self.streaming_link_sc = StreamingLink.objects.create(
            track=self.soundcloud_mix,
            streaming_platform='soundcloud',
            streaming_link='https://soundcloud.com/thelotradio/motion-ward-with-js-and-saigey-the-lot-radio-11-03-2023'
        )


    def test_streamling_links_positive(self):
        '''
        This also covers the test case:
            - Same track different streaming platforms
        '''
        self.assertEqual(StreamingLink.objects.count(), 3)

        #Test the first instance
        streaming_links = list(StreamingLink.objects.all())
        self.assertEqual(streaming_links[0].streaming_platform, 'bandcamp')
        self.assertEqual(streaming_links[0].streaming_link, 'https://horsevision.bandcamp.com/track/chemicals-2')
        self.assertIsNotNone(streaming_links[0].created_at)

    def test_invalid_platform_name(self):
        '''
        
        '''
        with self.assertRaises(ValidationError):
            invalid_platform = StreamingLink(
            track=self.soundcloud_mix,
            streaming_platform='napster',
            streaming_link='https://soundcloud.com/thelotradio/motion-ward-with-js-and-saigey-the-lot-radio-11-03-2023'
            )
            invalid_platform.full_clean()

    def test_uniqueness_stream_link(self):
        '''
        
        '''
        different_track = Track.objects.create(
            track_type='mix',
            track_name='Sven Vath Lover Parade',
            artist='Papa Sven',
            mix_page = 'Mudd',
            created_by=self.user_1
        )    

        with self.assertRaises(IntegrityError):
            StreamingLink.objects.create(
                track=different_track,
                streaming_platform='youtube',
                streaming_link='https://soundcloud.com/thelotradio/motion-ward-with-js-and-saigey-the-lot-radio-11-03-2023'
            )

    def test_uniqueness_track_streaming_platform(self):
        '''
        existing_link = StreamingLink.objects.create(
            track=self.soundcloud_mix,
            streaming_platform='soundcloud',
            streaming_link='https://soundcloud.com/thelotradio/motion-ward-with-js-and-saigey-the-lot-radio-11-03-2023'
        )
        
        '''
        with self.assertRaises(IntegrityError):
                StreamingLink.objects.create(
                    track=self.soundcloud_mix,  
                    streaming_platform='soundcloud',
                    streaming_link='https://soundcloud.com/different-url'
                )


class PlaylistTrackTest(TestCase):
    '''
    Test cases:
        - unique constraints:
            - playlist + position
    '''
    def setUp(self):
        self.user_1 = User.objects.create_user(
            email="test1@user.com",
            password="Meep!234",
            username="simple_john"
        )

        self.horse_vision_track = Track.objects.create(
            track_type='track',
            track_name='Chemicals',
            artist='Horse Vision',
            album_name='Another Name',
            created_by=self.user_1,
            purchase_link='https://horsevision.bandcamp.com/album/another-life'
        )

        self.pogues_track = Track.objects.create(
            track_type='track',
            track_name='Dirty Old Town',
            artist='The Pogues',
            created_by=self.user_1,
        )

        self.first_playlist = Playlist.objects.create(
            playlist_name = 'my_first_playlist',
            owner = self.user_1,
            playlist_type = 'track',
            is_private = 'public'
        )

        self.add_horse_vision_track = PlaylistTrack.objects.create(
            playlist=self.first_playlist,
            track=self.horse_vision_track,
            added_by=self.user_1
        )

        self.add_pogues_track = PlaylistTrack.objects.create(
            playlist=self.first_playlist,
            track=self.pogues_track,
            added_by=self.user_1
        )

    def test_playlist_track_positive(self):
        '''
        
        '''
        self.assertEqual(PlaylistTrack.objects.count(), 2)

        #Test the first instance
        playlist_tracks = list(PlaylistTrack.objects.all())
        self.assertEqual(playlist_tracks[0].track.track_name, 'Chemicals')
        self.assertEqual(playlist_tracks[0].playlist.playlist_name, 'my_first_playlist')
        self.assertEqual(playlist_tracks[0].added_by.username, 'simple_john')
        self.assertIsNotNone(playlist_tracks[0].added_at)

    def test_unique_playlist_track(self):
        '''
        '''
        with self.assertRaises(IntegrityError):
            PlaylistTrack.objects.create(
                        playlist=self.first_playlist,
                        track=self.pogues_track,
                        added_by=self.user_1
                    )
            

def tearDown(self):
    '''
    Clean up test data.
    '''
    Playlist.objects.all().delete()
    User.objects.all().delete()
    Track.objects.all().delete()
    PlaylistTrack.objects.all().delete()