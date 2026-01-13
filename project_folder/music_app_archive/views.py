from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError, transaction


from .models import *
from music_app_auth.models import AppLogging
from .forms import *
from .src.integrations.main_integrations import orchestrate_platform_api
from .src.custom_exceptions import BandCampMetaDataError, YouTubeMetaDataError

from music_app_auth.models import CustomUser
from music_app_auth.src.django_error_utils import handle_django_error
from music_app_auth.src.custom_exceptions import *


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@login_required
def user_profile(request, username):
    #get username from user_id
    user = get_object_or_404(CustomUser, username=username)

    context = {
        'profile_user': user,
        'username': username
    }
    return render(request, 'user_profile.html', context)


@login_required
def user_playlists(request, username):
    '''
    This view displays all of the playlists that a user has created or collaborated on. 
    '''
    #Retrieve the user        
    user = get_object_or_404(CustomUser, username=username)

    #Display the runs from the 'Playlist' model.
    user_playlists = Playlist.objects.filter(
        owner_id=user.id,
        is_deleted=False
        ).order_by('-date_created')

    context = {
        'title': 'Playlists',
        'user_playlists': user_playlists
    }

    return render(request, 'user_playlists.html', context=context)


@login_required
def create_playlist(request, username):
    '''
    Form that allows the user to create a playlist. Once they've completed the form they are redirecte to the view \
    'add_track_to_playlist' where they can begin adding in tracks, mixes or samples
    '''
    #Get relevant user
    user = get_object_or_404(CustomUser, username=username)

    #Security check: ensure logged-in user matches username
    if request.user != user:
        logger.warning(f"User {request.user.username} tried to create playlist for {username}")
        messages.error(request, "You can only create playlists for yourself")
        return redirect('user_profile', username=request.user.username)
    
    #Get user_id
    user_id = user.id

    #Initialise the CreatePlaylistForm
    create_playlist_form = CreatePlaylist()

    if request.method == 'POST':
        create_playlist_form = CreatePlaylist(request.POST)
        if create_playlist_form.is_valid():
            try:
                new_playlist = create_playlist_form.save(commit=False)

                #Set owner of Playlist
                new_playlist.owner = user

                #Get Playlist name
                playlist_name = new_playlist.playlist_name
                
                #Save the form
                new_playlist.save()

                #Add logging
                log_text = f'User has created playlist: {new_playlist.playlist_name}'
                AppLogging.objects.create(user_id = user_id, log_text=log_text)

                context = {
                    'user': user
                    ,'username': username
                    ,'playlist_name': playlist_name
                }

                return HttpResponseRedirect(reverse(viewname='add_streaming_link_to_playlist', args=[username, playlist_name]), context)
            except IntegrityError as e:
                #Duplicate playlist name (unique constraint violation)
                logger.warning(f"Duplicate playlist name '{new_playlist.playlist_name}' for user {username}: {e}")
                messages.error(request, f"You already have a playlist named '{new_playlist.playlist_name}'")
                
                context = {
                    'profile_user': user,
                    'username': username,
                    'form': create_playlist_form
                }
                return render(request, 'create_playlist.html', context)
            except Exception as e:
                #Unexpected database error
                logger.exception(f"Unexpected error creating playlist for {username}: {e}")
                messages.error(request, "An error occurred while creating your playlist. Please try again.")
                
                context = {
                    'profile_user': user,
                    'username': username,
                    'form': create_playlist_form
                }
                return render(request, 'create_playlist.html', context)
        else:
            create_playlist_form
            context = {
                'profile_user': user,
                'username': username,
                'form': create_playlist_form
            }
            return render(request, 'create_playlist.html', context)
          
    #Show empty form
    create_playlist_form = CreatePlaylist()
    context = {
        'profile_user': user,
        'username': username,
        'form': create_playlist_form
    }
    return render(request, 'create_playlist.html', context)

