/*
    This mart provides a breakdown of the playlists by:
        - Visibility (Private vs Public)

*/
WITH CTE_PLAYLIST_VISIBILITY AS (
    SELECT
        id,
        is_private,
        CASE
            WHEN is_private = 'private' THEN 'Private'
            ELSE 'Public'
        END AS playlist_visibility
    FROM {{ ref('stg_playlists') }}
    WHERE is_deleted = FALSE
)

SELECT playlist_visibility, COUNT(*) AS total_count
FROM CTE_PLAYLIST_VISIBILITY
group by playlist_visibility