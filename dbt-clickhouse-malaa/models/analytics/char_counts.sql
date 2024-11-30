{{
    config(
        materialized='materialized_view',
        order_by='char_',
        engine='SummingMergeTree(count)',
        primary_key='char_'
    )
}}

--mv_del:begin
    SELECT
        arrayJoin(ngrams(ifNull(before_text, ''), 1)) AS char_,
        toInt64(count(*) * -1) AS count
    FROM
        {{ ref('hacker_news_log') }}
    WHERE
        op IN ('d', 'u')
    GROUP BY
        char_
--mv_del:end

UNION ALL

--mv_add:begin
    SELECT
        arrayJoin(ngrams(ifNull(after_text, ''), 1)) AS char_,
        toInt64(count(*)) AS count
    FROM
        {{ ref('hacker_news_log') }}
    WHERE
        op IN ('c', 'u')
    GROUP BY
        char_
--mv_add:end
