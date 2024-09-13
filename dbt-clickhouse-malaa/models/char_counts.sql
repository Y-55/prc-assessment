{{
    config(
        materialized='materialized_view',
        order_by='char_',
        engine='SummingMergeTree(count)',
        primary_key='char_'
    )
}}

WITH delete_ops AS (
    SELECT
        arrayJoin(ngrams(ifNull(before_text, ''), 1)) AS char_,
        toInt64(count(*) * -1) AS count
    FROM
        hacker_news_log
    WHERE
        op IN ('d', 'u')
    GROUP BY
        char_
),

add_ops AS (
    SELECT
        arrayJoin(ngrams(ifNull(after_text, ''), 1)) AS char_,
        toInt64(count(*)) AS count
    FROM
        hacker_news_log
    WHERE
        op IN ('c', 'u')
    GROUP BY
        char_
),

final AS (
    SELECT
        assumeNotNull(coalesce(nullIf(delete_ops.char_, ''), nullIf(add_ops.char_,''))) AS char_,
        delete_ops.count + add_ops.count AS count
    FROM
        delete_ops
        FULL OUTER JOIN add_ops ON delete_ops.char_ = add_ops.char_
)

SELECT * FROM final
