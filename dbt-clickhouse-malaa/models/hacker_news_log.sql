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
        hacker_news_queue.ts_ms AS ts_ms,
        multiIf(before IS NULL, 'c', after IS NULL, 'd', 'u') AS op,
        JSONExtract(before, 'id', 'Nullable(String)') AS before_id,
        JSONExtract(before, 'text', 'Nullable(String)') AS before_text,
        JSONExtract(before, 'counter', 'Nullable(String)') AS before_counter,
        JSONExtract(before, 'state', 'Nullable(String)') AS before_state,
        JSONExtract(before, 'created_at', 'Nullable(String)') AS before_created_at,
        JSONExtract(before, 'updated_at', 'Nullable(String)') AS before_updated_at,
        JSONExtract(after, 'id', 'Nullable(String)') AS after_id,
        JSONExtract(after, 'text', 'Nullable(String)') AS after_text,
        JSONExtract(after, 'counter', 'Nullable(String)') AS after_counter,
        JSONExtract(after, 'state', 'Nullable(String)') AS after_state,
        JSONExtract(after, 'created_at', 'Nullable(String)') AS after_created_at,
        JSONExtract(after, 'updated_at', 'Nullable(String)') AS after_updated_at
    FROM 
        {{ source('default', 'hacker_news_queue') }}
)

SELECT * FROM final