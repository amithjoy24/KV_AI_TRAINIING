from googleapiclient.discovery import build
from .drive_utils import get_credentials

def extract_text_from_gdoc(document_id):
    service = build('docs', 'v1', credentials=get_credentials())
    doc = service.documents().get(documentId=document_id).execute()
    text = ""

    for element in doc.get("body", {}).get("content", []):
        if "paragraph" in element:
            for elem in element["paragraph"].get("elements", []):
                text += elem.get("textRun", {}).get("content", "")

    return text.strip()
