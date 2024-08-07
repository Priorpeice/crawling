from sqlalchemy import Column, Integer, String , Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_name =Column(String(255))#제품명
    finish = Column(String(255))#마감처리
    color = Column(String(255))#색상
    storage_capacity = Column(String(255))#용량 메모리 , 용량 따로 빼기 
    width = Column(String(50))#가로
    length = Column(String(50))#세로
    height = Column(String(50))#높이
    weight = Column(String(50))#무게
    display = Column(String(255))# 디스플레이 
    diagonal = Column(String(50))# 대각선 길이
    resolution = Column(String(50))# 해상도
    chip = Column(String(100))# 프로세서 
    release_date = Column(String(255))#설명
    images = Column(Text)
    #연결 단자 

