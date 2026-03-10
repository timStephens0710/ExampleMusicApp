/*
    This is the staging model for the Tracks model.

    It will be referenced in the following mart model:
        - mart_purchase_links
        - mart_track_type
        - mart_summary_stats
*/

SELECT "id"::INTEGER AS id,
       "track_type"::VARCHAR AS track_type,
       "purchase_link"::VARCHAR AS purchase_link
FROM {{ source('raw', 'music_app_archive_track')}}