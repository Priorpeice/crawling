from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from utils.image_utils import download_image



def crawl_samsung_data(url, device_name):
#  # Web driver setup
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service)
    driver = webdriver.Chrome()
    
    # Result dictionary to store extracted data
    result = {
        '디스플레이': [],
        '해상도': [],
        '대각선': [],
        '프로세서': [],
        '저장 용량': set(),
        '가로':[],
        '세로': [],
        '두께': [],
        '무게': [],
        '출시년월': [],
        '색상': [],
        '이미지':[]
    }
    
    try:
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        specs_div = soup.find(class_='fp-spec__content-table js-spec-data')
            
        if specs_div:
            spec_table_wraps = specs_div.find_all(class_='spec-table-wrap')
            for spec_table_wrap in spec_table_wraps:
                spec_tables = spec_table_wrap.find_all(class_='spec-table')
                for spec_table in spec_tables:
                    dls = spec_table.find_all('dl')
                    for dl in dls:
                        terms = dl.find_all('dt')
                        descriptions = dl.find_all('dd')
                        for term, description in zip(terms, descriptions):
                            term_text = term.get_text(strip=True)
                            description_text = description.get_text(strip=True).replace('&nbsp;', '')
                            if '디스플레이' in term_text:
                                ol_tags = description.find_all('ol')
                                for ol in ol_tags:
                                    li_tags = ol.find_all('li')
                                    for li in li_tags:
                                        spec_title = li.find('strong', class_='spec-title')
                                        spec_desc = li.find('p', class_='spec-desc')

                                        if spec_title and spec_desc:
                                            title_text = spec_title.get_text(strip=True)
                                            desc_text = spec_desc.get_text(strip=True).replace('&nbsp;', '')

                                            if '크기' in title_text:
                                                numeric_part = ''.join(filter(lambda c: c.isdigit() or c == '.', desc_text))
                                                try:
                                                    value_mm = float(numeric_part)
                                                    value_cm = value_mm / 10  
                                                    result["대각선"] = f"{value_cm:.1f} cm"
                                                except ValueError:
                                                    result["대각선"] = desc_text

                                            elif '해상도' in title_text:
                                                result["해상도"] = desc_text
                                            elif '종류' in title_text:
                                                result["디스플레이"] = desc_text

                            elif '프로세서' in term_text:
                                result['프로세서'].append(description_text)
                            elif '외관' in term_text:
                                ol_tags = description.find_all('ol')
                                for ol in ol_tags:
                                    li_tags = ol.find_all('li')
                                    for li in li_tags:
                                        spec_title = li.find('strong', class_='spec-title')
                                        spec_desc = li.find('p', class_='spec-desc')

                                        if spec_title and spec_desc:
                                            title_text = spec_title.get_text(strip=True)
                                            desc_text = spec_desc.get_text(strip=True).replace('&nbsp;', '')

                                            if '크기' in title_text:
                                                # '크기' 값을 세로, 가로, 두께로 나누기
                                                dimensions = desc_text.split(' x ')
                                                if len(dimensions) == 3:
                                                    result['세로'] = dimensions[0].strip()+"mm"
                                                    result['가로'] = dimensions[1].strip()+"mm"
                                                    result['두께'] = dimensions[2].strip()+"mm"

                                            elif '무게' in title_text:
                                                # '무게' 값을 저장하기
                                                result['무게'] = desc_text.strip()+"g"
                            
                            elif '상품 기본정보' in term_text:
                                ol_tags = description.find_all('ol')
                                for ol in ol_tags:
                                    li_tags = ol.find_all('li')
                                    for li in li_tags:
                                        spec_title = li.find('strong', class_='spec-title')
                                        spec_desc = li.find('p', class_='spec-desc')

                                        if spec_title and spec_desc:
                                            title_text = spec_title.get_text(strip=True)
                                            desc_text = spec_desc.get_text(strip=True).replace('&nbsp;', '')

                                        if '동일모델' in title_text:
                                            result["출시년월"] = desc_text

        # 색상 크롤링을 위한 dom 조작
        color_buttons = driver.find_elements(By.CLASS_NAME, 'js-design-tab')
        for button in color_buttons:
            driver.execute_script("arguments[0].click();", button)
    
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            design_table_ths = soup.find_all(class_='fp-spec-design__table-th')
            for th in design_table_ths:
                color_header = th.get_text(strip=True)
                if color_header == '색상':
                    color_td = th.find_next_sibling(class_='fp-spec-design__table-td js-design-contents is-active')
                    if color_td:
                        color_list_div = color_td.find(class_='fp-spec-design__color-list')
                        if color_list_div:
                            figures = color_list_div.find_all('figure')
                            first_image_saved = False
                            for figure in figures:
                                figcaption = figure.find('figcaption')
                                img_tag = figure.find('img')
                                if figcaption:
                                    result['색상'].append(figcaption.get_text(strip=True))
                                if img_tag and not first_image_saved:
                                    img_src = img_tag['src']
                                    if img_src.startswith("//"):
                                        img_src = "https:" + img_src
                                    img_path = download_image(img_src, device_name)
                                    if img_path:
                                        result['이미지'].append(img_path)
                                    first_image_saved = True    
        # 저장 용량 크롤링을 위한 Dom 조작
        spec_button = driver.find_elements(By.CLASS_NAME, 'js-spec-tab')
        for button in spec_button:
            driver.execute_script("arguments[0].click();", button)

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            # 스토리지 정보 파싱
            spec_tables = soup.find_all('div', class_='spec-table-wrap is-visible')

            for table in spec_tables:
                dl_tags = table.find_all('dl')
                for dl in dl_tags:
                    dt = dl.find('dt')
                    if dt and '메모리/스토리지(저장 용량)' in dt.get_text(strip=True):
                        dd = dl.find('dd')
                        if dd:
                            ol = dd.find('ol')
                            if ol:
                                li_tags = ol.find_all('li')
                                for li in li_tags:
                                    spec_title = li.find('strong', class_='spec-title')
                                    spec_desc = li.find('p', class_='spec-desc')
                                    if spec_title and spec_desc:
                                        title_text = spec_title.get_text(strip=True)
                                        desc_text = spec_desc.get_text(strip=True).replace('&nbsp;', '')  # &nbsp;를 공백으로 대체
                                        # '스토리지(저장 용량)'이 제목에 포함되어 있고, '사용'이 제목에 포함되지 않은 경우에만 저장
                                        if '스토리지(저장 용량)' in title_text and '사용 가능한' not in title_text:
                                            result['저장 용량'].add(desc_text)


        
    finally:
        # Quit the web driver
        driver.quit()

    # Applying set to each list to remove duplicates
    for key in result:
        if isinstance(result[key], set):
            result[key] = list(result[key])
        elif isinstance(result[key], list):
            result[key] = list(set(result[key]))
    
    # Return data in the format {device_name: result}
    return {device_name: result}

