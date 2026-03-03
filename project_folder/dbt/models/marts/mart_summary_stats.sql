/*
    This mart provides the following summary stats:
        - total users
        - total playlists
        - total tracks
*/
WITH CTE_TOTAL_USERS AS (
    SELECT 'Total Users' AS summary_metric
            ,COUNT(*) AS total_count
    FROM {{ ref('stg_users') }}
    WHERE is_active = 1
)
, CTE_TOTAL_PLAYLISTS AS (
    SELECT 'Total Playlists' AS summary_metric
        ,COUNT(*) AS total_count
    FROM {{ ref('stg_playlists') }}
)
, CTE_TOTAL_TRACKS AS (
    SELECT 'Total Tracks' AS summary_metric
        ,COUNT(*) AS total_count
    FROM {{ ref('stg_tracks') }}
    WHERE track_type = 'track'
)

SELECT *
FROM CTE_TOTAL_USERS
UNION ALL 
SELECT *
FROM CTE_TOTAL_PLAYLISTS
UNION ALL 
SELECT *
FROM CTE_TOTAL_TRACKS
