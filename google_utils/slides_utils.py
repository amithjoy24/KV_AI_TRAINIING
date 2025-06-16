from googleapiclient.discovery import build
from .drive_utils import get_credentials

def extract_text_from_gslides(presentation_id):
    service = build('slides', 'v1', credentials=get_credentials())
    pres = service.presentations().get(presentationId=presentation_id).execute()

    text = ""
    for slide in pres.get("slides", []):
        for element in slide.get("pageElements", []):
            if "shape" in element and "text" in element["shape"]:
                for elem in element["shape"]["text"]["textElements"]:
                    text += elem.get("textRun", {}).get("content", "")

    return text.strip()
