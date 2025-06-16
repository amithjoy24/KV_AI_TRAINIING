import requests
from readability import Document
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from PIL import Image
from io import BytesIO
import pytesseract

# ---------- USE SELENIUM TO LOAD PAGE ----------
def fetch_with_selenium(url):
    print(f"🔍 Using Selenium to load: {url}")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(5)  # Let JS load
        return driver.page_source, driver.current_url  # Return resolved base URL too
    finally:
        driver.quit()

# ---------- PARSE MAIN ARTICLE CONTENT WITH READABILITY ----------
def parse_main_content_with_readability(html):
    doc = Document(html)
    title = doc.title()
    main_html = doc.summary()
    soup = BeautifulSoup(main_html, 'html.parser')
    main_text = soup.get_text(separator="\n", strip=True)
    return title, main_text

# ---------- PARSE IMAGES FROM ORIGINAL HTML ----------
def extract_images_from_html(html, base_url=None):
    soup = BeautifulSoup(html, 'html.parser')

    image_data = []
    for idx, img in enumerate(soup.find_all('img')):
        img_url = img.get('src')
        alt_text = img.get('alt', '').strip()

        if not img_url:
            continue

        if base_url and not img_url.startswith(('http', 'https')):
            from urllib.parse import urljoin
            img_url = urljoin(base_url, img_url)

        try:
            img_resp = requests.get(img_url, timeout=5)
            img_obj = Image.open(BytesIO(img_resp.content))

            if not alt_text:
                alt_text = pytesseract.image_to_string(img_obj).strip()

            image_data.append({
                "index": idx,
                "url": img_url,
                "alt_or_ocr": alt_text,
                "image_bytes": img_resp.content
            })
        except Exception as e:
            print(f"⚠️ Failed to load image: {img_url} — {e}")

    return image_data

# ---------- EXPOSED FUNCTION ----------
def extract_content_from_url(url):
    try:
        html, final_url = fetch_with_selenium(url)
        title, main_text = parse_main_content_with_readability(html)
        images = extract_images_from_html(html, base_url=final_url)
        return {
            "title": title,
            "text": main_text,
            "images": images
        }
    except Exception as e:
        print(f"❌ Extraction failed for {url} — {e}")
        return None
