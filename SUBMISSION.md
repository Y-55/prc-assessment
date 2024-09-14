# Resolving the tasks using DBT (Data Build Tool)

In this brunch, I focused on utilizing dbt to handle all the necessary data transformations after creating the Kafka engine table, hacker_news_queue.  
dbt is a transformation tool responsible for handling the 'T' in the ELT process, meaning it focuses solely on transformations, not on loading data.  
In our case, the loading is managed by the ClickHouse Kafka engine, which I will continue to handle using the Python model HackerNewsQueue to create it.  
  
> For raw SQL commands submission, check the files `task1.sql` and `task2.sql`

## dbt Discovered Limitations
So far, I’ve identified three limitations with dbt:

- We cannot create more than one materialized view (MV) to push records into the same table.
- dbt does not support ALTER queries, so when the schema changes, instead of altering the tables, we have to recreate them, which re-runs all transformations on the entire dataset.
- There is limited support for some ClickHouse engines, such as the Kafka engine.


## Changes
- Updated the pyproject.toml with the needed packages for dbt.
- Created a folder for the dbt project named dbt-clickhouse-malaa and initialized dbt-clickhouse within it. -- mounted to management service on the docker compse file
- Commented out all the models in prc/clickhouse/models/hackernews.py except for HackerNewsQueue (the Kafka engine table), as dbt will be used to manage the remaining transformations.
- Created new model called HackerNewsQueueTable which would be used as the landing table for the rocords which coming to HackerNewsQueue.
- Added the command to run dbt in the scripts/init_dbs.sh file: 
    - `cd dbt-clickhouse-malaa` `dbt run`
    - This command navigates to the dbt project directory and runs all dbt models.
    - dbt models in `dbt-clickhouse-malaa/models`:
        - `hacker_news_queue_table`: used for storing selectable raw logs from the hacker_news_queue so when we requier to change the schema we can reselect all the raw records.
        - `hacker_news_log`: used for normlizing data from hacker_news_queue_table
        - `hacker_news`: the final table which mirrors the table in postgresql
        - `char_counts`: the table for task 1

## Task 1 Steps
- exec into the container named `prc-management-1` or `management`
- start the poetry virtual python environment `poetry shell`
- Run clear command to clear all postgres and clickhouse tables defined by us: `./scripts/clear_tables.sh`
- > Run start command to create all basic postrgres and clickhouse tables: `./scripts/init_dbs.sh` (task 1 would be implemented here)
- Run simulation command to start a simulation of a CDC process with specified parameters (e.g., number of rows per step, simulation time seconds, pause time seconds): `./scripts/start_simulation.sh N_ADDED_ROWS_PER_STEP=50 N_SIM_TIME_SECONDS=60 N_PAUSE_TIME_SECONDS=2` 

NOTE: if you want to rerun it, you'll need to drop clickhouse tables manually.

## Task 2 Steps (Run it after task 1)
- Alter the tables in PostgreSQL and add the 2 columns
- Replace the models in dbt-clickhouse-malaa/models by the models in dbt-models-new-schema which contains the exact same models with the added 2 new columns (age, duration)
- exec into the container named `prc-management-1` or `management`
- Run the following commands:
    - > cd dbt-clickhouse-malaa
    - > dbt run -s hacker_news_log hacker_news --full-refresh

#### If you require additional clarificaion, please do not hesitate to contact me.
