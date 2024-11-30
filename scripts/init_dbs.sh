#!/bin/bash

echo "Initializing databases"
python3 scripts/postgres/init.py
python3 scripts/clickhouse/init.py

echo "Initializing data sources and sink"
python3 scripts/redpanda/helpers/connect_source.py

# cd dbt-clickhouse-malaa
# dbt run