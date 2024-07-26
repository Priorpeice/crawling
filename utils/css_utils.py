import re
import requests

def fetch_css_content(css_url):
    response = requests.get(css_url)
    if response.status_code == 200:
        return response.text
    print(f"Failed to fetch CSS content from {css_url}")
    return ''

def extract_image_urls_from_css(css_content, device_version):
    # CSS class patterns to search for image URLs
    fillterd_device_version=return_iPhone(device_version)
    class_patterns = [
        f'.section-finish .image-finish-{fillterd_device_version}',
        f'.section-finish .image-finish-{fillterd_device_version}-plus'
    ]

    urls = []
    for pattern in class_patterns:
        # Find all URLs with the specified pattern
        regex_pattern = re.compile(rf'{re.escape(pattern)}\s*{{\s*background-image:\s*url\(([^)]+)\)\s*}}')
        matches = regex_pattern.findall(css_content)
        urls.extend(matches)

    return urls

def return_iPhone(device_version):
    result= device_version
    if device_version == "iphone-15" :
        result = "iphone"
    if device_version == "iphone-15-plus":
        result ="iphone-plus"
    return result

