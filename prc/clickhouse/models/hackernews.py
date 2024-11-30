from sqlalchemy import Column, literal, JSON, text
from clickhouse_sqlalchemy import (
    engines,
    select,
    MaterializedView,
    types
)

from prc.clickhouse.base import Base

class HackerNewsQueue(Base):
    before = Column(types.Nullable(types.String), name="before", primary_key=True, nullable=True)
    after = Column(types.Nullable(types.String), name="after", primary_key=True, nullable=True)
    ts_ms = Column(types.Float64, name="ts_ms", primary_key=True, nullable=False)
    op = Column(types.String, name='op', primary_key=True, nullable=False)
    
    __tablename__ = 'hacker_news_queue'
    __table_args__ = (
        engines.Kafka(
            broker_list='redpanda-1:29092',
            topic_list = 'pg.public.hacker_news',
            kafka_group_name = 'clickhouse-connect-group',
            kafka_format = 'JSONEachRow',
        ),
        {}
    )

class HackerNewsQueueTable(Base):
    id = Column((types.Int64), name='id', primary_key=True, nullable=False)
    op = Column(types.String, name='op', primary_key=True, nullable=False)
    before = Column(types.Nullable(types.String), name='before', nullable=True)
    after = Column(types.Nullable(types.String), name="after", nullable=True)
    ts_ms = Column(types.Float64, name="ts_ms", primary_key=True, nullable=False)
    version = Column(types.Float64, name="version", nullable=False)
    deleted = Column(types.Boolean, name="deleted", nullable=False)
    
    __tablename__ = 'hacker_news_queue_table'
    __table_args__ = (
        engines.ReplacingMergeTree(
            order_by='id',
            primary_key='id',
            version='version',
            deleted='deleted'
        ),
        {}
    )

HackerNewsQueueMatView = MaterializedView(
    HackerNewsQueueTable,
    select(
        text("coalesce(JSONExtract(before, 'id', 'Int64'), JSONExtract(after, 'id', 'Int64')) AS id"),
        HackerNewsQueue.op.label('op'),
        HackerNewsQueue.before.label('before'),
        HackerNewsQueue.after.label('after'),
        HackerNewsQueue.ts_ms.label('ts_ms'),
        HackerNewsQueue.ts_ms.label('version'),
        text("if(op = 'd', 1, 0) AS deleted")
    ),
    use_to=True, 
    name=f'{HackerNewsQueue.__tablename__}_mv',
)

# class HackerNewsLog(Base):
#     before_id = Column(types.Nullable(types.Int64),name='before_id', primary_key=True, nullable=True)
#     before_text = Column(types.Nullable(types.String),name='before_text', nullable=True)
#     before_counter = Column(types.Nullable(types.Int64),name='before_counter', nullable=True)
#     before_state = Column(types.Nullable(types.Boolean),name='before_state', nullable=True)
#     before_created_at = Column(types.Nullable(types.Int64),name='before_created_at', nullable=True)
#     before_updated_at = Column(types.Nullable(types.Int64),name='before_updated_at', nullable=True)
    
#     after_id = Column(types.Nullable(types.Int64),name='after_id', primary_key=True)
#     after_text = Column(types.Nullable(types.String),name='after_text', nullable=True)
#     after_counter = Column(types.Nullable(types.Int64),name='after_counter', nullable=True)
#     after_state = Column(types.Nullable(types.Boolean),name='after_state', nullable=True)
#     after_created_at = Column(types.Nullable(types.Int64),name='after_created_at', nullable=True)
#     after_updated_at = Column(types.Nullable(types.Int64),name='after_updated_at', nullable=True)
    
#     ts_ms = Column(types.Int64,name='ts_ms', primary_key=True)
#     op = Column(types.String,name='op', primary_key=True)
    
#     __tablename__ = 'hacker_news_log'
#     __table_args__ = (
#         engines.MergeTree(
#             primary_key="ts_ms",
#         ),
#         {}
#     )

