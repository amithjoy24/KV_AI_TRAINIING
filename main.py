import os
import sys


from scripts.file_processing import extract_from_file
from scripts.analysis import analyze_training_material_with_gpt
from scripts.url_processing import extract_content_from_url



def handle_file(file_path):
    print(f"\n📄 Processing file: {file_path}")
    text, images = extract_from_file(file_path)
    ocr_texts = [img['ocr_text'] for img in images if img['ocr_text']]
    return text, ocr_texts

def handle_url(url):
    result = extract_content_from_url(url)
    if result is None:
        return "", []
    # Extract what you want from dict:
    text = result.get("text", "")
    images = result.get("images", [])
    return text, images


def analyze_session(inputs, session_title=None, session_description=None):
    all_text = ""
    all_ocr_texts = []

    for input_path in inputs:
        if input_path.startswith("http"):
            text, ocrs = handle_url(input_path)
        elif os.path.isfile(input_path):
            text, ocrs = handle_file(input_path)
        else:
            print(f"⚠️ Skipping invalid input: {input_path}")
            continue

        all_text += f"\n\n{text}"
        all_ocr_texts.extend(ocrs)

    print("\n🤖 Generating GPT analysis...\n")
    feedback = analyze_training_material_with_gpt(
        text=all_text,
        images_ocr_texts=all_ocr_texts,
        session_title=session_title,
        session_description=session_description,
    )

    print("📝 === Feedback Report ===\n")
    print(feedback)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <file_or_url1> <file_or_url2> ...")
        sys.exit(1)

    # Optional metadata
    session_title = "MACHINE LEARNING"
    session_description = "This session is for ML."

    inputs = sys.argv[1:]
    analyze_session(inputs, session_title, session_description)
