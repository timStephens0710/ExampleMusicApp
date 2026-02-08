from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


from ..models import *

User = get_user_model()


class BaseTestCase(TestCase):
    '''
    Base test case with common setup for all playlist tests.
    '''
    def setUp(self):
        self.user_1 = User.objects.create_user(
            email="test1@user.com",
            password="Meep!234",
            username="simple_john",
            email_verified=True
        )

        self.test_playlist = Playlist.objects.create(
            playlist_name = 'test_playlist',
            owner = self.user_1,
            playlist_type = 'track',
            is_private = 'public'
        )

        self.wip_playlist = Playlist.objects.create(
            playlist_name = 'WIP playlist',
            owner = self.user_1,
            playlist_type = 'track',
            is_private = 'private'
        )

        self.simple_track_1 = Track.objects.create(
            track_type='track',
            track_name='Another Life',
            artist='Horse Vision',
            album_name='Another Name',
            created_by=self.user_1,
            purchase_link='https://horsevision.bandcamp.com/album/another-life'
        )

        self.simple_track_2 = Track.objects.create(
            track_type='track',
            track_name='If I Had A Gun…',
            artist="Noel Gallagher's High Flying Birds",
            album_name="Noel Gallagher's High Flying Birds",
            created_by=self.user_1
        )

        self.simple_streaming_link_2 = StreamingLink.objects.create(
            track = self.simple_track_2,
            streaming_platform='youtube',
            streaming_link = 'https://www.youtube.com/watch?v=zYta6v1wZiI&list=LL&index=1',
            added_by = self.user_1
        )

class CreatePlaylistTest(BaseTestCase):
    '''
    This test case assseses the functionality of the view, create_playlist()

    It handles the following test cases:
        - Positive:
            - The user can successfully create a playlist,
            - The user is successfully redirected to the add_track_to_playlist() view
    '''
    def setUp(self):
        super().setUp()
        
        self.playlist_name = 'test_playlist_1'
        self.playlist_type = 'tracks'
        self.playlist_description = 'this playlist exists'
        self.is_private = 'public'
    

    def test_create_playlist_positive(self):
        #Login 
        self.client.login(email="test1@user.com", password="Meep!234")

        url = reverse('create_playlist', args=[self.user_1.username])

        response = self.client.post(url, {
            'playlist_name': self.playlist_name,
            'playlist_type': self.playlist_type,
            'description': self.playlist_description,
            'is_private': self.is_private
            })

        #Verify that the playlist is created
        self.assertEqual(response.status_code, 302)

       #Verify playlist was created in database
        self.assertTrue(
            Playlist.objects.filter(
                playlist_name=self.playlist_name,
                owner=self.user_1
            ).exists()
        )
        
        #Get the created playlist
        created_playlist = Playlist.objects.get(
            playlist_name=self.playlist_name,
            owner=self.user_1
        )

        self.assertEqual(created_playlist.playlist_name, self.playlist_name)
        self.assertEqual(created_playlist.owner.username, self.user_1.username)
        self.assertEqual(created_playlist.description, self.playlist_description)
        self.assertEqual(created_playlist.playlist_type, self.playlist_type)
        self.assertEqual(created_playlist.is_private, self.is_private)

        #Check correct redirect url after 
        expected_url = reverse("add_streaming_link_to_playlist", args=[self.user_1.username, created_playlist.playlist_name])
        self.assertRedirects(response, expected_url)


