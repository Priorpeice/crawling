from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True, autoincrement=True)
    finish = Column(String(255))
    storage_capacity = Column(String(255))
    size_and_weight = Column(String(255))
    display = Column(String(500))
    chip = Column(String(100))
