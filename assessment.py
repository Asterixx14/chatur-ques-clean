import json
import os
import time
from bson import ObjectId
from openai import OpenAI
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Create OpenAI client using the new SDK
client = OpenAI(api_key=api_key)

CATEGORIES = ["culture_fit", "work_style", "ethics", "comprehensive"]

def get_prompt(q):
    return f"""
You are a helpful assistant classifying interview questions.

Task 1: Assign one of these categories to the question:
- culture_fit
- work_style
- ethics
- comprehensive

Task 2: If the question naturally references a company (like "our company", "this company", or any specific company name), replace it with {{company_name}}.  
If there is no natural reference, do not insert anything.

Return your answer as a JSON with two keys:
- "category": one of the above four
- "question": the updated question (with placeholder if needed)

Only return valid JSON. No explanation.
Question: "{q}"
"""

# Load all interview questions
with open("interview_questions.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

all_questions = [q.strip() for group in raw_data for q in group["questions"]]

results = []

for idx, question in enumerate(all_questions):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or gpt-3.5-turbo
            messages=[
                {"role": "user", "content": get_prompt(question)}
            ],
            temperature=0,
        )

        reply = response.choices[0].message.content.strip()
        parsed = json.loads(reply)

        category = parsed.get("category", "comprehensive")
        if category not in CATEGORIES:
            print(f"⚠️ Invalid category returned: {category}")
            category = "comprehensive"

        results.append({
            "id": str(ObjectId()),
            "question": parsed.get("question", question),
            "category": category
        })

        print(f"[{idx + 1}/{len(all_questions)}] ✅")
        time.sleep(1.1)

    except Exception as e:
        print(f"❌ Error on: {question}\n{e}")

# Save output
with open("categorized_questions.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("🎯 Done! Saved to categorized_questions.json")