@login_required
def add_streaming_link_to_playlist(request, username, playlist_name):
    '''
    Steps:
        1. Initialize AddStreamingLink() form
        2. Check if POST is valid 
        3. call URL in the youtube API
        4. Retrive the relevant information to pre-fill the AddTrackToPlaylist & AddStreamingLinkToTrack forms
        5. Re-direc to add_track_to_playlist(request, username, playlist_name)
            - May have to 
    '''
    #Get user instance via username
    user = get_object_or_404(CustomUser, username=username)

    #Security check: ensure logged-in user matches username
    if request.user != user:
        logger.warning(f"User {request.user.username} tried to add link to {username}'s playlist")
        messages.error(request, "You can only add tracks to your own playlists")
        return redirect('user_playlists', username=request.user.username)
    
    #Get relevant user_id
    user_id = user.id

    #Initialise forms
    add_streaming_link_to_playlist_form = AddStreamingLink()

    #Verify playlist exists and belongs to user
    try:
        playlist = Playlist.objects.get(playlist_name=playlist_name, owner=user, is_deleted=False)
    except Playlist.DoesNotExist:
        logger.warning(f"Playlist '{playlist_name}' not found for user {username}")
        messages.error(request, f"Playlist '{playlist_name}' not found")
        return redirect('user_playlists', username=username)

    #AddStreamingLink() form
    if request.method== 'POST':
        add_streaming_link_to_playlist_form = AddStreamingLink(request.POST)
        #Check if both forms are valid
        if add_streaming_link_to_playlist_form.is_valid():
            #Add logging here
            log_text = f"{user.username} has submitted a streaming link"
            AppLogging.objects.create(user_id = user_id, log_text=log_text)

            #Retrieve data from form link
            track_type=add_streaming_link_to_playlist_form.cleaned_data['track_type']
            streaming_link=add_streaming_link_to_playlist_form.cleaned_data['streaming_link']
            try:
                #Generate Meta Data Dictionary
                meta_data_dict = orchestrate_platform_api(streaming_link, track_type)

                #Store meta_data_dict in session
                request.session["meta_data_dict"] = meta_data_dict 

                return HttpResponseRedirect(reverse(viewname='add_track_to_playlist', args=[username, playlist_name]))
            except (YouTubeMetaDataError, BandCampMetaDataError) as e:
                #Platform-specific API error
                logger.warning(f"Platform API error for {streaming_link}: {str(e)}")
                messages.warning(
                    request,
                    f"Could not fetch metadata: {str(e)}. Please enter track details manually."
                )
                
                #Store minimal metadata for manual entry
                request.session['meta_data_dict'] = {
                    'track_type': track_type,
                    'streaming_link': streaming_link,
                    'streaming_platform': 'unknown',
                    'track_name': '',
                    'artist': '',
                    'album_name': '',
                    'mix_page': '',
                    'record_label': '',
                    'genre': '',
                    'purchase_link': ''
                }        
                return redirect('add_track_to_playlist', username=username, playlist_name=playlist_name)
            except ValueError as e:
               #Invalid URL or unsupported platform
                logger.warning(f"Invalid URL submitted by {username}: {streaming_link} - {str(e)}")
                messages.error(request, str(e))
                
                context = {
                    'username': username,
                    'playlist_name': playlist_name,
                    'playlist': playlist,
                    'add_streaming_link_to_playlist_form': add_streaming_link_to_playlist_form,
                }
                return render(request, 'add_link.html', context)
            except Exception as e:
                # Unexpected error
                logger.exception(f"Unexpected error fetching metadata for {streaming_link}: {e}")
                messages.error(request, "An unexpected error occurred. Please try again.")
                
                context = {
                    'username': username,
                    'playlist_name': playlist_name,
                    'playlist': playlist,
                    'add_streaming_link_to_playlist_form': add_streaming_link_to_playlist_form,
                }
                return render(request, 'add_link.html', context)
        else:
            #Form has failed the validation
            logger.debug(f"Invalid streaming link form by {username}: {add_streaming_link_to_playlist_form.errors}")
            messages.warning(request, "Please correct the errors below")
            
            context = {
                'username': username,
                'playlist_name': playlist_name,
                'playlist': playlist,
                'add_streaming_link_to_playlist_form': add_streaming_link_to_playlist_form,
            }
            return render(request, 'add_link.html', context)
    
    #Generate empty form
    add_streaming_link_to_playlist_form = AddStreamingLink()
    context = {
        'username': username,
        'playlist_name': playlist_name,
        'playlist': playlist,
        'add_streaming_link_to_playlist_form': add_streaming_link_to_playlist_form,
    }
    return render(request, 'add_link.html', context)


