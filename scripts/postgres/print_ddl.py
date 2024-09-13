import prc.postgres.models
from scripts.utils import print_ddl

objs = [
    cls 
    for cls in map(
        lambda n: 
            getattr(prc.postgres.models, n),
            prc.postgres.models.__all__
        )
]
print_ddl(
    "postgresql", 
    objs
)