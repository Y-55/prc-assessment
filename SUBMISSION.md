# Resolving the tasks using Alembic and Goose

In this branch, I focused on utilizing automatic migration from Alembic (SQLAlchemy's schema migration solution) for PostgreSQL and used Goose for ClickHouse migrations for simplicity and ease of use.  
- Goose is a database migration tool written in Go, designed to manage schema changes for databases. It allows developers to apply, rollback, and track schema migrations in a structured way using migration scripts. Goose is compatible with multiple databases, including PostgreSQL, MySQL, and ClickHouse, and helps ensure that database schemas are consistent across different environments (development, staging, production) by versioning changes.  
- Migrations in Goose can be written in SQL or Go, and the tool provides commands like up (to apply migrations) and down (to rollback migrations), making it easy to manage database versions.
> For raw SQL commands submission, check the files `task1.sql` and `task2.sql`

## Changes
- Updated the Dockerfile and docker-compose.yaml to include the necessary environment variables and install Go and Goose in the prc-management container.
- Initialized Alembic with a folder to be used for PostgreSQL schema migrations using autogenerate functionality.
- Created a folder, clickhouse-goose-migrations, which will contain ClickHouse migrations.
- Created modified versions of PostgreSQL and ClickHouse SQLAlchemy models located in new-schema-models.
- Created two migrations in clickhouse-goose-migrations for Task 1 and Task 2.

## Task 1 Steps
- exec into the container named `prc-management-1` or `management`
- start the poetry virtual python environment `poetry shell`
- Run clear command to clear all postgres and clickhouse tables defined by us: `./scripts/clear_tables.sh`
- Run start command to create all basic postrgres and clickhouse tables: `./scripts/init_dbs.sh`
- Run the first Clickhouse migraion which contains the code for creating char_counts table `cd clickhouse-goose-migrations` `goose up 20240915061431` `cd ..`
- Run simulation command to start a simulation of a CDC process with specified parameters (e.g., number of rows per step, simulation time seconds, pause time seconds): `./scripts/start_simulation.sh N_ADDED_ROWS_PER_STEP=50 N_SIM_TIME_SECONDS=60 N_PAUSE_TIME_SECONDS=2`
- Check the results.

NOTE: if you want to rerun it, you'll need to drop clickhouse tables manually or rool back the schema by execuing `goose down`.

## Task 2 Steps (Run it after task 1)
- Replace the file `prc/postgres/models/models.py` by `new-schema-models/postgres/models.py` which containse the code with the added columns.
- Run postgresql alembic auto migraiont command `alembic revision --autogenerate -m "add age, duration columns"` to automatically generate the migration code.
- Run `alembic upgrade head` to implement the migraiton
- Run `cd clickhouse-goose-migrations` `goose up` to run Clickhouse's manually created migraion.
- Check the results.

#### If you require additional clarificaion, please do not hesitate to contact me.
