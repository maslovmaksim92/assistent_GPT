# gpt_handler.py
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_gpt(message: str) -> str:
    try:
        messages = [
            {"role": "system", "content": "Ты полезный AI-помощник, улучшаешь код и создаешь продукты."},
            {"role": "user", "content": message},
        ]
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Ошибка при обращении к GPT]: {e}"
