#!/bin/bash

echo "Initializing databases"
python scripts/postgres/init.py
python scripts/clickhouse/init.py

echo "Initializing data sources and sink"
python scripts/redpanda/helpers/connect_source.py