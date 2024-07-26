import requests
from bs4 import BeautifulSoup
from utils.image_utils import clean_device_name, download_image,replace_hyphen_with_space,filterd_iPhone_path,extract_image_urls
from utils.css_utils import fetch_css_content, extract_image_urls_from_css
from urllib.parse import urljoin

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
                            if device_name not in result:
                                result[device_name] = {}
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
                                    if device_name not in result:
                                        result[device_name] = {}
                                    if rowheader_text not in result[device_name]:
                                        result[device_name][rowheader_text] = []
                                    result[device_name][rowheader_text].append(f"{key}: {value}")
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
                            if device_name not in result:
                                result[device_name] = {}
                            result[device_name]["이미지"] = image_path

    return result
