/*
    This mart provides a breakdown of the playlists by:
        - TYPE
*/
SELECT "playlist_type" 
      ,COUNT(*) as total_count
FROM {{ ref('stg_playlists') }}
group by "playlist_type"