import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Split long text into chunks of N words
def chunk_text(text, max_words=1500):
    words = text.split()
    for i in range(0, len(words), max_words):
        yield " ".join(words[i:i + max_words])

# Analyze a single chunk with session focus
def analyze_chunk(chunk_text, chunk_num, session_topic):
    prompt = f"""
You are reviewing part {chunk_num} of a training session titled: "{session_topic}".

Your job is to strictly evaluate the following uploaded training material:

{chunk_text}

Provide a concise evaluation focusing on:
1. ✅ Clarity and completeness of the material.
2. ✅ How relevant the content is to the session topic: "{session_topic}".
3. ✅ Any missing concepts or subtopics that should be included to improve coverage.
4. ✅ Suggestions to enhance engagement or practical understanding.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional training material evaluator AI. Focus strictly on analyzing the uploaded material and give improvement suggestions."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
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
        print(f"🧠 Analyzing chunk {i + 1}/{len(chunks)}...")
        try:
            feedback = analyze_chunk(chunk, i + 1, session_title)
            feedbacks.append(f"🧩 Feedback for part {i + 1}:\n{feedback}")
        except Exception as e:
            feedbacks.append(f"❌ Error in chunk {i + 1}: {str(e)}")

    # Combine feedbacks
    final_prompt = f"""
The following is feedback across parts of a training session titled "{session_title}":

{chr(10).join(feedbacks)}

Now:
- Combine all this feedback into a concise overall evaluation.
- Comment on how well the uploaded materials align with the topic.
- Suggest specific content, examples, or sections that could be added to enhance quality.
"""

    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a training program evaluator AI. Focus on topic alignment and material completeness."},
            {"role": "user", "content": final_prompt}
        ],
        temperature=0.4,
    )

    return final_response.choices[0].message.content.strip()
