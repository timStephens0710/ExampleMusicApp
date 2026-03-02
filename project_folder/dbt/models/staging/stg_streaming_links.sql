/*
    This is the staging model for the StreamingLink model.

    It will be referenced in the following mart model:
        - mart_xxxx

*/

SELECT id,
       streaming_platform
FROM {{ source('raw', 'streaming_links')}} --streaminglink