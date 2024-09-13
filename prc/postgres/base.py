from sqlalchemy import (
    create_engine,
    MetaData
)
from sqlalchemy.engine import URL

# sqlalchemy 1.x:
# from sqlalchemy.ext.declarative import declarative_base

# sqlalchemy 2.x:
# MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os
import prc
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(prc.__file__))))

def get_db_url():
    load_dotenv()
    params = {
        "drivername": "postgresql",
        "username": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "host": os.getenv("POSTGRES_HOST"),
        "port": os.getenv("POSTGRES_PORT"),
        "database": os.getenv("POSTGRES_DB")
    }
    return URL.create(**params)

url = get_db_url()
engine = create_engine(url)
session = sessionmaker(bind=engine)()
Base = declarative_base()