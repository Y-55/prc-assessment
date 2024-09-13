import os
from dotenv import load_dotenv
from typing import Any

import pandas as pd
import sqlalchemy as sa
from sqlalchemy import (
    create_engine,
)
# sqlalchemy 1.x:
# from sqlalchemy.ext.declarative import declarative_base

# sqlalchemy 2.x:
# MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9
from sqlalchemy.orm import declarative_base

# from sqlalchemy.orm import sessionmaker
# from clickhouse_sqlalchemy import get_declarative_base
from clickhouse_sqlalchemy import make_session

from clickhouse_sqlalchemy import MaterializedView
from sqlalchemy.orm.decl_api import DeclarativeMeta

class ClikchouseSQLAlchmeyWrapper():
    def __init__(self, env_path:str=None, is_refelct=True):
        if env_path is None:
            # print("env_path is None")
            import prc
            PROJECT_PATH=os.path.dirname(os.path.dirname(os.path.abspath(prc.__file__)))
            env_path=PROJECT_PATH+"/.env"
        load_dotenv(env_path)
        self._check_env()
        self.uri = "clickhouse+native://{user}:{password}@{host}:{port}/{db}".format(
            user=os.getenv("CLICKHOUSE_USER"),
            password=os.getenv("CLICKHOUSE_PASSWORD"),
            host=os.getenv("CLICKHOUSE_HOST"),
            port=os.getenv("CLICKHOUSE_NATIVE_PORT"),
            db=os.getenv("CLICKHOUSE_DB")
        )
        self._start(is_refelct=is_refelct)
    
    def _start(self, is_refelct=True, uri=None):
        if uri is not None:
            self.uri = uri
        self.engine = create_engine(self.uri)
        self.session = make_session(self.engine)
        # self.session = sessionmaker(bind=engine)()
        # self.metadata = MetaData()
        # self.metadata.bind = self.engine
        # self.ase = get_declarative_base(metadata=metadata)
        self.base = declarative_base()
        if is_refelct:
            self.base.metadata.reflect(self.engine)

    def _check_env(self):
        elements = [
            "CLICKHOUSE_HOST",
            "CLICKHOUSE_NATIVE_PORT",
            "CLICKHOUSE_USER",
            "CLICKHOUSE_PASSWORD",
            "CLICKHOUSE_DB",
        ]
        for element in elements:
            if os.getenv(element) is None:
                raise Exception(f"{element} not found in .env")
        
    def is_materialized_view(self, obj: object) -> bool:
        """Check if object is a MaterializedView object

        Args:
            obj (object): object to check if it is a MaterializedView object

        Returns:
            bool: True if object is a MaterializedView object, False otherwise
        """
        return type(obj) == MaterializedView

    def is_table(self, obj: object) -> bool:
        """Check if object is a Table object

        Args:
            obj (object): object to check if it is a Table object

        Returns:
            bool: True if object is a Table object, False otherwise
        """
        return type(obj) == DeclarativeMeta

    def has_object(self, obj: object, _type: str=None) -> bool:
        """Check if object exists in the database

        Args:
            obj (object): object to check if it exists in the database
            _type (str, optional): Type of object to check for. Defaults to None.

        Raises:
            ValueError: object is not a MATERIALIZED_VIEW or TABLE
            ValueError: passed type doesn't match object type

        Returns:
            bool: True if object exists in the database, False otherwise
        """
        if _type == None:
            if self.is_materialized_view(obj):
                return sa.inspect(self.engine).has_table(obj.name)
            elif self.is_table(obj):
                return sa.inspect(self.engine).has_table(obj.__tablename__)
            else:
                raise ValueError(f'object is not a MATERIALIZED_VIEW or TABLE')
        elif _type == 'MATERIALIZED_VIEW' and self.is_materialized_view(obj):
            return sa.inspect(self.engine).has_table(obj.name)
        elif _type == 'TABLE' and self.is_table(obj):
            return sa.inspect(self.engine).has_table(obj.__tablename__)
        else:
            raise ValueError(f'passed type is {_type} but object is {type(obj)}')
            

    def has_table(self, obj: object) -> bool:
        """Check if table exists in the database

        Args:
            obj (object): object to check if it exists in the database

        Returns:
            bool: True if table exists in the database, False otherwise
        """
        return self.has_object(obj, _type='TABLE')

    def has_materialized_view(self, obj: object) -> bool:
        """Check if materialized view exists in the database

        Args:
            obj (object): object to check if it exists in the database

        Returns:
            bool: True if materialized view exists in the database, False otherwise
        """
        return self.has_object(obj, _type='MATERIALIZED_VIEW')

    def insert(self, table: DeclarativeMeta, values: dict):
        """Insert values into a table

        Args:
            table (DeclarativeMeta): Table to insert values into
            values (dict): Values to insert into the table
        """
        self.execute(
            table.__table__.insert(), 
            values
        )
        self.commit()

    def update(self, table:DeclarativeMeta, where:dict, values:dict):
        """Update values in a table

        Note: 
            can't update primary keys
        
        Args:
            table (DeclarativeMeta): Table to update values in
            where (dict): Where clause to filter rows to update
            values (dict): Values to update in the table (key=column, value=new_value
        """
        query = table.__table__.update()
        if where:
            for k,v in where.items():
                query = query.where(table.__table__.c[k] == v)
        query = query.values(values)
        
        self.execute(query)
        self.commit()

    def delete(self, table:DeclarativeMeta, where:dict):
        """

        Args:
            table (DeclarativeMeta): Table to delete values from
            where (dict): Where clause to filter rows to delete
        """
        query = table.__table__.delete()
        if where:
            for k,v in where.items():
                query = query.where(table.__table__.c[k] == v)
            
        self.execute(query)
        self.commit()
        
    def has_value(self, table:DeclarativeMeta, where):
        """Check if a value exists in a table

        Args:
            table (_type_): _description_
            where (_type_): _description_

        Returns:
            _type_: _description_
        """
        query = table.__table__.select()
        if where:
            for k,v in where.items():
                query = query.where(table.__table__.c[k] == v)
        
        result = self.execute(query).fetchall()
        return len(result) > 0

    def select(self, table:DeclarativeMeta, where: dict=None, verbose: bool=False, to_pandas:bool=True):
        """Select values from a table

        Args:
            table (DeclarativeMeta): Table to select values from
            where (dict, optional): Where clause to filter rows to select. Defaults to None.
            verbose (bool, optional): Print the result. Defaults to False.
            to_pandas (bool, optional): Convert the result to a pandas DataFrame. Defaults to True.

        Returns:
            list: List of values from the table
            or
            pd.DataFrame: DataFrame of values from the table
        """
        query = table.__table__.select()
        if where:
            for k,v in where.items():
                query = query.where(table.__table__.c[k] == v)
        
        result = self.execute(query).fetchall()
        
        if to_pandas:
            columns = [column.name for column in table.__table__.columns]
            result = pd.DataFrame(result, columns=columns)
        if verbose:
            print(result)
        return result   

    def create(self, obj:object):
        """Create a table or materialized view
        Args:
            obj (object): object to create
        """
        if type(obj) == MaterializedView:
            if not self.has_materialized_view(obj):
                obj.create(bind=self.engine, checkfirst=True)
            else:
                print(f'{obj.name} does exist')
        elif type(obj) == DeclarativeMeta:
            if not self.has_table(obj):
                obj.__table__.create(bind=self.engine, checkfirst=True)
            else:
                print(f'{obj.__tablename__} does exist')
        else:
            print(f'object is not a MATERIALIZED_VIEW or TABLE')

    def drop(self, obj:object):
        """Drop a table or materialized view
        Args:
            obj (object): object to create
        """
        if type(obj) == MaterializedView:
            if self.has_materialized_view(obj):
                obj.drop(bind=self.engine, checkfirst=True)
            else:
                print(f'{obj.name} does not exist')
        elif type(obj) == DeclarativeMeta:
            if self.has_table(obj):
                obj.__table__.drop(bind=self.engine, checkfirst=True)
            else:
                print(f'{obj.__tablename__} does not exist')
        else:
            print(f'object is not a MATERIALIZED_VIEW or TABLE')

    def create_all(self):
        """Create all tables and materialized views
        """
        self.base.metadata.create_all(bind=self.engine, checkfirst=True)

    def drop_all(self):
        """Drop all tables and materialized views
        """
        self.base.metadata.drop_all(bind=self.engine, checkfirst=True)
        
    def show_tables(self, detailed:bool=False):
        if detailed:
            data = []
            for k, v in self.base.metadata.tables.items():
                data.append({
                    "name": v.name,
                    "columns": {
                        c.name: {
                            "type": c.type,
                            "nullable": c.nullable,
                            "default": c.default,
                            "primary_key": c.primary_key
                        }
                        for c in v.columns
                    },
                    "engine": v.engine
                })
            return data
        return list(self.base.metadata.tables.keys())
    
    def execute(self, query:Any):
        return self.session.execute(query)

    def commit(self):
        self.session.commit()