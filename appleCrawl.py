import requests
from bs4 import BeautifulSoup
from utils.image_utils import clean_device_name, download_image,replace_hyphen_with_space,filterd_iPhone_path,extract_image_urls
from utils.css_utils import fetch_css_content, extract_image_urls_from_css
from urllib.parse import urljoin

def initialize_device_result(result, device_name):
    if device_name not in result:
        result[device_name] = {}

def crawl_apple_data(url,device_version):
    result = {}
    device_names = []

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        header_row = soup.find('div', class_='techspecs-header-row')
        if header_row:
            column_headers = header_row.find_all('div', class_='techspecs-columnheader')
            for column_header in column_headers:
                device_name = column_header.get_text(strip=True)
                cleaned_device_name = clean_device_name(device_name.lower())
                device_names.append(cleaned_device_name)
        rows = soup.find_all(class_='techspecs-row')
        for row in rows:
            rowheader = row.find(class_='techspecs-rowheader')
            if rowheader:
                rowheader_text = rowheader.get_text(strip=True)
                if rowheader_text == '칩':
                    ul = row.find('ul', class_='techspecs-list')
                    if ul:
                        chip_data = [li.get_text(strip=True) for li in ul.find_all('li', role='listitem')]
                        for device_name in device_names:
                            initialize_device_result(result, device_name)
                            result[device_name][rowheader_text] = chip_data
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
                                    initialize_device_result(result, device_name)
                                    if rowheader_text not in result[device_name]:
                                        result[device_name][rowheader_text] = []
                                    result[device_name][rowheader_text].append(f"{key}: {value}")
                elif rowheader_text == '마감': 
                    finish_columns = rowheader.find_next_siblings('div', role='cell gridcell')
                    for idx, finish_column in enumerate(finish_columns):
                        content_wrapper = finish_column.find('div', class_='content-wrapper')
                        if content_wrapper:
                            finishs = content_wrapper.find_all('p')
                            if finishs:
                                color = finishs[0].get_text(strip=True)
                                finish = finishs[1].get_text(strip=True).replace('<br>', ' ')
                                if idx < len(device_names):
                                    device_name = device_names[idx]
                                    initialize_device_result(result, device_name)
                                    result[device_name]['색상'] = color
                                    result[device_name]['마감'] = finish
                        else: #iphone이 하나일 경우
                            content = finish_column.find_all('div')
                            finishs = content[0].find_all('p')
                            if finishs:
                                color = finishs[1].get_text(strip=True)
                                finish = finishs[2].get_text(strip=True).replace('<br>', ' ')
                                if idx < len(device_names):
                                    device_name = device_names[idx]
                                    initialize_device_result(result, device_name)
                                    result[device_name]['색상'] = color
                                    result[device_name]['마감'] = finish

                elif rowheader_text == '크기 및 무게2':
                    size_columns = rowheader.find_next_siblings('div', role='cell gridcell')
                
                    for idx, size_column in enumerate(size_columns):
                        figure = size_column.find('figure')
                        weight_div = size_column.find('div', class_='weight-wrapper')

                        # 크기 정보 추출
                        size = {}
                        if figure:
                            figcaptions = figure.find_all('figcaption')
                            for figcaption in figcaptions:
                                strong = figcaption.find('strong')
                                if strong:
                                    key = strong.get_text(strip=True).replace(':', '')
                                    value = figcaption.find('p').get_text(strip=True)
                                    size[key] = value

                        # 무게 정보 추출
                        weight = ''
                        if weight_div:
                            weight_strong = weight_div.find('strong', class_='weight-copy')
                            weight_p = weight_div.find('p', class_='weight-copy')
                            if weight_strong and weight_p:
                                weight = weight_p.get_text(strip=True)

                        # 기기 이름 찾기
                        if idx < len(device_names):
                            device_name = device_names[idx]
                            initialize_device_result(result, device_name)
                            
                            # '가로', '세로', '두께', '무게'를 result[device_name]에 저장
                            if '가로' in size:
                                result[device_name]['가로'] = size['가로']
                            if '세로' in size:
                                result[device_name]['세로'] = size['세로']
                            if '두께' in size:
                                result[device_name]['두께'] = size['두께']
                            if weight:
                                result[device_name]['무게'] = weight
                # '디스플레이' 섹션을 처리하는 코드 추가
                elif rowheader_text == '디스플레이':
                    display_columns = rowheader.find_next_siblings('div', role='cell gridcell')

                    for idx, display_column in enumerate(display_columns):
                        # 기기 이름 찾기
                        if idx < len(device_names):
                            device_name = device_names[idx]
                            initialize_device_result(result, device_name)
                            
                            # 디스플레이 정보 추출
                            ul_tag = display_column.find('ul', class_='techspecs-list')
                            if ul_tag:
                                li_tags = ul_tag.find_all('li')
                                if len(li_tags) >= 3:
                                    display = li_tags[0].get_text(strip=True)
                                    diagonal = li_tags[1].get_text(strip=True)
                                    resolution = li_tags[2].get_text(strip=True)

                                    result[device_name]['디스플레이'] = display
                                    result[device_name]['대각선'] = diagonal
                                    result[device_name]['해상도'] = resolution


                else:
                    columns = row.find_all(class_='techspecs-column')
                    if len(columns) == len(device_names):
                        for idx, device_name in enumerate(device_names):
                            if device_name not in result:
                                result[device_name] = {}
                            result[device_name][rowheader_text] = columns[idx].get_text(strip=True)

        if device_version == "iphone-15-pro":
                image_urls =extract_image_urls(soup)
        else : 
            filterd_path = filterd_iPhone_path(device_version)
            css_url = f'https://www.apple.com/v/{device_version}/{filterd_path}/built/styles/specs.built.css'
            css_content = fetch_css_content(css_url)
            image_urls = extract_image_urls_from_css(css_content, device_version)

            # Download images
        for image_url in image_urls:
            if image_url:
                    # Convert relative URL to absolute URL if needed
                full_image_url = urljoin('https://www.apple.com', image_url)
                formatted_device_version = replace_hyphen_with_space(device_version)
                for device_name in device_names:
                    formatted_device_name = replace_hyphen_with_space(device_name.lower())
                    if formatted_device_version in formatted_device_name:
                        print(f"Downloading image from: {full_image_url}")
                        image_path = download_image(full_image_url, device_name)
                        if image_path:
                            initialize_device_result(result, device_name)
                            result[device_name]["이미지"] = image_path

    return result
