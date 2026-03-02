/*
    This is the staging model for the Tracks model.

    It will be referenced in the following mart model:
        - mart_xxxx

*/

SELECT id,
       track_type,
       purchase_link
FROM {{ source('raw', 'tracks')}}