
ALTER TABLE "default"."hacker_news_log"
ADD COLUMN "before_age" Nullable(Int64),
ADD COLUMN "before_duration" Nullable(Int64),
ADD COLUMN "after_age" Nullable(Int64),
ADD COLUMN "after_duration" Nullable(Int64);

DROP TABLE "default"."hacker_news_log_mview";

CREATE MATERIALIZED VIEW default.hacker_news_log_mview TO default.hacker_news_log
(
    `ts_ms` Float64,
    `op` String,
    `before_id` Nullable(String),
    `before_text` Nullable(String),
    `before_counter` Nullable(String),
    `before_state` Nullable(String),
    `before_created_at` Nullable(String),
    `before_updated_at` Nullable(String),
    `before_age` Nullable(String), --age
    `before_duration` Nullable(String), --duration
    `after_id` Nullable(String),
    `after_text` Nullable(String),
    `after_counter` Nullable(String),
    `after_state` Nullable(String),
    `after_created_at` Nullable(String),
    `after_updated_at` Nullable(String),
    `after_age` Nullable(String), --age
    `after_duration` Nullable(String) --duration
)
AS SELECT
    hacker_news_queue.ts_ms AS ts_ms,
    multiIf(before IS NULL, 'c', after IS NULL, 'd', 'u') AS op,
    JSONExtract(before, 'id', 'Nullable(String)') AS before_id,
    JSONExtract(before, 'text', 'Nullable(String)') AS before_text,
    JSONExtract(before, 'counter', 'Nullable(String)') AS before_counter,
    JSONExtract(before, 'state', 'Nullable(String)') AS before_state,
    JSONExtract(before, 'created_at', 'Nullable(String)') AS before_created_at,
    JSONExtract(before, 'updated_at', 'Nullable(String)') AS before_updated_at,
    JSONExtract(before, 'age', 'Nullable(String)') AS before_age, -- age
    JSONExtract(before, 'duration', 'Nullable(String)') AS before_duration, -- duration
    JSONExtract(after, 'id', 'Nullable(String)') AS after_id,
    JSONExtract(after, 'text', 'Nullable(String)') AS after_text,
    JSONExtract(after, 'counter', 'Nullable(String)') AS after_counter,
    JSONExtract(after, 'state', 'Nullable(String)') AS after_state,
    JSONExtract(after, 'created_at', 'Nullable(String)') AS after_created_at,
    JSONExtract(after, 'updated_at', 'Nullable(String)') AS after_updated_at,
    JSONExtract(after, 'age', 'Nullable(String)') AS after_age, -- age
    JSONExtract(after, 'duration', 'Nullable(String)') AS after_duration -- duration
FROM default.hacker_news_queue;

ALTER TABLE "default"."hacker_news"
ADD COLUMN "age" Nullable(Int64),
ADD COLUMN "duration" Nullable(Int64);

DROP TABLE "default"."mview_add_hacker_news";

CREATE MATERIALIZED VIEW default.mview_add_hacker_news TO default.hacker_news
(
    `id` Int64,
    `text` Nullable(String),
    `counter` Nullable(Int64),
    `state` Nullable(Bool),
    `created_at` Nullable(Int64),
    `updated_at` Nullable(Int64),
    `version` Int64,
    `deleted` UInt8,
    `age` Nullable(Int64), --age
    `duration` Nullable(Int64) --dur
)
AS SELECT
    toInt64(assumeNotNull(after_id)) AS id,
    hacker_news_log.after_text AS text,
    hacker_news_log.after_counter AS counter,
    hacker_news_log.after_state AS state,
    hacker_news_log.after_created_at AS created_at,
    hacker_news_log.after_updated_at AS updated_at,
    hacker_news_log.ts_ms AS version,
    0 AS deleted,
    hacker_news_log.after_age AS age, --age
    hacker_news_log.after_duration AS duration --dur
FROM default.hacker_news_log
WHERE hacker_news_log.op IN ('c', 'u');

DROP TABLE "default"."mview_del_hacker_news";

CREATE MATERIALIZED VIEW default.mview_del_hacker_news TO default.hacker_news
(
    `id` Int64,
    `text` Nullable(String),
    `counter` Nullable(Int64),
    `state` Nullable(Bool),
    `created_at` Nullable(Int64),
    `updated_at` Nullable(Int64),
    `version` Int64,
    `deleted` UInt8,
    `age` Nullable(Int64), --age
    `duration` Nullable(Int64) --dur
)
AS SELECT
    toInt64(assumeNotNull(before_id)) AS id,
    hacker_news_log.before_text AS text,
    hacker_news_log.before_counter AS counter,
    hacker_news_log.before_state AS state,
    hacker_news_log.before_created_at AS created_at,
    hacker_news_log.before_updated_at AS updated_at,
    hacker_news_log.ts_ms AS version,
    1 AS deleted,
    hacker_news_log.before_age AS age, --age
    hacker_news_log.before_duration AS duration --dur
FROM default.hacker_news_log
WHERE hacker_news_log.op IN ('d');
