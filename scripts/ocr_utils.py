from PIL import Image
import pytesseract
from io import BytesIO

def ocr_image_from_bytes(image_bytes):
    """
    Run OCR on image bytes and return extracted text.
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        text = pytesseract.image_to_string(img).strip()
        return text
    except Exception as e:
        print(f"❌ OCR failed: {e}")
        return ""

def ocr_image_from_pil(img):
    """
    Run OCR on a PIL Image object.
    """
    try:
        text = pytesseract.image_to_string(img).strip()
        return text
    except Exception as e:
        print(f"❌ OCR failed: {e}")
        return ""
