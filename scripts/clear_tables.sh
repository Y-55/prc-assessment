#!/bin/bash

echo "clearing databases in postgres and clickhouse"
python scripts/postgres/clear.py
python scripts/clickhouse/clear.py