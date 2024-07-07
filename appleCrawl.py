import requests
from bs4 import BeautifulSoup

def crawl_apple_data(url):
    result = {}
    device_names = []

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Header parsing to get device names
        header_row = soup.find('div', class_='techspecs-header-row')
        if header_row:
            column_headers = header_row.find_all('div', class_='techspecs-columnheader')
            for column_header in column_headers:
                device_names.append(column_header.get_text(strip=True))
        
        # Data parsing
        rows = soup.find_all(class_='techspecs-row')
        for row in rows:
            rowheader = row.find(class_='techspecs-rowheader')
            if rowheader:
                rowheader_text = rowheader.get_text(strip=True)
                
                # Handling '칩' section
                if rowheader_text == '칩':
                    ul = row.find('ul', class_='techspecs-list')
                    if ul:
                        chip_data = [li.get_text(strip=True) for li in ul.find_all('li', role='listitem')]
                        for device_name in device_names:
                            if device_name not in result:
                                result[device_name] = {}
                            result[device_name][rowheader_text] = chip_data
                
                # Handling '상품정보표시' section
                elif rowheader_text == '상품정보표시':
                    uls = row.find_all('ul', class_='techspecs-list-disc')
                    for ul in uls:
                        lis = ul.find_all('li', role='listitem')
                        for li in lis:
                            li_text = li.get_text(strip=True)
                            if ':' in li_text:
                                key, value = li_text.split(':', 1)
                                key = key.strip()
                                value = value.strip()
                                for device_name in device_names:
                                    if device_name not in result:
                                        result[device_name] = {}
                                    if rowheader_text not in result[device_name]:
                                        result[device_name][rowheader_text] = []
                                    result[device_name][rowheader_text].append(f"{key}: {value}")
                
                # Handling other sections
                else:
                    columns = row.find_all(class_='techspecs-column')
                    if len(columns) == len(device_names):
                        for idx, device_name in enumerate(device_names):
                            if device_name not in result:
                                result[device_name] = {}
                            result[device_name][rowheader_text] = columns[idx].get_text(strip=True)
    
    return result
