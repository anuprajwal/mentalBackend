import google.generativeai as genai
import json
import re

# Configure Gemini API key
# Get your key from https://aistudio.google.com/app/apikey
genai.configure(api_key="IzaSyC0pfgi2xhfSZ5RpADnPRFCou_6fmwzpY0")

# Create a model instance
chat_model = genai.GenerativeModel("gemini-1.5-flash")  # or gemini-1.5-pro for better quality


def get_ai_response(user_query: str) -> str:
    """
    Empathetic supportive response to a user query.
    """
    system_prompt = (
        "You are an empathetic and supportive AI friend. "
        "Your role is to chat with people who may feel lonely, anxious, or in need of companionship. "
        "Always respond like a close, caring friend who listens deeply and replies with warmth, "
        "understanding, and genuine emotion. Be comforting, reassuring, and encouraging. "
        "Make the user feel that they are not alone and that you are always ready to talk with them. "
        "Avoid being overly formal or robotic—speak naturally, warmly, and kindly, just like a real friend."
    )

    response = chat_model.generate_content(
        [system_prompt, user_query],
        generation_config={"temperature": 0.7}
    )

    return response.text.strip()


def analyze_journal_entry(entry: str, mood: str):
    """
    Analyze the journal entry → return JSON with hashtags + supportive response.
    """
    prompt = f"""
    You are an AI wellness companion.
    Analyze the following journal entry and respond in JSON only with two fields:
    1. "tags": 3-5 short hashtags that summarize the key emotions or themes.
    2. "response": a short supportive message (1-2 sentences).

    Journal Entry: "{entry}",
    mentioned mood: "{mood}"
    """

    completion = chat_model.generate_content(
        prompt,
        generation_config={"temperature": 0.7}
    )

    content = completion.text.strip()

    # Clean out ```json ... ``` if the model adds it
    cleaned = re.sub(r"^```(?:json)?|```$", "", content, flags=re.MULTILINE).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print("⚠️ Could not parse AI response. Raw output:", content)
        return {"tags": [], "response": content}
