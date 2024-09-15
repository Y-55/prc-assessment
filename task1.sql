-- solution 1
CREATE TABLE default.char_counts
(
    `char_` String,
    `count` Int64
)
ENGINE = SummingMergeTree(count)
PRIMARY KEY char_
ORDER BY (char_);

CREATE MATERIALIZED VIEW add_char_counts_mv TO char_counts AS (
	SELECT
    	arrayJoin(ngrams(ifNull(after_text, ''), 1)) AS char_,
    	toInt64(count(*)) AS count
	FROM
		hacker_news_log
	WHERE
		op IN ('c', 'u')
	GROUP BY
		char_
);

CREATE MATERIALIZED VIEW del_char_counts_mv TO char_counts AS (
	SELECT
    	arrayJoin(ngrams(ifNull(before_text, ''), 1)) AS char_,
    	toInt64(count(*) * -1) AS count
	FROM
		hacker_news_log
	WHERE
		op IN ('d', 'u')
	GROUP BY
		char_
);

-- this solution is strait forward and doesn't need any cmvao


-- solution 2
CREATE TABLE default.char_counts
(
    `char_` String,
    `count` Int64
)
ENGINE = SummingMergeTree(count)
PRIMARY KEY char_
ORDER BY (char_);

CREATE MATERIALIZED VIEW default.char_counts_mv TO default.char_counts
(
    `char_` String,
    `count` Int64
)
AS WITH
    delete_ops AS
    (
        SELECT
            arrayJoin(ngrams(ifNull(before_text, ''), 1)) AS char_,
            toInt64(count(*) * -1) AS count
        FROM default.hacker_news_log
        WHERE op IN ('d', 'u')
        GROUP BY char_
    ),
    add_ops AS
    (
        SELECT
            arrayJoin(ngrams(ifNull(after_text, ''), 1)) AS char_,
            toInt64(count(*)) AS count
        FROM default.hacker_news_log
        WHERE op IN ('c', 'u')
        GROUP BY char_
    ),
    final AS
    (
        SELECT
            assumeNotNull(coalesce(nullIf(delete_ops.char_, ''), nullIf(add_ops.char_, ''))) AS char_,
            delete_ops.count + add_ops.count AS count
        FROM delete_ops
        FULL OUTER JOIN add_ops ON delete_ops.char_ = add_ops.char_
    )
SELECT *
FROM final

-- I made this solution cause dbt only supports 1 MatView for each Table.