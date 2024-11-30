{{
    config(
        materialized='materialized_view',
        engine='ReplacingMergeTree(version, deleted)',
        primary_key='assumeNotNull(id)',
        order_by='assumeNotNull(id)'
    )
}}

--mv_add:begin
SELECT
        toInt64((after_id)) AS id,
        hacker_news_log.after_text AS text,
        hacker_news_log.after_counter AS counter,
        hacker_news_log.after_state AS state2,
        hacker_news_log.after_created_at AS created_at,
        hacker_news_log.after_updated_at AS updated_at,
        hacker_news_log.ts_ms AS version,
        0 AS deleted
    FROM 
        {{ ref('hacker_news_log') }}
    WHERE 
        hacker_news_log.op IN ('c', 'u')
--mv_add:end

UNION ALL

--mv_del:begin
    SELECT
        toInt64((before_id)) AS id,
        hacker_news_log.before_text AS text,
        hacker_news_log.before_counter AS counter,
        hacker_news_log.before_state AS state2,
        hacker_news_log.before_created_at AS created_at,
        hacker_news_log.before_updated_at AS updated_at,
        hacker_news_log.ts_ms AS version,
        1 AS deleted
    FROM 
        {{ ref('hacker_news_log') }}
    WHERE 
        hacker_news_log.op IN ('d')
--mv_del:end