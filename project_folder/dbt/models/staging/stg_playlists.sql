/*
    This is the staging model for the Playlist model.

    It will be referenced in the following mart model:
        - mart_summary_totals
        - mart_breakdown_playlist_type
        - mart_breakdown_is_private
*/

SELECT id,
       playlist_type,
       is_private
FROM {{ source('raw', 'playlists')}}