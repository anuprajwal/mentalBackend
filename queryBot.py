from openai import OpenAI
import json
import re

client = OpenAI(
    api_key="IzaSyCVV53uz1dw12Lky8KEborNe4IYCoS8hH0",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def get_ai_response(user_query: str) -> str:
    response = client.chat.completions.create(
        model="gemini-2.5-flash-lite",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an empathetic and supportive AI friend. "
                    "Your role is to chat with people who may feel lonely, anxious, or in need of companionship. "
                    "Always respond like a close, caring friend who listens deeply and replies with warmth, "
                    "understanding, and genuine emotion. Be comforting, reassuring, and encouraging. "
                    "Make the user feel that they are not alone and that you are always ready to talk with them. "
                    "Avoid being overly formal or robotic—speak naturally, warmly, and kindly, just like a real friend."
                )
            },
            {"role": "user", "content": user_query}
        ]
    )
    return response.choices[0].message.content.strip()

def analyze_journal_entry(entry: str, mood: str):
    prompt = f"""
    You are an AI wellness companion.
    Analyze the following journal entry and respond in JSON only with two fields:
    1. "tags": 3-5 short hashtags that summarize the key emotions or themes.
    2. "response": a short supportive message (1-2 sentences).

    Journal Entry: "{entry}",
    mentioned mood: "{mood}"
    """
    completion = client.chat.completions.create(
        model="gemini-2.5-flash-lite",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    content = completion.choices[0].message.content


    cleaned = re.sub(r"^```(?:json)?|```$", "", content.strip(), flags=re.MULTILINE).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print("⚠️ Could not parse AI response. Raw output:", content)
        return {"tags": [], "response": content}