class AddTrackToPlaylistTest(BaseTestCase):
    '''
    Track is successfully added + correct redirection.

    this is handy for debugging: print(f"Response content: {response.content.decode()}")

    #TODO fix up this test once I've got Bandcamp added to my API's.
    '''
    def setUp(self):        
        self.track_type = 'track'
        self.track_name = 'Another Life'
        self.artist = 'Horse Vision'
        self.album = 'Another Name'
        self.genre = 'indie'
        self.purchase_link = 'https://horsevision.bandcamp.com/album/another-life'
        self.streaming_platform = 'bandcamp'


    # def test_add_track_positive(self):
    #     #Login
    #     self.client.login(email="test1@user.com", password="Meep!234")

    #     #url
    #     url = reverse("add_track_to_playlist", args=[self.user_1.username, self.test_playlist.playlist_name])

    #     response = self.client.post(url, {
    #         'track_type': self.track_type,
    #         'track_name': self.track_name,
    #         'artist': self.artist,
    #         'album_name': self.album,
    #         'genre': self.genre,
    #         'purchase_link': self.purchase_link,
    #         'streaming_platform': self.streaming_platform,
    #         'streaming_link': self.purchase_link
    #     })

    #     #Check the track was added
    #     self.assertEqual(response.status_code, 302)

    #     #Get relevant playlist
    #     playlist = Playlist.objects.get(playlist_name=self.test_playlist.playlist_name)

    #     #Verify track was added in database
    #     self.assertTrue(
    #         PlaylistTrack.objects.filter(
    #             added_by=self.user_1
    #         ).exists()
    #     )
    #     #Verify track is added to PlaylistTrack
    #     playlist_track = PlaylistTrack.objects.get(playlist=playlist.id)
    #     self.assertEqual(playlist_track.playlist, self.test_playlist)
    #     self.assertEqual(playlist_track.added_by, self.user_1)
    #     self.assertEqual(playlist_track.position, 1)
    #     self.assertIsNotNone(playlist_track.added_at)

    #     #Verify track is added to PlaylistTrack
    #     self.assertTrue(
    #         Track.objects.filter(
    #             track_name=self.track_name,
    #             artist=self.artist
    #         ).exists()
    #     )

    #     track = Track.objects.get(pk=playlist_track.track_id)
    #     self.assertEqual(track.track_name, self.track_name)
    #     self.assertEqual(track.track_type, self.track_type)
    #     self.assertEqual(track.artist, self.artist)
    #     self.assertEqual(track.album_name, self.album)
    #     self.assertEqual(track.genre, self.genre)
    #     self.assertEqual(track.purchase_link, self.purchase_link)
    #     self.assertEqual(track.created_by, self.user_1)
    #     self.assertIsNotNone(track.date_added)

    #     #Verify track is added to StreamingLink
    #     self.assertTrue(
    #         StreamingLink.objects.filter(
    #             track=track.id,
    #             streaming_platform=self.streaming_platform
    #         ).exists()
    #     )

    #     streaming_track_link = StreamingLink.objects.get(track=track.id)

    #     self.assertEqual(streaming_track_link.streaming_platform, self.streaming_platform)
    #     self.assertEqual(streaming_track_link.streaming_link, self.purchase_link)
    #     self.assertEqual(streaming_track_link.added_by, self.user_1)
    #     self.assertIsNotNone(track.date_added)

    #     #Check correct redirect url after 
    #     expected_url = reverse("view_edit_playlist", args=[self.user_1.username, self.test_playlist.playlist_name])
    #     self.assertRedirects(response, expected_url)


class ViewTracksInPlaylist(BaseTestCase):
    '''
    Test cases:
        - positive:
            - if n tracks are added to the playlist,  count(list_of_tracks) = n
            - the correct playlist is retrieved, via playlist_name + user
            - check the correct values are displayed in the correpsonding fields
            - track ordering
        - Edge cases:
            - empty playlist should contain zero rows

    '''
    def setUp(self):
        super().setUp()

        self.simple_streaming_link_1 = StreamingLink.objects.create(
            track = self.simple_track_1,
            streaming_platform='bandcamp',
            streaming_link = self.simple_track_1.purchase_link,
            added_by = self.user_1
        )

        PlaylistTrack.objects.create(
            playlist=self.test_playlist,
            track=self.simple_track_1,
            added_by=self.user_1
        )

        PlaylistTrack.objects.create(
            playlist=self.test_playlist,
            track=self.simple_track_2,
            added_by=self.user_1
        )

    def test_view_playlist_track_positive(self):
        '''
        
        '''
        #Login
        self.client.login(email="test1@user.com", password="Meep!234")
        #Create url
        url = reverse("view_edit_playlist", args=[self.user_1.username, self.test_playlist.playlist_name])
        #Generate response
        response = self.client.get(url)
        #Get context
        context = response.context

        #Access individual context variables
        playlist_name = context['playlist_name']
        list_of_tracks = context['list_of_tracks']

        self.assertEqual(playlist_name, self.test_playlist.playlist_name)
        self.assertEqual(len(list_of_tracks), 2)
        self.assertEqual(list_of_tracks[0]['track_name'], 'Another Life')
        self.assertEqual(list_of_tracks[1]['artist'], "Noel Gallagher's High Flying Birds")

    
    def test_view_playlist_empty(self):
        #Login
        self.client.login(email="test1@user.com", password="Meep!234")
        #Create URL
        url = reverse("view_edit_playlist", args=[self.user_1.username, self.wip_playlist.playlist_name])
        #Generate response
        response = self.client.get(url)
        #Get the context
        context = response.context

        #Access individual context variables
        list_of_tracks = context['list_of_tracks']
        self.assertEqual(len(list_of_tracks), 0)


