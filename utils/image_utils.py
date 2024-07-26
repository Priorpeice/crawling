import requests
import os

def replace_hyphen_with_space(text):
    result = text.replace('-', ' ')
    result = result.replace('p', 'P')
    return result

def clean_device_name(device_name):
    device_name = device_name.replace('\xa0', '-').strip()
    device_name = replace_hyphen_with_space(device_name)
    return device_name

def download_image(url, device_name):
    if not url:
        return None
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs('images', exist_ok=True)
        file_path = f'images/{device_name.replace(" ", "_")}.jpg'
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return file_path
    else:
        print(f"Failed to download image from {url}")
    return None

def filterd_iPhone_path(device_version):
    path = "i"
    if device_version == "iphone-15" :
        path = "c"
    return path

def extract_image_urls(soup):
    image_urls = []

    picture_tags = soup.find_all('picture')
    for picture in picture_tags:       
        img_tag = picture.find('img')
        if img_tag:
            src = img_tag.get('src')
            if src and 'hero' in src and src.endswith('.jpg'):
                image_urls.append(src)
    
    return image_urls