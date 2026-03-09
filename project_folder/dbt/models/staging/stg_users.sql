/*
    This is the staging model for the CustomUser model.

    It will be referenced in the following mart model:
        - mart_summary_stats.sql
*/

SELECT id,
       username,
       is_active
FROM {{ source('raw', 'customuser')}}