from readability import Document
from bs4 import BeautifulSoup

def extract_google_docs_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    # Extract text from Google Docs specific classes
    text_blocks = soup.find_all("div", class_="kix-lineview-content")
    texts = [block.get_text(separator=" ", strip=True) for block in text_blocks]
    full_text = "\n".join(texts)
    return full_text

def extract_main_content(url, html=None):
    if "docs.google.com/document" in url:
        # For Google Docs, pass in HTML from Selenium or requests
        if not html:
            raise ValueError("HTML content required for Google Docs extraction")
        return "Google Docs Content", extract_google_docs_content(html)
    else:
        # For normal pages, use readability
        doc = Document(html)
        title = doc.title()
        main_html = doc.summary()
        soup = BeautifulSoup(main_html, 'html.parser')
        main_text = soup.get_text(separator="\n", strip=True)
        return title, main_text

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def load_page_with_selenium(url):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        time.sleep(5)  # wait for content to load
        return driver.page_source
    finally:
        driver.quit()

url = "https://docs.google.com/document/d/1CenMpL_ir2MbBzOCWX5sYJIEELOpbBSfnZoRzyiECo4/edit"
html_content = load_page_with_selenium(url)
title, main_text = extract_main_content(url, html_content)

print("Title:", title)
print("Extracted Text Snippet:", main_text[:1000])
