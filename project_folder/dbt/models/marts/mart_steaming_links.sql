{{ config(
    materialized='incremental',
    unique_key='streaming_link_id'
)}}

/*
    This mart is an incremental model that provides a breakdown by streaming platform.
    I chose it to be incremental because every time a user shares a new track they will 
    add a corresponding streaming link. This means we only need to process new records 
    since the last run rather than rebuilding the entire table every time.
*/

WITH new_streaming_links AS (
    SELECT *
    FROM {{ ref('stg_streaming_links') }}
    {% if is_incremental() %}
    WHERE created_at > (SELECT MAX(created_at) FROM {{ this }})
    {% endif %}
)

SELECT streaming_platform
      ,COUNT(*) AS total_count
FROM new_streaming_links
GROUP BY streaming_platform