from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from device import Base, Device
from crawl import crawl_data

# MySQL 연결 설정
DATABASE_URI = 'mysql+pymysql://root:1234@localhost:3305/crwal'
engine = create_engine(DATABASE_URI)

# 테이블 생성
Base.metadata.create_all(engine)

# 세션 생성
Session = sessionmaker(bind=engine)
session = Session()

def crawl_and_save(url):
    result = crawl_data(url)
    
    # 크롤링한 데이터의 키와 컬럼을 매핑
    column_mapping = {
        '마감': 'finish',
        '저장 용량1': 'storage_capacity',
        '크기 및 무게2': 'size_and_weight',
        '디스플레이': 'display',
        '칩': 'chip'
    }
    
    # Device 객체 생성
    spec = Device()
    
    # 결과를 데이터베이스에 저장
    for key, value in result.items():
        if key in column_mapping:
            column_name = column_mapping[key]
            setattr(spec, column_name, value)

    # 데이터베이스에 추가
    session.add(spec)

    # 세션 커밋
    session.commit()

    # 세션 종료
    session.close()

    # 결과 출력
    for key, value in result.items():
        print(f"{key} : {value}")

if __name__ == "__main__":
    url = 'https://www.apple.com/kr/iphone-13/specs/'
    crawl_and_save(url)
