from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from utils.image_utils import download_image



def crawl_samsung_data(url, device_name):
    # Web driver setup
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    # Result dictionary to store extracted data
    result = {
        '디스플레이': [],
        '프로세서': [],
        '메모리/스토리지(저장 용량)': [],
        '외관 사양': [],
        '상품 기본정보': [],
        '색상': [],
        '이미지':[]
    }
    
    try:
        driver.get(url)
        spec_items = driver.find_elements(By.CLASS_NAME, 'spec-item')
        for spec_item in spec_items:
            tab_product = spec_item.find_element(By.CLASS_NAME, 'fp-spec__tab-product')
            button = tab_product.find_element(By.TAG_NAME, 'button')
            driver.execute_script("arguments[0].click();", button)
           
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
                                description_text = description.get_text(strip=True)
                                if '메모리' in term_text or '스토리지' in term_text:
                                    result['메모리/스토리지(저장 용량)'].append(description_text)
                                elif '디스플레이' in term_text:
                                    result['디스플레이'].append(description_text)
                                elif '프로세서' in term_text:
                                    result['프로세서'].append(description_text)
                                elif '외관' in term_text:
                                    result['외관 사양'].append(description_text)
                                elif '상품 기본정보' in term_text:
                                    result['상품 기본정보'].append(description_text)
        
        
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
    finally:
        # Quit the web driver
        driver.quit()

    # Applying set to each list to remove duplicates
    for key in result:
        result[key] = list(set(result[key]))
    
    # Return data in the format {device_name: result}
    return {device_name: result}

