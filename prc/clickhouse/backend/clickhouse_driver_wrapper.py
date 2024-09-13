import os
from typing import List, Any
from dotenv import load_dotenv
import pandas as pd
from clickhouse_driver import Client
import prc.clickhouse.backend.engines as ENGINES

class ClikchouseDriverWrapper():
    def __init__(
        self,
        env_path:str=None,
    ):
        if env_path is None:
            import prc
            PROJECT_PATH=os.path.dirname(os.path.dirname(os.path.abspath(prc.__file__)))
            env_path=PROJECT_PATH+"/.env"
        load_dotenv(env_path)
        self._check_env()
        self.host = os.getenv("CLICKHOUSE_HOST")
        self.port = os.getenv("CLICKHOUSE_NATIVE_PORT")
        self.user = os.getenv("CLICKHOUSE_USER")
        self.password = os.getenv("CLICKHOUSE_PASSWORD")
        
        self._start(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password
        )
    
    def _start(self, host,port,user,password):
        self.client = Client(
            host=host,
            port=port,
            user=user,
            password=password,
        )
    def _check_env(self):
        elements = [
            "CLICKHOUSE_HOST",
            "CLICKHOUSE_NATIVE_PORT",
            "CLICKHOUSE_USER",
            "CLICKHOUSE_PASSWORD",
        ]
        for element in elements:
            if os.getenv(element) is None:
                raise Exception(f"{element} not found in .env")

    def execute(self, input):
        return self.client.execute(input)
    def query_dataframe(self, input):
        return self.client.query_dataframe(input)
    
    def run(self, queries, verbose=True, to_pandas=True, skip=False,just_output=False,title=None):
        if skip: return
        if title is not None and title != "":
            print(f"<< {title} >>")
        queries = [query.strip() for query in queries.split(';') if query.strip() != '']
        if verbose and not just_output: print(f"Running {len(queries)} commands")
        for i, query in enumerate(queries):
            if verbose and not just_output: 
                print(f"Running: (order={i})")
                print(query)
            if to_pandas:
                output = self.client.query_dataframe(query)
                if verbose:
                    if not output.empty:
                        print("Output:")
                        print(output)
            else:
                output = self.client.execute(query)
                if verbose:
                    if output:
                        print("Output:")
                        print(output)

    def has_table(self, table_name: str):
        query = f"SHOW TABLES LIKE '{table_name}'"
        result = self.client.execute(query)
        return len(result) > 0

    def has_materialized_view(self, mv_name: str) -> bool:
        pass

    def insert(self, table_name: str, values: dict):
        """Insert values into a table

        Args:
            table_name (str): Table to insert values into
            values (dict): Values to insert into the table
        """
        pass

    def update(self, table_name:str, where:dict, values:dict):
        """Update values in a table

        Note: 
            can't update primary keys
        
        Args:
            table_name (str): Table to update values in
            where (dict): Where clause to filter rows to update
            values (dict): Values to update in the table (key=column, value=new_value
        """
        query = f"UPDATE {table_name} SET "
        if where:
            for k,v in where.items():
                pass
        query = query.values(values)
        
        self.session.execute(query)
        self.session.commit()

    def delete(self, table_name:str, where:dict):
        """

        Args:
            table (DeclarativeMeta): Table to delete values from
            where (dict): Where clause to filter rows to delete
        """
        query = f"DELETE FROM {table_name}"
        if where:
            for k,v in where.items():
                pass
            
        self.session.execute(query)
        self.session.commit()
        
    def has_value(self, table_name:str, where):
        """Check if a value exists in a table

        Args:
            table_name (_type_): _description_
            where (_type_): _description_

        Returns:
            _type_: _description_
        """
        query = f"SELECT * FROM {table_name}"
        if where:
            for k,v in where.items():
                pass
        
        result = self.session.execute(query).fetchall()
        return len(result) > 0

    def select(self, table_name:str, where: dict=None, verbose: bool=False, to_pandas:bool=True):
        """Select values from a table

        Args:
            table_name (str): Table to select values from
            where (dict, optional): Where clause to filter rows to select. Defaults to None.
            verbose (bool, optional): Print the result. Defaults to False.
            to_pandas (bool, optional): Convert the result to a pandas DataFrame. Defaults to True.

        Returns:
            list: List of values from the table
            or
            pd.DataFrame: DataFrame of values from the table
        """
        query = f"SELECT * FROM {table_name}"
        if where:
            for k,v in where.items():
                pass

        result = self.session.execute(query).fetchall()  
    def valid_column(self, column:dict):
        if 'name' not in column:
            raise ValueError(f"Column name not found")
        if 'type' not in column:
            raise ValueError(f"Column type not found")
        if 'primary_key' in column and type(column['primary_key']) != bool:
            raise ValueError(f"Column primary_key should be a boolean")
        return True
    def valid_engine(self, engine, columns):
        if engine['name'] not in ENGINES.__all__:
            raise ValueError(f"Engine {engine} not supported")
        if 'order_by' in engine:
            if type(engine['order_by']) != list and type(engine['order_by']) != str:
                raise ValueError(f"Engine order_by should be a list of strings or a string")
            if type(engine['order_by']) == list:
                for ob in engine['order_by']:
                    if ob not in columns:
                        raise ValueError(f"Order by {ob} not found in columns")
            if type(engine['order_by']) == str and engine['order_by'] not in columns:
                raise ValueError(f"Order by {engine['order_by']} not found in columns")
        if 'primary_key' in engine:
            if type(engine['primary_key']) != list and type(engine['primary_key']) != str:
                raise ValueError(f"Engine primary_key should be a list of strings or a string")
            if type(engine['primary_key']) == list:
                for pk in engine['primary_key']:
                    if pk not in columns:
                        raise ValueError(f"Primary key {pk} not found in columns")
            if type(engine['primary_key']) == str and engine['primary_key'] not in columns:
                raise ValueError(f"Primary key {engine['primary_key']} not found in columns")
        return True
    def create(self, table_name:str, columns_data:dict, engine_data:str, order_by:Any=None):
        """Create a table or materialized view
        Args:
            table_name (str): table to create
        """
        
        for column in columns_data.values():
            self.valid_column(column)
        self.valid_engine(engine_data, columns_data.keys())
        
        query = f"CREATE TABLE {table_name} ("
        for k,v in columns_data.items():
            query += f"{k} {v['type']}"
            if 'default' in v:
                query += f" DEFAULT {v['default']}"
            if 'nullable' in v:
                query += " NULLABLE"
            query += ","
        query = query[:-1]
        query += ")"
        if order_by:
            query += f" ORDER BY {order_by}"
        self.client.execute(query)

    def drop(self, table_name:str):
        """Drop a table or materialized view
        Args:
            obj (object): object to create
        """
        query = f"DROP TABLE {table_name}"
        self.client.execute(query)

    def create_all(self):
        """Create all tables and materialized views
        """
        pass

    def drop_all(self):
        """Drop all tables and materialized views
        """
        pass