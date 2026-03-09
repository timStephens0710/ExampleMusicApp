/*
    This mart provides an insight into how many tracks that have been posted contain a purchase link.
*/
WITH CTE_TRACKS AS (
    SELECT 
        COUNT(*) AS total_tracks,
        COUNT(CASE WHEN "purchase_link" IS NOT NULL THEN 1 END) AS total_with_purchase_link
    FROM {{ ref('stg_tracks') }}
    WHERE "track_type" = 'track'
)

SELECT 
    total_tracks
    , total_with_purchase_link 
    , CAST(total_with_purchase_link / total_tracks AS DECIMAL(18, 2)) AS purchase_track_ratio
FROM CTE_TRACKS