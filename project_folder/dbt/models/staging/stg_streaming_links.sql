/*
    This is the staging model for the StreamingLink model.

    It will be referenced in the following mart model:
        - mart_streaming_links.sql
        - mart_summary_stats.sql
*/

SELECT id,
       streaming_platform,
       created_at
FROM {{ source('raw', 'streaming_links')}} --streaminglink