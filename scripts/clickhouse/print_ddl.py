import prc.clickhouse.models
from scripts.utils import print_ddl

objs = [
    cls 
    for cls in map(
        lambda n: 
            getattr(prc.clickhouse.models, n),
            prc.clickhouse.models.__all__
        )
]
print_ddl(
    "clickhouse", 
    objs
)