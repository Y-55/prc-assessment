# Task

## Motivation

As explained in the README's Explanation/Setup Goal section, this task aims to evaluate your ability to manage our ClickHouse analytical workloads and optimize their management. The setup mirrors our production ClickHouse environment, and the tasks involve creating analytical views based on your understanding of the CDC (Change Data Capture) setup and established pipelines.

## Tasks
### 1. Counting Characters

We currently use the following PostgreSQL query to count the occurrences of each character in the text column:
```SQL
select char_, count(*)
from(
	select UNNEST(string_to_array(hacker_news."text", NULL)) as char_
	from hacker_news
)
group by char_
```

#### Objective:
Create a ClickHouse table named `char_counts` that reflects the exact result of this query.  
Ensure this table always reflects the latest data based on new inserts, deletes, or updates to the PostgreSQL hacker_news table.  
Use one or more materialized views to achieve this.


Ideally we can query clickhouse using:
```SQL
select *
from char_counts [final]
```
and we'd have the exact same result as the one from the PostgreSQL query.

Note: the \[final\] means that the `final` statement is optional depending on the way you design the table


#### Output format
The output of this task is a series of SQL commands defining the creation of all the required tables/materialzied views to generate the correct `char_counts` table.


#### Added points
- if you do it in a way that's version controlled

#### How to test:
- define your tables/materialized views
- follow the steps in [Steps](##Steps) to clear all tables defined by us and to start the CDC simulation process
    > NOTE: if you create some tables yourself, you might need to manually clear them using the `TRUNCATE` SQL command
- after the simulation is done, compare the answer you get from clickhouse:
    ```SQL
    select *
    from char_counts [final]
    ```

    to the answer from postgres:
    ```SQL 
    select char_, count(*)
    from(
        select UNNEST(string_to_array(hacker_news."text", NULL)) as char_
        from hacker_news
    )
    group by char_
    ```

### 2. Migration management

We need to modify the PostgreSQL hacker_news table schema by adding two new nullable columns:
```
"age" int
"duration" int
```

### Objective:
Add these columns to the PostgreSQL hacker_news table and update the existing CDC/ClickHouse process to include these new columns in the ClickHouse hacker_news table.
In the end, the clickhouse `hacker_news` table should include those 2 new columns.  
And when you manually add/update a few new rows to the postgres table with these 2 new columns, they should be reflected correctly in the `hacker_news` clickhouse table when querying:  
```
select * 
from hacker_news final
```

#### Output format
The output of this task is can be a series of SQL commands to edit/create/delete tables and materialized views.  
Or if you're comfortable with python, you can add to the code in `prc/postgres/models/models.py` and `prc/clickhouse/models/hackernews.py` to make the needed changes.  
Or can be written in any other language you prefer (golang, Java, ..etc) as long as you provide commands to run it correctly  


#### Added points
- if you do it in a way that's version controlled
- if you are able to automate this process

#### How to test:
- follow the steps in [Steps](##Steps) to clear all tables defined by us and to start the CDC simulation process
    > NOTE: if you create some tables yourself, you might need to manually clear them using `TRUNCATE`
- after the simulation is done, run your process to add the new 2 columns in postgres and clickhouse
- after the new columns are successfully integrated, add or edit a few rows in the postgres `hacker_news` table
- check that these changes are correctly reflected in the clickhouse `hacker_news` table



# Running the CDC simulation

## Steps
- exec into the container named `prc-management-1` or `management`
- start the poetry virtual python environment `poetry shell`
- Run clear command to clear all postgres and clickhouse tables defined by us: `./scripts/clear_tables.sh`
- Run start command to create all basic postrgres and clickhouse tables: `./scripts/init_dbs.sh`
- Run simulation command to start a simulation of a CDC process with specified parameters (e.g., number of rows per step, simulation time seconds, pause time seconds): `./scripts/start_simulation.sh N_ADDED_ROWS_PER_STEP=50 N_SIM_TIME_SECONDS=60 N_PAUSE_TIME_SECONDS=2`

### Checking that CDC is working when adding data to Postgres DB
While adding data to database, check `localhost:8123/play` and run the following query to check the final state of the final state table:
```SQL  
select * from hacker_news final
order by version desc;
```

## Explanation

### The content of `./init_dbs.sh`
- Initializes Postgres a model that is defined within `prc/postgres/models/models.py`: `hacker_news` table that stores some traditional data.
- Initialize ClickHouse models that are defined within `prc/clickhouse/models/models.py`, which includes the following tables and materialized views:
  - `hacker_news_log` table that stores the history of streamed data from `hacker_news_queue` using `hacker_news_log_mview` materialized view to sync both tables.
  - `hacker_news` tables that stores the final state from `hacker_news_log` using `mview_add_hacker_news` and `mview_del_hacker_news` materialized views to add and remove records accordingly.
- Connect the source (aka. `Postgres`) to `Redpanda` using Kafka connect (aka. `Debezium`). Check `connect-configs/connect-source.json` for more info.

### The content of `./clear_tables.sh`
- drops the tables and materialized views that are defined in `prc/postgres/models/models.py` and `prc/clickhouse/models/hackernews.py`

### The content of `./start_simulation.sh`
- Add data to the `hacker_news` table within `Postgres` Database.
  - The script runs for a total of `N_SIM_TIME_SECONDS` seconds
  - First, we add randomly generated `N_ADDED_ROWS_PER_STEP` rows to the `hacker_news` table in postgres
  - After, the simulation runs an infinite loop that randomly decides to update, delete, or add more rows to the `hacker_news` table
  - After each add/delete/add operation the script pauses for `N_PAUSE_TIME_SECONDS` seconds
  - The script terminates once the simulation time is >= `N_SIM_TIME_SECONDS` seconds
