import requests
from bs4 import BeautifulSoup

def crawl_data(url):
    result = {}
    
    # requests를 사용하여 웹 페이지에 GET 요청을 보냄
    response = requests.get(url)

    # 요청이 성공했는지 확인
    if response.status_code == 200:
        # BeautifulSoup을 사용하여 HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 클래스가 'techspecs-row'인 모든 요소를 찾음
        rows = soup.find_all(class_='techspecs-row')
        
        # 'techspecs-row' 클래스를 가진 요소들에 대해 반복
        for row in rows:
            # 해당 행에서 'techspecs-rowheader' 클래스를 가진 요소를 찾음
            rowheader = row.find(class_='techspecs-rowheader')
            if rowheader:
                # 현재 행에서 'techspecs-column' 클래스를 가진 요소를 찾음
                column = row.find(class_='techspecs-column') or row.find(class_='cell gridcell')
                if column:
                    # 현재 행의 'techspecs-rowheader' 텍스트를 key로, 'techspecs-column' 또는 'cell gridcell' 텍스트를 value로 저장
                    result[rowheader.get_text(strip=True)] = column.get_text(strip=True)
    
    return result
