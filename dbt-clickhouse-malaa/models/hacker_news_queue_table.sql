{{
    config(
        materialized='materialized_view',
        engine='MergeTree',
        order_by='ts_ms',
        primary_key='ts_ms'
    )
}}

WITH final AS (
    SELECT
        *
    FROM 
        {{ source('default', 'hacker_news_queue') }}
)

SELECT * FROM final