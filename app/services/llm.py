from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

async def generate_draft(link: str, comment: str) -> str:
    if not settings.openai_api_key:
        return f"Link: {link}\nComment: {comment}\n\n(No OpenAI API key configured, so this is a basic draft.)"

    prompt = f"""
You are an assistant for the IOI team Bolivia. Your task is to draft an official announcement message.
The user provided the following link: {link}
And the following comment/instructions: {comment}

Please generate a professional, encouraging, and clear message that will be sent via Email, WhatsApp, and Telegram.
Include the link naturally in the text.
The message should be in Spanish.
Keep it concise but informative.
"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for the IOI Team Bolivia."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating draft: {e}\n\nFallback draft:\nLink: {link}\nComment: {comment}"
