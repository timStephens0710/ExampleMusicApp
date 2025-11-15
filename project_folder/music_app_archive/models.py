from django.db import models
from django.db.models import Max
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.conf import settings

import uuid


# Create your models here.
class Playlist(models.Model):
    '''
    The following model contains all of the high-level information regarding the playlists that a user has created.

    #TODO:
        - Consider adding a UUID field for security reasons later on in development.
    '''
    PLAYLIST_TYPES = (
        ('tracks', 'Tracks'),
        ('liked', 'Liked'),
        ('mixes', 'Mixes'),
        ('samples', 'Samples'),
    )

    VISIBILITY_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
    )

    playlist_name = models.CharField(blank=False, null=False, max_length=200)
    slug = models.SlugField(max_length=200, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL
        , on_delete=models.CASCADE
        , related_name='playlists'
        , verbose_name='Playlist Owner'
        )
    playlist_type = models.CharField(
        max_length=50
        , choices=PLAYLIST_TYPES
        , default='tracks'
        , blank=False
        , null=False
        )
    description = models.CharField(max_length=200, blank=True, default='')
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    is_private = models.CharField(
        choices=VISIBILITY_CHOICES
        , blank=False
        , default='public'
        , max_length=10
        , null=False
        )
    is_deleted = models.BooleanField(default=False)

    class Meta:
        #Unique constraints on the table
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'playlist_name'],
                name='unique_owner_playlist_name'
            ),
            models.UniqueConstraint(
                fields=['owner', 'slug'],
                name='unique_owner_slug'
            )
        ]
        #Indexes
        indexes = [
            #User's playlists sorted by date
            models.Index(
                fields=['owner', '-date_created'],
                name='playlist_owner_date_idx'
            ),
            #Public feed discovery
            models.Index(
                fields = ['is_private', 'is_deleted', '-date_created'],
                name='playlist_public_feed_idx'
            )
        ]

        ordering = ['-date_created']
        verbose_name = 'Playlist'
        verbose_name_plural = 'Playlists'


    def save(self, *args, **kwargs):
        """Auto-generate slug from playlist_name if not set"""
        if not self.slug:
            self.slug = slugify(self.playlist_name)
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.playlist_name} by {self.owner.username}"
    

class Track(models.Model):
    '''
    The following model contains all of the low-level information regarding the tracks that a users have posted or added to Playlists.

    It can handle 3 different types:
        - Track
        - Mix
        - Sample

    Uniqueness to be enforced via StreamingLink URLS, not track names, to handle remixes, live versions etc.

    #TODO:
        - Consider adding a field for the cover art
            - That will probably tie in with my future design to only display the cover art.
        - Add track_duration
        - Create a function in a view or the API to handle duplicate track_names + artists        
    '''
    TRACK_TYPE = (
        ('track', 'Track'),
        ('mix', 'Mix'),
        ('sample', 'Sample')
    )    
    
    track_type = models.CharField(choices=TRACK_TYPE, blank=False, null=False, default='track', max_length=20)
    track_name = models.CharField(max_length=250, blank=False, null=False)
    artist = models.CharField(max_length=250, blank=False, null=False)
    album_name = models.CharField(max_length=250, blank=True)
    mix_page =  models.CharField(max_length=250, blank=True)
    record_label = models.CharField(max_length=250, blank=True)
    genre = models.CharField(max_length=250, blank=True)
    purchase_link = models.URLField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tracks_created',
        verbose_name='First Added By'
    )
    date_added = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        #indexes
        indexes = [
            models.Index(
                fields=['track_name', 'artist'],
                name='track_name_artist_idx'
            ),
            models.Index(
                fields=['-date_added'],
                name='track_date_added_idx'
            )        
            ]
        
        ordering = ['-date_added']

    
    def __str__(self):
        return f"{self.track_name} by {self.artist}"