@login_required
def add_track_to_playlist(request, username, playlist_name):
    '''
    This form update the Track and StreamingLink models.
        - The Track & StreamingLink model can be updated here
            - The other place is when a user posts (to come later on)
    '''
    #Get user instance via username
    user = get_object_or_404(CustomUser, username=username)
    #Security check: ensure logged-in user matches username
    if request.user != user:
        logger.warning(f"User {request.user.username} tried to add track to {username}'s playlist")
        messages.error(request, "You can only add tracks to your own playlists")
        return redirect('user_playlists', username=request.user.username)
    #Get relevant user_id
    user_id = user.id

    #Get playlist instance
    playlist = get_object_or_404(Playlist, playlist_name=playlist_name, owner=user, is_deleted=False)

    #Get youtube_meta_data_dict
    meta_data_dict = request.session.get("meta_data_dict")

    if not meta_data_dict:
        logger.warning(f"No metadata in session for {username}/{playlist_name}")
        messages.warning(request, "No track data found. Please submit a streaming link first.")
        return redirect('add_streaming_link_to_playlist', username=username, playlist_name=playlist_name)

    #Initialise forms and pre-fill with youtube_meta_data_dict
    add_track_to_playlist_form = AddTrackToPlaylist(
        initial={
            'track_type': meta_data_dict.get("track_type"),
            'track_name': meta_data_dict.get("track_name"),
            'artist': meta_data_dict.get("artist"),
            'album_name': meta_data_dict.get("album_name"),
            'mix_page': meta_data_dict.get("mix_page"),
            'record_label': meta_data_dict.get("record_label"),
            'genre': meta_data_dict.get("genre"),
            'purchase_link': meta_data_dict.get("purchase_link"),
            }
        )
    
    add_streaming_link_to_track_form = AddStreamingLinkToTrack(
            initial={
            'streaming_platform': meta_data_dict.get("streaming_platform"),
            'streaming_link': meta_data_dict.get("streaming_link")
            }
        )

    #AddStreamingLinkToTrack() form
    if request.method== 'POST':
        add_track_to_playlist_form = AddTrackToPlaylist(request.POST)
        add_streaming_link_to_track_form = AddStreamingLinkToTrack(request.POST)
        #Check if both forms are valid
        if add_track_to_playlist_form.is_valid() and add_streaming_link_to_track_form.is_valid():
            try:
                with transaction.atomic():
                    #Save track
                    new_track = add_track_to_playlist_form.save(commit=False)
                    #Set created_by to Track
                    new_track.created_by = user
                    new_track.save()
                    logger.info(f"Created track: {new_track.track_name} by {new_track.artist}")

                    #Add corresponding streaming link
                    new_streaming_link = add_streaming_link_to_track_form.save(commit=False)
                    #Add Track to Track
                    new_streaming_link.track = new_track
                    #Set created_by to Track
                    new_streaming_link.added_by = user
                    new_streaming_link.save()
                    logger.info(f"Created streaming link: {new_streaming_link.streaming_platform}")

                    #Create instance in PlaylistTrack model
                    PlaylistTrack.objects.create(
                        playlist=playlist,
                        track=new_track,
                        added_by=user
                    )

                    #Add logging here
                    log_text = f'{user.username} has added the following track "{new_track.track_name}" to {playlist.playlist_name}'
                    AppLogging.objects.create(user_id = user_id, log_text=log_text)

                   #Clear session data
                    if 'meta_data_dict' in request.session:
                        del request.session['meta_data_dict']

                    return redirect(reverse(viewname='view_edit_playlist', args=[username, playlist_name]))
            except IntegrityError as e:
                #Duplicate track or streaming link
                logger.warning(f"Integrity error adding track to {playlist_name}: {str(e)}")
                
                #Check if it's a duplicate streaming link
                if 'streaming_link' in str(e).lower() or 'unique' in str(e).lower():
                    messages.error(
                        request,
                        "This track is already in your library. Each streaming link can only be added once."
                    )
                else:
                    messages.error(
                        request,
                        "This track/link combination already exists. Please use a different link."
                    )
                
                #Re-render form with data
                context = {
                    'username': username,
                    'playlist_name': playlist_name,
                    'playlist': playlist,
                    'add_track_to_playlist_form': add_track_to_playlist_form,
                    'add_streaming_link_to_track_form': add_streaming_link_to_track_form
                }
                return render(request, 'add_track.html', context)
            except Exception as e:
                # Unexpected database error
                logger.exception(f"Unexpected error adding track to {playlist_name}: {e}")
                messages.error(request, "An error occurred while saving the track. Please try again.")
                
                context = {
                    'username': username,
                    'playlist_name': playlist_name,
                    'playlist': playlist,
                    'add_track_to_playlist_form': add_track_to_playlist_form,
                    'add_streaming_link_to_track_form': add_streaming_link_to_track_form
                }
                return render(request, 'add_track.html', context)
        else:
            #Form has failed validation
            logger.debug(f"Invalid track forms by {username}: Track errors: {add_track_to_playlist_form.errors}, Link errors: {add_streaming_link_to_track_form.errors}")
            messages.warning(request, "Please correct the errors below")
            
            context = {
                'username': username,
                'playlist_name': playlist_name,
                'playlist': playlist,
                'add_track_to_playlist_form': add_track_to_playlist_form,
                'add_streaming_link_to_track_form': add_streaming_link_to_track_form
            }
            return render(request, 'add_track.html', context)
    #Initialize forms with metadata from session
    add_track_to_playlist_form = AddTrackToPlaylist(
        initial={
            'track_type': meta_data_dict.get('track_type'),
            'track_name': meta_data_dict.get('track_name'),
            'artist': meta_data_dict.get('artist'),
            'album_name': meta_data_dict.get('album_name'),
            'mix_page': meta_data_dict.get('mix_page'),
            'record_label': meta_data_dict.get('record_label'),
            'genre': meta_data_dict.get('genre'),
            'purchase_link': meta_data_dict.get('purchase_link'),
        }
    )
    
    add_streaming_link_to_track_form = AddStreamingLinkToTrack(
        initial={
            'streaming_platform': meta_data_dict.get('streaming_platform'),
            'streaming_link': meta_data_dict.get('streaming_link')
        }
    )
    
    context = {
        'username': username,
        'playlist_name': playlist_name,
        'playlist': playlist,
        'add_track_to_playlist_form': add_track_to_playlist_form,
        'add_streaming_link_to_track_form': add_streaming_link_to_track_form,
        'metadata_source': meta_data_dict.get('streaming_platform', 'manual')
    }
    return render(request, 'add_track.html', context)
    