# class HackerNews(Base):
#     id = Column(types.Int64,name='id',primary_key=True)
#     text = Column(types.String,name='text')
#     counter = Column(types.Int64,name='counter')
#     state = Column(types.Boolean,name='state')
#     created_at = Column(types.Int64,name='created_at')
#     updated_at = Column(types.Int64,name='updated_at')
    
#     version = Column(types.Int64,name='version',primary_key=True)
#     deleted = Column(types.UInt8,name='deleted',primary_key=True)
    
#     __tablename__ = 'hacker_news'
#     __table_args__ = (
#         engines.ReplacingMergeTree(
#             order_by='id',
#             primary_key='id',
#             version='version',
#             deleted='deleted'
#         ),
#         {}
#     )

# HackerNewsMatViewAdd = MaterializedView(
#     HackerNews, 
#     select(
#         text("toInt64(assumeNotNull(after_id)) as id"),
#         HackerNewsLog.after_text.label('text'),
#         HackerNewsLog.after_counter.label('counter'),
#         HackerNewsLog.after_state.label('state'),
#         HackerNewsLog.after_created_at.label('created_at'),
#         HackerNewsLog.after_updated_at.label('updated_at'),
#         HackerNewsLog.ts_ms.label('version'),
#         literal(0).label('deleted')
#     ).where(
#         HackerNewsLog.op.in_(['c','u'])
#     ),
#     use_to=True, 
#     name=f'mview_add_{HackerNews.__tablename__}'
# )

# HackerNewsMatViewDel = MaterializedView(
#     HackerNews, 
#     select(
#         text("toInt64(assumeNotNull(before_id)) as id"),
#         HackerNewsLog.before_text.label('text'),
#         HackerNewsLog.before_counter.label('counter'),
#         HackerNewsLog.before_state.label('state'),
#         HackerNewsLog.before_created_at.label('created_at'),
#         HackerNewsLog.before_updated_at.label('updated_at'),
#         HackerNewsLog.ts_ms.label('version'),
#         literal(1).label('deleted')
#     ).where(
#         HackerNewsLog.op.in_(['d','u'])
#     ),
#     use_to=True, 
#     name=f'mview_del_{HackerNews.__tablename__}'
# )

# HackerNewsLogMatView = MaterializedView(
#     HackerNewsLog,
#     select(
#         HackerNewsQueue.ts_ms.label("ts_ms"),
#         text("multiIf(isNull(before), 'c', isNull(after), 'd', 'u') as op"),
#         text(
#             "JSONExtract(before, 'id', 'Nullable(String)')  as before_id"
#         ),
#         text("JSONExtract(before, 'text', 'Nullable(String)')  as before_text"),
#         text(
#             "JSONExtract(before, 'counter', 'Nullable(String)')  as before_counter"
#         ),
#         text(
#             "JSONExtract(before, 'state', 'Nullable(String)')  as before_state"
#         ),
#         text(
#             "JSONExtract(before, 'created_at', 'Nullable(String)')  as before_created_at"
#         ),
#         text(
#             "JSONExtract(before, 'updated_at', 'Nullable(String)')  as before_updated_at"
#         ),

        
#         text(
#             "JSONExtract(after, 'id', 'Nullable(String)')  as after_id"
#         ),
#         text("JSONExtract(after, 'text', 'Nullable(String)')  as after_text"),
#         text(
#             "JSONExtract(after, 'counter', 'Nullable(String)')  as after_counter"
#         ),
#         text(
#             "JSONExtract(after, 'state', 'Nullable(String)')  as after_state"
#         ),
#         text(
#             "JSONExtract(after, 'created_at', 'Nullable(String)')  as after_created_at"
#         ),
#         text(
#             "JSONExtract(after, 'updated_at', 'Nullable(String)')  as after_updated_at"
#         ),
#     ),
#     use_to=True,
#     name="hacker_news_log_mview",
# )