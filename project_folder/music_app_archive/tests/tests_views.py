import json

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

        self.bad_user = User.objects.create_user(
            email="badUser@test.com",
            password="rand0mV!llian1234",
            username="bad_user",
            email_verified=True
        )

        self.unauth_user = User.objects.create_user(
            email="unAuthUser@test.com",
            password="Fre0D0cker$2026",
            username="unauth_user",
            email_verified=False
        )

        self.test_playlist = Playlist.objects.create(
            playlist_name = 'test_playlist',
            owner = self.user_1,
            playlist_type = 'tracks',
            is_private = 'public'
        )

        self.wip_playlist = Playlist.objects.create(
            playlist_name = 'WIP playlist',
            owner = self.user_1,
            playlist_type = 'tracks',
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

        self.playlist_track_1 =PlaylistTrack.objects.create(
            playlist=self.test_playlist,
            track=self.simple_track_1,
            added_by=self.user_1
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

        self.playlist_track_2 = PlaylistTrack.objects.create(
            playlist=self.test_playlist,
            track=self.simple_track_2,
            added_by=self.user_1
        )

        self.simple_track_3 = Track.objects.create(
            track_type='track',
            track_name='Future',
            artist="Nils Petter Molvær, Moritz von Oswald",
            album_name="1/1",
            created_by=self.user_1
        )

        self.simple_streaming_link_3 = StreamingLink.objects.create(
            track = self.simple_track_3,
            streaming_platform='youtube',
            streaming_link = 'https://www.youtube.com/watch?v=V4tc_r4O_6k&list=LL&index=2',
            added_by = self.user_1
        )

        self.playlist_track_3 = PlaylistTrack.objects.create(
            playlist=self.test_playlist,
            track=self.simple_track_3,
            added_by=self.user_1
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
    '''
    def setUp(self):        
        self.playlist_type = 'tracks'
        self.track_type = 'track'
        self.track_name = 'Another Life'
        self.artist = 'Horse Vision'
        self.album = 'Another Name'
        self.genre = 'indie'
        self.purchase_link = 'https://horsevision.bandcamp.com/album/another-life'
        self.streaming_platform = 'bandcamp'



class ViewTracksInPlaylist(BaseTestCase):
    '''
    Test cases:
        - positive:
            - if n tracks are added to the playlist,  count(list_of_playlist_tracks) = n
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
        list_of_playlist_tracks = context['list_of_playlist_tracks']

        self.assertEqual(playlist_name, self.test_playlist.playlist_name)
        self.assertEqual(len(list_of_playlist_tracks), 3)
        self.assertEqual(list_of_playlist_tracks[0]['track_name'], 'Another Life')
        self.assertEqual(list_of_playlist_tracks[1]['artist'], "Noel Gallagher's High Flying Birds")

    
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
        list_of_playlist_tracks = context['list_of_playlist_tracks']
        self.assertEqual(len(list_of_playlist_tracks), 0)


class AddLinkToTrackTest(BaseTestCase):
    '''
    view we're testing:
        - add_streaming_link_to_playlist(request, username, playlist_name)
            - url: path('<str:username>/<str:playlist_name>/add_link_to_track', views.add_streaming_link_to_playlist, name = 'add_streaming_link_to_playlist') #add track to a specific playlist
    '''
    def test_add_streaming_link_to_playlist_positive(self):
        #Login
        login_success = self.client.login(email="test1@user.com", password="Meep!234")
        self.assertTrue(login_success, "Login failed")
        
        url = reverse("add_streaming_link_to_playlist", 
                    args=[self.user_1.username, self.test_playlist.playlist_name])
        
        post_data = {
            'track_type': self.simple_track_2.track_type,
            'streaming_link': self.simple_streaming_link_2.streaming_link
        }
        
        response = self.client.post(url, post_data)

        self.assertEqual(response.status_code, 302, 
                        f"Expected redirect (302) but got {response.status_code}")
        
        if response.status_code == 302:
            expected_url = reverse("add_track_to_playlist", 
                                args=[self.user_1.username, self.test_playlist.playlist_name])
            self.assertRedirects(response, expected_url)

    def test_add_streaming_link_to_playlist_negative(self):
        #Login
        self.client.login(email="test1@user.com", password="Meep!234")
        #Create url
        url = reverse("add_streaming_link_to_playlist", args=[self.user_1.username, self.test_playlist.playlist_name])
        #Generate response
        response = self.client.post(url, {
            'playlist_type':"tracks",
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


class DeletePlaylistTest(BaseTestCase):
    def test_unauthorised_user(self):
        #Generate url
        url = reverse("delete_playlists",args=[self.bad_user.username,])

        #Generate response
        response = self.client.delete(
            url,
            data=json.dumps({'playlist_id': [self.test_playlist.id]}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)

    def test_wrong_http_method(self):
        #Login
        self.client.force_login(self.user_1)
        
        #Generate url
        url = reverse("delete_playlists",args=[self.user_1.username])

        #Generate response
        response = self.client.post(
            url,
            data=json.dumps({'playlist_id': [self.test_playlist.id]}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 405)

    def test_delete_playlist_positive(self):
        #Login
        self.client.force_login(self.user_1)
        
        #Generate url
        url = reverse("delete_playlists",args=[self.user_1.username])

        #Generate response
        response = self.client.delete(
            url,
            data=json.dumps({'playlist_id': [self.test_playlist.id]}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        #Retrieve playlist and check is_deleted
        playlist=Playlist.objects.get(id=self.test_playlist.id)
        playlist_is_deleted_status = playlist.is_deleted
        self.assertTrue(playlist_is_deleted_status)

    def test_delete_multiple_playlists_positive(self):
        #Login
        self.client.force_login(self.user_1)

        #Generate url
        url = reverse("delete_playlists", args=[self.user_1.username])

        #Generate response
        response = self.client.delete(
            url,
            data=json.dumps({'playlist_id': [self.test_playlist.id, self.wip_playlist.id]}),
            content_type='application/json'
        )

        #Retrieve playlist and check is_deleted
        playlist=Playlist.objects.get(id=self.wip_playlist.id)
        playlist_is_deleted_status = playlist.is_deleted
        self.assertTrue(playlist_is_deleted_status)

    def test_empty_playlist_ids(self):
        #Login
        self.client.force_login(self.user_1)

        #Generate url
        url = reverse("delete_playlists", args=[self.user_1.username])

        #Generate response
        response = self.client.delete(
            url,
            data=json.dumps({'playlist_id': []}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_user_deletes_other_user_playlist(self):
        #Login
        self.client.force_login(self.bad_user)

        #Generate url
        url = reverse("delete_playlists",args=[self.bad_user.username])

        #Generate response
        response = self.client.delete(
            url,
            data=json.dumps({'playlist_id': [self.wip_playlist.id]}),
            content_type='application/json'
        )

        #Confirm there is no error
        self.assertEqual(response.status_code, 200)

        #Confirm 0 rows updated
        data = json.loads(response.content)
        self.assertEqual(data['deleted_count'], 0)

        #Confirm wip_playlist still exists
        playlist=Playlist.objects.get(id=self.wip_playlist.id)
        playlist_is_deleted_status = playlist.is_deleted
        self.assertFalse(playlist_is_deleted_status)


class DeletePlaylistTracksTest(BaseTestCase):
    def test_unauthorised_user(self):
        #Generate url
        url = reverse("delete_playlist_tracks",args=[self.bad_user.username, self.test_playlist.playlist_name])

        #Generate response
        response = self.client.delete(
            url,
            data=json.dumps({'playlist_track_id': [self.playlist_track_1.id]}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)

    def test_wrong_http_method(self):
        #Login
        self.client.force_login(self.user_1)
        
        #Generate url
        url = reverse("delete_playlist_tracks",args=[self.user_1.username, self.test_playlist.playlist_name])

        #Generate response
        response = self.client.post(
            url,
            data=json.dumps({'playlist_track_id': [self.playlist_track_1.id]}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 405)

    def test_delete_playlist_tracks_positive(self):
        #Login
        self.client.force_login(self.user_1)
        
        #Generate url
        url = reverse("delete_playlist_tracks",args=[self.user_1.username, self.test_playlist.playlist_name])

        #Generate response
        response = self.client.delete(
            url,
            data=json.dumps({'playlist_track_id': [self.playlist_track_1.id]}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        #Retrieve playlist_track and check is_deleted
        playlist_track=PlaylistTrack.objects.get(id=self.playlist_track_1.id)
        playlist_track_is_deleted_status = playlist_track.is_deleted
        self.assertTrue(playlist_track_is_deleted_status)

    def test_delete_multiple_playlist_tracks_positive(self):
        #Login
        self.client.force_login(self.user_1)

        #Generate url
        url = reverse("delete_playlist_tracks",args=[self.user_1.username, self.test_playlist.playlist_name])

        #Generate response
        response = self.client.delete(
            url,
            data=json.dumps({'playlist_track_id': [self.playlist_track_1.id, self.playlist_track_2.id]}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        #Retrieve playlist and check is_deleted
        playlist_track_2=PlaylistTrack.objects.get(id=self.playlist_track_2.id)
        playlist_track_is_deleted_status = playlist_track_2.is_deleted
        self.assertTrue(playlist_track_is_deleted_status)

    def test_empty_playlist_track_ids(self):
        #Login
        self.client.force_login(self.user_1)

        #Generate url
        url = reverse("delete_playlist_tracks",args=[self.user_1.username, self.test_playlist.playlist_name])

        #Generate response
        response = self.client.delete(
            url,
            data=json.dumps({'playlist_track_id': []}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_user_deletes_other_user_playlist_track(self):
        #Login
        self.client.force_login(self.bad_user)

        #Generate url
        url = reverse("delete_playlist_tracks",args=[self.bad_user.username, self.test_playlist.playlist_name])

        #Generate response
        response = self.client.delete(
            url,
            data=json.dumps({'playlist_track_id': [self.playlist_track_1.id]}),
            content_type='application/json'
        )

        #Confirm there is no error
        self.assertEqual(response.status_code, 200)

        #Confirm 0 rows updated
        data = json.loads(response.content)
        self.assertEqual(data['deleted_count'], 0)

        #Confirm wip_playlist still exists
        playlist_track=PlaylistTrack.objects.get(id=self.playlist_track_1.id)
        playlist_track_is_deleted_status = playlist_track.is_deleted
        self.assertFalse(playlist_track_is_deleted_status)


def tearDown(self):
    '''
    Clean up test data.
    '''
    Playlist.objects.all().delete()
    User.objects.all().delete()
    Track.objects.all().delete()
    PlaylistTrack.objects.all().delete()
