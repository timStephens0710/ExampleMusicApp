/*
    This mart provides a breakdown by streaming link platform
*/
SELECT "streaming_platform"
      ,COUNT(*) AS total_count
FROM {{ ref('stg_streaming_links') }}
group by "streaming_platform"