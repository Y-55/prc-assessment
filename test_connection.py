import clickhouse_connect

client = clickhouse_connect.get_client(host='localhost', port=8123, username='default', password='')

# for queue_number in range(100, 1000):
#     r1 = client.query(f'''CREATE TABLE IF NOT EXISTS default.hacker_news_queue{queue_number}
# (
#     `before` Nullable(String),
#     `after` Nullable(String),
#     `ts_ms` Float64,
#     `op` String
# )
# ENGINE = Kafka('redpanda-1:29092', 'pg.public.hacker_news', 'clickhouse-connect-group', 'JSONEachRow')''')
    
for queue_number in range(1, 1000):
    r1 = client.query(f'''DROP TABLE default.hacker_news_queue{queue_number}''')



print(r1)


