# PRC (Postgres, Redpanda, ClickHouse)


This serves as a detailed description for the local setup to run the assessment.  
It includes explanation to runing a postgres db, trigger a CDC process, and consume it in clickhouse.  
> For the task details, read `TASK.md`

## Prerequisites
- Docker with enough RAM and CPU

## Installed Containers
- Postgres DB. This acts as our main production database that our application logic is running on
- Clickhouse. This is our datawarehouse where we want to have a copy of all changes of our Postgres tables and add extra analytical views to use.
- Connect (Debezium). Debezium is responsible for starting and executing the CDC process from Postgres to the destination sink.
- Redpanda. A kafka alternative that is simpler to deploy, and arguably more effecient.
- Redpanda-console. The console to observe and manage redpanda topics,consumers, ..etc if needed
- The management container, which is a python-based container that has everything needed to run our scripts to create and clean the tables in postgres and clickhouse, and that has the logic to CDC simulation process 

## Setup
- Build the containers using `docker compose up -d`


## Explanation

### Setup Goal
The goal of this setup is to simulate how we are using Clickhosue with our Malaa databases. It provides a playground to test ClickHouse concepts and functionality.

In this setup we'll have a postgres table `hacker_news` which we consider as a table used by the Malaa application in production, and that is being added to, updated, and deleted from.

We'll also have a CDC process set up to log the changefeed of the postgres table into clickhouse, and to build analytical workloads of these tables in clickhouse.

The clickhouse tables and materialized views processes set up in this assessment are the building blocks of all of our clickhouse analytical workloads in Malaa. You might not need to use all of them. They provide an insight to how we use clickhouse and how we hope you can help us with using it.

### CDC Process Explanation

1. Changes in Postgres:
    - Changes (additions, edits, deletions) occur in the `hacker_news` table in Postgres.
2. Debezium Tracking:
    - Debezium tracks these changes and publishes the change logs to Redpanda's topic `pg.public.hacker_news`.
3. ClickHouse Queue:
    - A ClickHouse table named `hacker_news_queue` is subscribed to the Redpanda topic `pg.public.hacker_news`. This table uses the [Kafka Engine](https://clickhouse.com/docs/en/engines/table-engines/integrations/kafka) and serves as the entry point for CDC changelogs into ClickHouse. Note that this table does not support SELECT statements and is only used as a source for downstream processes.
    - The data in this table consists of two JSON objects: `before` and `after`, each containing the values of the database row before and after the create/delete/update event.
4. Materialized View for Log Processing:
    - A materialized view named `hacker_news_log_mview` consumes data from `hacker_news_queue`, flattens the JSON data into columns, and extracts the operation op code from the message. This view writes the flattened data into the `hacker_news_log` table, which uses the [MergeTree Engine](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree).
    - At this stage, all changes from the original Postgres table are saved in `hacker_news_log` in a log format with before and after states.
5. Creating the Final Table:
    - The next steps involve consuming these logs to create a table that reflects the final state of these changes, matching the original Postgres table.
    - Two materialized views, `mview_add_hacker_news` and `mview_del_hacker_news`, read the log records and generate rows for the final table `hacker_news` based on the operation op.
6. Final Table Configuration:
    - The final table `hacker_news` uses the [ReplacingMergeTree Engine](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree) with the id column as the primary key. It also uses the `version` and `deleted` columns to manage row replacements and deletions.
    - `mview_add_hacker_news` generates new rows representing the most recent `version` of each row with a specific `id`.
    - `mview_del_hacker_news` generates rows indicating which rows to remove from the final table, ensuring that only the latest true values are kept.
7. Final State Management:
    - The `hacker_news` table may contain multiple rows for the same `id` value, but the engine will eventually keep only the row with the highest `version` value. If this row has a `deleted` value of 1, it will be removed, and no records for that `id` will persist.
    - To see the merged version of the table, you can query it using the `FINAL` keyword 
    ```SQL
    select *
    from hacker_news FINAL
    ```

### Repanda Console

Accessing `localhost:8080` should take you to `Redpanda Console`. This is where you can see the CDC change feed messages when they get to redpanda.  
It's not necessary to use, but might be helpful in debugging if you suspect that data is not being streamed into redpanda correctly.  

#### Topics

When accessing `Topics`' page, you will see four rows:
- `connect-configs`, `connect-offsets`, and `connect-status` are metadata used by Redpanda to track processes.
- `pg.public.hacker_news` is our created topic for this example by `Debezium`. It follows `PREFIX_TOPIC_FROM_DEBEZIUM_SETTINGS.public.TABLE_NAME`. Within the topic's page, you will see
  - `Messages` tab shows the latest messages
  - `Consumers` tab shows the consumers that are listening. You should see one called `clickhouse-connect-group` if you run `./init_dbs.sh`, and you should see another one called `my-group` if you run `scripts/redpanda/consume_data_sample.py` which is python script that listens and prints what exists within the topic.
  - Other tabs are settings and can be ignored at the moment



## Local Credentials
### Postgres
- username: admin
- password: password
- localhost:5432

### Clickhouse
- username: default
- password: (no password)
- localhost:9000

# Task Details
For specific task instructions, refer to `TASK.md`