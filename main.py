from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from device import Base, Device
from appleCrawl import crawl_apple_data
from samsungCrawl import crawl_samsung_data
import re

def extract_device_name_from_url(url):
    pattern = re.compile(r'galaxy-[\w-]+')
    match = pattern.search(url)
    return match.group() if match else 'Unknown Device'

DATABASE_URI = 
engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def save_to_db(data, column_mapping):
    session = Session()
    print(data)
    for device_name, specs in data.items():
        spec = Device(device_name=device_name)  # 디바이스 이름 설정
        for key, value in specs.items():
            if key in column_mapping:
                column_name = column_mapping[key]
                if isinstance(value, list):
                    value = ', '.join(value)
                setattr(spec, column_name, value)
        session.add(spec)
    
    session.commit()
    session.close()

def crawl_and_save(url, brand,device_name):
    if brand == 'apple':
        result = crawl_apple_data(url,device_name)
        column_mapping = {
            '색상': 'color',
            '저장 용량1': 'storage_capacity',
            '가로': 'width',
            '세로': 'length',
            '두께': 'height',
            '무게': 'weight',
            '디스플레이': 'display',
            '대각선': 'diagonal',
            '해상도': 'resolution',
            '칩': 'chip',
            '상품정보표시':'release_date',
            '이미지': 'images'
        }
    elif brand == 'samsung':
        column_mapping = {
            '색상': 'color',
            '저장 용량': 'storage_capacity',
            '가로': 'width',
            '세로': 'length',
            '두께': 'height',
            '무게': 'weight',
            '디스플레이': 'display',
            '대각선': 'diagonal',
            '해상도': 'resolution',
            '프로세서': 'chip',
            '출시년월':'release_date',
            '이미지': 'images'
        }
        result = crawl_samsung_data(url, device_name)
    else:
        raise ValueError("지원하지 않는 브랜드입니다.")
    
    save_to_db(result, column_mapping)
    
    for key, value in result.items():
        print(f"{key} : {value}")

if __name__ == "__main__":
    apple_url = 'https://www.apple.com/kr/{}/specs/'
    apple_device_identifier ='iphone-14'
    apple_url=apple_url.format(apple_device_identifier)
    
    samsung_url= 'https://www.samsung.com/sec/smartphones/{}/specs/'
    device_identifier = 'galaxy-s24-ultra'
    samsung_url = samsung_url.format(device_identifier)   

    samsung_device_name = extract_device_name_from_url(samsung_url)

    print("애플 사양 크롤링 및 저장")
    crawl_and_save(apple_url, 'apple',apple_device_identifier)
    
    print("\n삼성 사양 크롤링 및 저장")
    crawl_and_save(samsung_url, 'samsung',samsung_device_name)
