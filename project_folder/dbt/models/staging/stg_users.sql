/*
    This is the staging model for the CustomUser model.

    It will be referenced in the following mart model:
        - mart_summary_stats.sql
*/

SELECT "id"::INTEGER AS id,
       "username"::VARCHAR AS playlist_type,
       "is_active"::BOOLEAN AS is_active
FROM {{ source('raw', 'music_app_auth_customuser')}}