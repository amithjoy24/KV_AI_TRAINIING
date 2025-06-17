import os
import requests
from urllib.parse import urlparse, parse_qs
import time

def create_downloads_folder():
    os.makedirs("downloads", exist_ok=True)

def identify_google_service(url: str) -> str:
    if 'docs.google.com/document' in url:
        return 'docs'
    elif 'docs.google.com/spreadsheets' in url:
        return 'sheets'
    elif 'docs.google.com/presentation' in url:
        return 'slides'
    else:
        return 'unknown'

def extract_doc_id(url: str) -> str:
    if '/d/' in url:
        return url.split('/d/')[1].split('/')[0]
    parsed = urlparse(url)
    return parse_qs(parsed.query).get('id', [None])[0]

def build_export_url(doc_type: str, doc_id: str) -> str:
    if doc_type == 'docs':
        return f"https://docs.google.com/document/d/{doc_id}/export?format=pdf"
    elif doc_type == 'sheets':
        return f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=pdf"
    elif doc_type == 'slides':
        return f"https://docs.google.com/presentation/d/{doc_id}/export/pdf"
    return ""

def download_pdf(url: str, session: requests.Session) -> str | None:
    doc_type = identify_google_service(url)
    if doc_type == 'unknown':
        print(f"Unsupported URL: {url}")
        return None

    doc_id = extract_doc_id(url)
    if not doc_id:
        print(f"Could not extract doc ID from: {url}")
        return None

    export_url = build_export_url(doc_type, doc_id)
    if not export_url:
        print(f"Could not build export URL for: {url}")
        return None

    filename = f"{doc_type}_{doc_id[:8]}.pdf"
    filepath = os.path.join("downloads", filename)

    try:
        response = session.get(export_url)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"✅ Saved: {filepath}")
            return filepath
        else:
            print(f"❌ Failed to download PDF: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Error downloading: {e}")

    return None


def google_to_pdf(url):

    create_downloads_folder()
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})

    filepath = download_pdf(url, session)
    return filepath
        

