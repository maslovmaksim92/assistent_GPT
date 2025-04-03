import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROJECT_PATH = "./"


def generate_code_from_task(task: str) -> str:
    """
    Используется в wiki_task_updater.py для генерации кода по описанию задачи
    """
    print("[🧠] Отправка запроса в OpenAI (из wiki_task_updater)...")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ты опытный Python-разработчик. Ответ должен содержать только Python-код без пояснений."},
            {"role": "user", "content": task}
        ]
    )
    code = response.choices[0].message.content
    print("[✅] GPT сгенерировал код по задаче")
    return code


def write_code(idea: str, full_context: str = None) -> bool:
    try:
        print("[🧠] Отправка запроса в OpenAI...")

        messages = [
            {"role": "system", "content": "Ты — опытный Python-разработчик. Твоя задача — улучшить и оптимизировать код. Если предлагаешь изменить код, всегда используй чёткий формат: ```python FILE: filename.py\nкод```"},
            {"role": "user", "content": f"Вот описание задачи: {idea}"}
        ]

        if full_context:
            messages.append({"role": "user", "content": f"Вот текущий код проекта:\n{full_context}\n\nПредложи улучшения и верни файлы с новым кодом в формате: ```python FILE: filename.py\nновый код```"})

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.4
        )

        generated = response.choices[0].message.content.strip()
        with open("./code_suggestion.md", "w", encoding="utf-8") as f:
            f.write(generated)

        print("[🔍] Разбор предложений...")
        apply_code_updates(generated)

        return True

    except Exception as e:
        print(f"[❌] Ошибка при генерации кода: {e}")
        return False


def apply_code_updates(md_content: str):
    matches = re.findall(r"```python FILE: (.*?)\\n(.*?)```", md_content, re.DOTALL)

    if not matches:
        print("[⚠️] Не найдено изменений для файлов.")
        return

    for filename, code in matches:
        filepath = os.path.join(PROJECT_PATH, filename.strip())
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code.strip())
            print(f"[✅] Обновлён файл: {filename}")
        except Exception as e:
            print(f"[❌] Не удалось обновить {filename}: {e}")
