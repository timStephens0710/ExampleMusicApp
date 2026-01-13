from django import forms
from django.core import exceptions
from django.forms import ModelForm

from .models import Playlist, Track, StreamingLink
from .src.utils import check_streaming_link_platform


class CreatePlaylist(ModelForm):
    '''
    The following form class represents how a user creates/updates a specific playlist.

    Models + Fields required:
        - Playlist:
            - playlist_name
            - playlist_type
            - description
            - is_private
    '''
    class Meta:
        model = Playlist
        fields = (
            'playlist_name',
            'playlist_type',
            'description',
            'is_private'
        )

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)

        playlist_type_choices = list(self.fields['playlist_type'].choices)
        playlist_type_choices.remove(('liked', 'Liked'))
        self.fields['playlist_type'].choices = playlist_type_choices


class AddStreamingLink(forms.Form):
    '''
    Form for the API.
    '''
    TRACK_TYPE = (
        ('track', 'Track'),
        ('mix', 'Mix'),
        ('sample', 'Sample')
    )

    PLATFORM_CHOICES = [
        ('youtube', 'YouTube'),
        ('youtube_music', 'YouTube Music'),
        ('bandcamp', 'Bandcamp'),
    ]

    track_type = forms.ChoiceField(choices=TRACK_TYPE, label='Type')
    streaming_link = forms.CharField(label='Link', max_length=500)

    def clean_streaming_link(self):
        url = self.cleaned_data['streaming_link']
        
        platform = check_streaming_link_platform(url)
        
        if not platform:
            raise forms.ValidationError(
                "URL must be from YouTube or Bandcamp"
            )
        return url


class AddTrackToPlaylist(ModelForm):
    '''
    The following form 
    Track fields required:
        - track_type
        - track_name
        - artist
        - album_name
        - mix_page
        - record_label
        - genre
        - purchase_link

    Validator:
        - If the user creates a playlist_type == 'track', then 
    '''
    class Meta:
        model = Track
        fields = (
            'track_type',
            'track_name',
            'artist',
            'album_name',
            'mix_page',
            'record_label',
            'genre',            
            'purchase_link'
        )


class AddStreamingLinkToTrack(ModelForm):
    '''
    The following form 

    StreamingLink fields required:
        - streaming_platform
        - streaming_link  
    '''
    class Meta:
        model = StreamingLink
        fields = (
            'streaming_platform',
            'streaming_link'
        ) 