class StreamingLink(models.Model):
    '''
    The following model contains all of the streaming information relating to a track, mix or sample that a user has posted or added to Playlists.

    Refer to PLATFORM_CHOICES for the platforms that are supported.
    '''
    PLATFORM_CHOICES = [
        ('youtube', 'YouTube'),
        ('youtube_music', 'YouTube Music'),
        ('spotify', 'Spotify'),
        ('soundcloud', 'SoundCloud'),
        ('nina', 'Nina'),
        ('bandcamp', 'Bandcamp')
        ]

    track = models.ForeignKey(
        to='Track',
        on_delete=models.PROTECT,
        related_name='streaming_links',
        verbose_name='Streamed on'
        )
    streaming_platform = models.CharField(choices=PLATFORM_CHOICES, max_length=20, blank=False, null=False)
    streaming_link = models.URLField(unique=True, max_length=500, blank=False, null=False)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='streaming_links_added',
        verbose_name='Added By'
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        #Unique constraints on the table
        constraints = [
            models.UniqueConstraint(
                fields=['track', 'streaming_platform'],
                name='unique_track_streaming_platform'
            )
        ]

        verbose_name = 'Streaming Link'
        verbose_name_plural = 'Streaming Links'

    def clean(self):
        '''
        Validate URL matches the selected platform
        '''
        platform_domains = {
            'spotify': ['spotify.com', 'open.spotify.com'],
            'youtube': ['youtube.com'],
            'youtube_music': ['music.youtube.com'],
            'soundcloud': ['soundcloud.com'],
            'bandcamp': ['bandcamp.com'],
            'nina': ['ninaprotocol.com']
        }

        domain_list = platform_domains.get(self.streaming_platform, [])
        if domain_list and not any(domain in self.streaming_link.lower() for domain in domain_list):
            raise ValidationError({
                'streaming_link': f"URL doesn't appear to be from {self.get_streaming_platform_display()}"
            })

    def __str__(self):
        return f"{self.get_streaming_platform_display()} - {self.track.track_name}"


class PlaylistTrack(models.Model):
    '''
    The following model is a junction table between Playlist, Track & User.
    It displays the tracks in a playlist that a user has created. The same track can appear in may different playlists of a user, as well as many different
    playlists from diffferent users. 
    '''
    playlist=models.ForeignKey(
        to='Playlist',
        on_delete=models.CASCADE, #Set to CASCADE because if the user deletes the playlist the Playlist track information is redundant
        blank=False, 
        related_name='tracks_in_playlist',
        verbose_name='Tracks in Playlist'
    )
    track=models.ForeignKey(
        to='Track',
        on_delete=models.CASCADE, #Allow user to delete their own tracks freely.
        related_name='playlist_entries',
        verbose_name='Playlist entries'
    )
    added_by=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, #We want to keep the playlist content despite the fact a user is deleted. This is important for collab playlists.
        null=True,
        blank=True,
        related_name='playlist_tracks_added',
        verbose_name='Playlist Tracks Added'
        )
    position=models.PositiveIntegerField(blank=True, null=True, help_text='Position of track in playlist')
    added_at=models.DateTimeField(auto_now_add=True, editable=False)

    def save(self, *args, **kwargs):
        '''
        Auto incremenent the position based on the playlist id.
        '''
        if self.position is None:
            #Get the maximum position for this playlist
            max_position = PlaylistTrack.objects.filter(playlist=self.playlist).aggregate(Max('position'))['position__max']

            #Set position to max + 1
            self.position = (max_position or 0) + 1
        
        super().save(*args, **kwargs)


    class Meta:
        #Unique constraints
        constraints = [
            models.UniqueConstraint(
                fields=['playlist', 'track'], #the same track cannot be added twice to same playlist
                name='unique_playlist_track'
            ),
            models.UniqueConstraint(
                fields=['playlist', 'position'],
                name='unique_playlist_position'
            )
            ]
        
        #indexes
        indexes = [
                models.Index(
                    fields=['playlist', 'position'],
                    name='playlist_position_idx'
                ),
                models.Index(
                    fields=['track'], #We want the user's to search within their playlists.
                    name='track_idx'
                )            
                ]

        ordering = ['playlist', 'position']

    def __str__(self):
        return f"{self.playlist_id} - {self.track_id} @ {self.position}"