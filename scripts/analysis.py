import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Split long text into chunks of N words
def chunk_text(text, max_words=1500):
    words = text.split()
    for i in range(0, len(words), max_words):
        yield " ".join(words[i:i+max_words])

# Analyze a single chunk
def analyze_chunk(chunk_text, chunk_num):
    prompt = f"""
You are reviewing part {chunk_num} of a training session's content.
Please provide feedback on:
1. Clarity and structure
2. Relevance to topic
3. Engagement level
4. Suggestions for improvement


Text Content:
{chunk_text}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert training reviewer AI."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()

# Analyze all content in chunks and summarize
def analyze_training_material_with_gpt(text, images_ocr_texts=None, session_title=None, session_description=None):
    print("🔍 Chunking training material...")
    full_text = f"Session Title: {session_title}\nDescription: {session_description}\n{text}"
    ocr_text = "\n".join(images_ocr_texts or [])
    combined = full_text + "\n\nImage Content:\n" + ocr_text

    chunks = list(chunk_text(combined, max_words=1500))
    feedbacks = []

    for i, chunk in enumerate(chunks):
        print(f"🧠 Analyzing chunk {i+1}/{len(chunks)}...")
        try:
            feedback = analyze_chunk(chunk, i + 1)
            feedbacks.append(f"🧩 Feedback for part {i+1}:\n{feedback}")
        except Exception as e:
            feedbacks.append(f"❌ Error in chunk {i+1}: {str(e)}")

    # Combine feedbacks
    final_prompt = f"""
Here is the compiled feedback from all parts of a training session:

{chr(10).join(feedbacks)}

Based on these, summarize overall feedback for the session in a concise report.
"""

    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a training program evaluator AI."},
            {"role": "user", "content": final_prompt}
        ],
        temperature=0.5,
    )

    return final_response.choices[0].message.content.strip()
