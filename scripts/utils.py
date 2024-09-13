from typing import List, Any
from clickhouse_sqlalchemy import MaterializedView
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy import create_mock_engine

def print_ddl(dialect_driver: str, objs: List[Any]) -> None:
    """Prints the DDL of the given objects.
        Creates a mock engine and dumps its DDL to stdout.
    Args:
        dialect_driver (str): the dialect driver to use for the mock engine (e.g. 'clickhouse')
        objs (List[Any]): the list of objects to print the DDL of (e.g. [MaterializedView, Table])
    """

    def dump(sql, *multiparams, **params):
        print(
            str(sql.compile(dialect=dialect_driver))
            .replace("\t", "")
            .replace("\n", ""),
            end=";",
        )

    engine = create_mock_engine(f"{dialect_driver}://", dump)
    for obj in objs:
        if type(obj) == MaterializedView:
            obj.create(bind=engine, checkfirst=True)
        elif type(obj) == DeclarativeMeta:
            obj.__table__.create(bind=engine, checkfirst=False)
        print("\n\n")