class AddLinkToTrackTest(BaseTestCase):
    '''
    view we're testing:
        - add_streaming_link_to_playlist(request, username, playlist_name)
            - url: path('<str:username>/<str:playlist_name>/add_link_to_track', views.add_streaming_link_to_playlist, name = 'add_streaming_link_to_playlist') #add track to a specific playlist

    #TODO Test cases:
        - positive cases:
            - Link works
            - Retrieve youtube_meta_data_dict from request.session
                - Test the data dictionary is not empty
    '''
    def test_add_streaming_link_to_playlist_positive(self):
        '''
        '''
        #Login
        self.client.login(email="test1@user.com", password="Meep!234")
        #Create url
        url = reverse("add_streaming_link_to_playlist", args=[self.user_1.username, self.test_playlist.playlist_name])
        #Generate response
        response = self.client.post(url, {
            'track_type': self.simple_track_2.track_type,
            'streaming_link': self.simple_streaming_link_2.streaming_link
        })

        #Check the form was submitted correctly
        self.assertEqual(response.status_code, 302)

        #Check the correct redirect url after
        expected_url = reverse("add_track_to_playlist", args=[self.user_1.username, self.test_playlist.playlist_name])
        self.assertRedirects(response, expected_url)

    def test_add_streaming_link_to_playlist_negative(self):
        #Login
        self.client.login(email="test1@user.com", password="Meep!234")
        #Create url
        url = reverse("add_streaming_link_to_playlist", args=[self.user_1.username, self.test_playlist.playlist_name])
        #Generate response
        response = self.client.post(url, {
            'track_type':"track",
            'streaming_link': "https://maps.google.com/"
        })

        #Check error response code
        self.assertEqual(response.status_code, 200)

        #Extract the form from the context
        form = response.context["add_streaming_link_to_playlist_form"]
        #Test that form is invalid
        self.assertFalse(form.is_valid())
        #Test that the correct error message is raised
        self.assertIn(
            "URL must be from YouTube or Bandcamp",
            form.errors["streaming_link"]
        )

    def test_meta_data_dictionary_positive(self):
        '''

        '''
        #Login
        self.client.login(email="test1@user.com", password="Meep!234")
        #Create url
        url = reverse("add_streaming_link_to_playlist", args=[self.user_1.username, self.test_playlist.playlist_name])
        #Generate response
        response = self.client.post(url, {
            'track_type': self.simple_track_2.track_type,
            'streaming_link': self.simple_streaming_link_2.streaming_link
        })
        #Access request
        session = self.client.session
        #Get meta_data_dictionary
        meta_data_dictionary = session.get("meta_data_dict")

        #Test meta_data_dictionary
        self.assertIsNotNone(meta_data_dictionary)
        self.assertEqual(meta_data_dictionary['track_name'], self.simple_track_2.track_name)
        self.assertEqual(meta_data_dictionary['streaming_platform'], self.simple_streaming_link_2.streaming_platform)


def tearDown(self):
    '''
    Clean up test data.
    '''
    Playlist.objects.all().delete()
    User.objects.all().delete()
    Track.objects.all().delete()
    PlaylistTrack.objects.all().delete()
