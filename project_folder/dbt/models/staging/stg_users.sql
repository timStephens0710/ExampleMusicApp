/*
    This is the staging model for the CustomUser model.

    It will be referenced in the following mart model:
        - mart_xxxx

*/

SELECT id,
       email,
       is_active
FROM {{ source('raw', 'users')}} --customuser