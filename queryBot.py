from openai import OpenAI

client = OpenAI(api_key="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")

def get_ai_response(user_query: str) -> str:

    response = client.chat.completions.create(
        model="gpt-4o-mini",
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
            {
                "role": "user",
                "content": user_query
            }
        ]
    )

    # Extract clean response text
    return response.choices[0].message.content.strip()
