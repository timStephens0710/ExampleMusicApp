from django.shortcuts import get_object_or_404

from ..models import Playlist


def get_playlist(playlist_name, user):
    '''
    Retrieve instance from Playlist model, based on playlist_name and
    '''
    playlist = get_object_or_404(
            Playlist.objects.select_related('owner')
            , playlist_name=playlist_name
            , owner = user
            )
    return playlist


def get_playlist_tracks(playlist) -> list:
    '''
    Retrieve all tracks in a playlist with their streaming links.
    
    Args:
        playlist: Playlist instance
        
    Returns:
        List of dictionaries with track data and streaming links
    '''
    from ..models import PlaylistTrack

    #1. Get relevant PlaylistTrack from the model, along with Track + StreamingLink meta data
    playlist_tracks = PlaylistTrack.objects.filter(
        playlist=playlist
        ).select_related(
            'track',
            'added_by'
        ).prefetch_related(
            'track__streaming_links'
        ).order_by('position')
    
    #2. Create empty list
    list_of_tracks = []

    #3. Build list for track data
    for playlist_track in playlist_tracks:
        track = playlist_track.track

        #Get streaming_links for specific track
        streaming_links = list(track.streaming_links.all())

        #Create dictionary to pass through context
        track_data = {
            'position': playlist_track.position,
            'track_id': track.id,
            'track_name': track.track_name,
            'artist': track.artist,
            'album_name': track.album_name or '-',
            'genre': track.genre or '-',
            'record_label': track.record_label or '-',
            'mix_page': track.mix_page or '-',
            'date_added': playlist_track.added_at,
            'added_by': playlist_track.added_by.username if playlist_track.added_by else 'Unknown',
            'streaming_links': [
                {
                    'platform': link.get_streaming_platform_display(),
                    'platform_code': link.streaming_platform,
                    'url': link.streaming_link,
                    'id': link.id
                }
                for link in streaming_links
            ],
            # For backward compatibility with your template
            'streaming_platform': streaming_links[0].get_streaming_platform_display() if streaming_links else '-',
            'link': streaming_links[0].streaming_link if streaming_links else '#',
        }

        #4. Append track_data to list_of_tracks
        list_of_tracks.append(track_data)

        return list_of_tracks
