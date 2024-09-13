import prc.clickhouse.models as models
from prc.clickhouse.backend import ClikchouseSQLAlchmeyWrapper as Client

client = Client(is_refelct=False)

for model_name in models.__all__:
    model = getattr(models, model_name)
    if client.is_table(model):
        if client.has_table(model):
            print(f"Table {model.__tablename__} already exists, dropping it")
            client.drop(model)
    else:
        if client.has_materialized_view(model):
            print(f"Materialized view already exists, dropping it")
            client.drop(model)