@login_required
def view_edit_playlist(request, username, playlist_name):
    '''
    Displays a specific playlist for a user, where they can edit.
    '''
    #Get user instance via username
    user = get_object_or_404(CustomUser, username=username)
    #Security check: ensure logged-in user matches username
    if request.user != user:
        logger.warning(f"User {request.user.username} tried to view playlist: {playlist_name}")
        messages.error(request, "You can only view to your own playlists")
        return redirect('user_playlists', username=request.user.username)
    #Get relevant user_id
    user_id = user.id

    #Get relevant playlist
    playlist = get_object_or_404(
        Playlist.objects.select_related('owner')
        , playlist_name=playlist_name
        , owner = user
        , is_deleted = False
        )

    #2. Get relevant PlaylistTrack from the model, along with Track + StreamingLink meta data
    playlist_tracks = PlaylistTrack.objects.filter(
        playlist=playlist
        ).select_related(
            'track',
            'added_by'
        ).prefetch_related(
            'track__streaming_links'
        ).order_by('position')
    
    #3. Build list for track data
    list_of_tracks = []

    for playlist_track in playlist_tracks:
        try:
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

            #Append track_data to list_of_tracks
            list_of_tracks.append(track_data)
        except Exception as e:
            #Skip current track and move onto the next one
            logger.error(f"Error processing track in playlist {playlist_name}: {e}")
            continue
    
    context = {
        'user_id': user_id,
        'username': username, 
        'playlist_name': playlist_name,
        'list_of_tracks': list_of_tracks
    }
    return render(request, 'view_edit_playlist.html', context)

