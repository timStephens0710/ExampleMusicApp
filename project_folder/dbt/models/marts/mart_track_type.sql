/*
    This mart provides a breakdown by track type
*/
SELECT track_type 
      ,COUNT(*) AS total_count
FROM {{ ref('stg_tracks') }}
GROUP BY track_type
