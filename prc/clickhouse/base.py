from sqlalchemy import (
    create_engine,
    MetaData
)
# sqlalchemy 1.x:
# from sqlalchemy.ext.declarative import declarative_base

# sqlalchemy 2.x:
# MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from clickhouse_sqlalchemy import get_declarative_base, make_session

from dotenv import load_dotenv
import os
import prc
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(prc.__file__))))

def get_db_url():
    load_dotenv()
    DB_ENGINE = "clickhouse+native"
    DB_NAME = os.getenv("CLICKHOUSE_DB")
    DB_HOST = os.getenv("CLICKHOUSE_HOST")
    DB_PORT = os.getenv("CLICKHOUSE_NATIVE_PORT")
    DB_USER = os.getenv("CLICKHOUSE_USER")
    DB_PASS = os.getenv("CLICKHOUSE_PASSWORD")
    return f"{DB_ENGINE}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

URI = get_db_url()
engine = create_engine(URI)
session = make_session(engine)
# session = sessionmaker(bind=engine)()
# metadata = MetaData()
# metadata.bind = engine
# Base = get_declarative_base(metadata=metadata)
Base = declarative_base()