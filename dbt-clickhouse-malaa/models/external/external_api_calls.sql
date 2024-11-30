{{
    config(
        materialized='view',
        order_by='id',
        primary_key='id'
    )
}}

SELECT
    1 AS id