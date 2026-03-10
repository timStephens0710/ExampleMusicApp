/*
    This is the staging model for the Playlist model.

    It will be referenced in the following mart model:
        - mart_summary_stats
        - mart_breakdown_playlist_type
        - mart_breakdown_is_private
*/
SELECT
    "id"::INTEGER AS id,
    "playlist_type"::VARCHAR AS playlist_type,
    "is_private"::VARCHAR AS is_private,
    "is_deleted"::BOOLEAN AS is_deleted
FROM {{ source('raw', 'music_app_archive_playlist') }}