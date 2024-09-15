-- +goose Up
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

-- +goose Down
DROP TABLE default.char_counts;
DROP TABLE default.add_char_counts_mv;
DROP TABLE default.del_char_counts_mv;
