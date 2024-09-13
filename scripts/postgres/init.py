import prc.postgres.models as models
from prc.postgres.backend import PostgresSQLAlchemyWrapper as Client

client = Client()

for model_name in models.__all__:
    model = getattr(models, model_name)
    if client.has_table(model):
        print(f"Table {model.__tablename__} already exists, dropping it")
        client.drop(model)
    print(f"Creating table {model.__tablename__}")
    client.create(model)