from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_name =Column(String(255))#제품명
    finish = Column(String(255))#색상
    storage_capacity = Column(String(255))#용량 메모리 , 용량 따로 빼기 
    size_and_weight = Column(String(255))#외관 크기
    display = Column(String(500))# 디스플레이 크기
    chip = Column(String(100))# 프로세서 
    releaseDate = Column(String(255))#출시일
    #연결 단자 

