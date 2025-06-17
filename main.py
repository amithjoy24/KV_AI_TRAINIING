import os
import sys


from scripts.file_processing import extract_from_file
from scripts.analysis import analyze_training_material_with_gpt
from scripts.url_processing import extract_content_from_url
from scripts.google_url_processing import identify_google_service,google_to_pdf



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
    temp_files_to_delete = []

    for input_path in inputs:
        if input_path.startswith("http"):
            service_type = identify_google_service(input_path)
            if service_type in {"docs", "sheets", "slides"}:
                print(f"📄 Detected Google {service_type} link. Downloading as PDF...")
                saved_pdf_path = google_to_pdf(input_path)
                print(f"SAVED PATH : {saved_pdf_path}")
                if saved_pdf_path:
                    text, ocrs = handle_file(saved_pdf_path)
                    temp_files_to_delete.append(saved_pdf_path)  # Track for deletion
                else:
                    print(f"⚠️ Failed to download Google file: {input_path}")
                    continue
            else:
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

    # 🧹 Clean up temporary files
    for file_path in temp_files_to_delete:
        try:
            os.remove(file_path)
            print(f"🧹 Deleted temporary file: {file_path}")
        except Exception as e:
            print(f"⚠️ Failed to delete {file_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <file_or_url1> <file_or_url2> ...")
        sys.exit(1)

    # Optional metadata
    session_title = "MACHINE LEARNING"
    session_description = "This session is for LLMS for students who are already familiar with basics."

    inputs = sys.argv[1:]
    analyze_session(inputs, session_title, session_description)

        
