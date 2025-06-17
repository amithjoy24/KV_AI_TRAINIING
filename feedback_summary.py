from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chunk_list(lst, chunk_size=10):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def summarize_chunk(feedback_chunk, role_name):
    text = "\n- ".join(feedback_chunk)
    prompt = f"""
You are an expert analyst. Summarize the following {role_name} feedback points into a concise paragraph:

- {text}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

def hierarchical_summarize(feedback_list, role_name):
    # Step 1 & 2: Chunk & summarize each chunk
    chunk_summaries = []
    for chunk in chunk_list(feedback_list, chunk_size=10):
        summary = summarize_chunk(chunk, role_name)
        chunk_summaries.append(summary)
    
    # Step 3 & 4: Summarize combined chunk summaries if more than 1 chunk
    if len(chunk_summaries) == 1:
        return chunk_summaries[0]
    else:
        combined_text = "\n- ".join(chunk_summaries)
        prompt = f"""
You are an expert analyst. Summarize the following summarized {role_name} feedback points into a concise paragraph:

- {combined_text}
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()

def final_combined_analysis(student_summary, trainer_summary):
    prompt = f"""
You are an expert educational analyst.

Here is the summary of student feedback about a session:
{student_summary}

Here is the summary of trainers and moderators feedback about a student:
{trainer_summary}

Please provide:

1. An integrated analysis highlighting the overall perfomance of trainers and the quality of sessions.
2. For each student analyze the feedback given by trainers and moderators and give analysis on how the student can improve where his weakness and strength lies.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

# Putting it all together

def analyze_large_feedback(student_feedback, trainer_moderator_feedback):
    student_summary = hierarchical_summarize(student_feedback, "student")
    trainer_summary = hierarchical_summarize(trainer_moderator_feedback, "trainer and moderator")

    final_report = final_combined_analysis(student_summary, trainer_summary)
    return final_report


# Example usage

student_feedback = [
    # large list of student feedback strings
    'The session was great',
    'The session was fun.'
]

trainer_moderator_feedback = [
    # large list of trainer/mod feedback strings
    'The student was great'
    'The student was an idiot'
]

report = analyze_large_feedback(student_feedback, trainer_moderator_feedback)
print(report)
