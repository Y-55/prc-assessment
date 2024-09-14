{{
    config(
        materialized='materialized_view',
        engine='ReplacingMergeTree(version, deleted)',
        primary_key='assumeNotNull(id)',
        order_by='assumeNotNull(id)'
    )
}}

WITH delete_ops AS (
    SELECT
        toInt64((before_id)) AS id,
        hacker_news_log.before_text AS text,
        hacker_news_log.before_counter AS counter,
        hacker_news_log.before_state AS state,
        hacker_news_log.before_created_at AS created_at,
        hacker_news_log.before_updated_at AS updated_at,
        hacker_news_log.ts_ms AS version,
        1 AS deleted,
        hacker_news_log.before_age AS age, --age
        hacker_news_log.before_duration AS duration --dur
    FROM 
        {{ ref('hacker_news_log') }}
    WHERE 
        hacker_news_log.op IN ('d')
),

add_ops AS (
    SELECT
        toInt64((after_id)) AS id,
        hacker_news_log.after_text AS text,
        hacker_news_log.after_counter AS counter,
        hacker_news_log.after_state AS state,
        hacker_news_log.after_created_at AS created_at,
        hacker_news_log.after_updated_at AS updated_at,
        hacker_news_log.ts_ms AS version,
        0 AS deleted,
        hacker_news_log.after_age AS age, --age
        hacker_news_log.after_duration AS duration --dur
    FROM 
        {{ ref('hacker_news_log') }}
    WHERE 
        hacker_news_log.op IN ('c', 'u')
),

final AS (
    SELECT
        coalesce(delete_ops.id, add_ops.id) AS id,
        coalesce(delete_ops.text, add_ops.text) AS text,
        coalesce(delete_ops.counter, add_ops.counter) AS counter,
        coalesce(delete_ops.state, add_ops.state) AS state,
        coalesce(delete_ops.created_at, add_ops.created_at) AS created_at,
        coalesce(delete_ops.updated_at, add_ops.updated_at) AS updated_at,
        coalesce(nullIf(delete_ops.version, 0), add_ops.version) AS version,
        coalesce(delete_ops.deleted, add_ops.deleted) AS deleted,
        coalesce(delete_ops.age, add_ops.age) AS age,
        coalesce(delete_ops.duration, add_ops.duration) AS duration
    FROM
        delete_ops
        FULL OUTER JOIN add_ops ON delete_ops.id = add_ops.id
)

SELECT * FROM final