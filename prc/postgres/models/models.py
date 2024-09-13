from sqlalchemy import Column, UniqueConstraint, Identity

from prc.postgres.base import Base
from prc.postgres.backend.types import (
    Integer, 
    String,
    DateTime,
    Boolean
)
import datetime
class HackerNews(Base):
    __tablename__ = 'hacker_news'
    
    id = Column(Integer(), primary_key=True)
    text = Column(String(100))
    counter = Column(Integer())
    state = Column(Boolean())
    created_at = Column(DateTime())
    updated_at = Column(DateTime())

    
    __table_args__ = ()
    
    def __init__(self, id, text, created_at=datetime.datetime.now(), updated_at=datetime.datetime.now()):
        self.id = id
        self.text = text
        self.created_at = created_at
        self.updated_at = updated_at
    
    def __repr__(self):
        params = {
            "id": self.id,
            "text": self.text,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        params_str = ", ".join([f"{k}={v}" for k, v in params.items()])
        return f"<HackerNews({params_str})>"