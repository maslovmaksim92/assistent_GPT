import os
import logging
import subprocess
from flask import Flask, request, render_template_string, redirect, url_for
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

# Загрузка переменных из .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Настройка логирования в файл
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, "app.log")

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)

# Flask-приложение
app = Flask(__name__)
logs = []
gpt_thoughts = ""

# HTML-шаблон
TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>MaksimGPT</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2 { color: #222; }
        .log, .chat, .thoughts { background-color: #f5f5f5; padding: 15px; margin-bottom: 20px; border-radius: 8px; }
        .chat textarea { width: 100%; height: 80px; }
        .chat input[type=submit] { margin-top: 10px; padding: 8px 16px; }
        .logo { font-size: 28px; font-weight: bold; }
        .section-title { font-size: 22px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="logo">🤖 MaksimGPT</div>

    <form method="POST" action="/git_pull" style="display:inline;">
        <button type="submit">🧩 Обновить из GitHub</button>
    </form>
    <form method="POST" action="/clear_logs" style="display:inline; margin-left: 10px;">
        <button type="submit">🧹 Очистить логи</button>
    </form>

    <div class="log">
        <div class="section-title">📜 Логи</div>
        {% for log in logs %}
            <pre>{{ log }}</pre>
        {% endfor %}
    </div>

    <div class="chat">
        <div class="section-title">💬 Чат с GPT</div>
        <form method="POST" action="/chat">
            <textarea name="message" placeholder="Напиши команду: Сделай это / Улучши / Изучи..."></textarea><br>
            <input type="submit" value="📨 Отправить">
        </form>
    </div>

    <div class="thoughts">
        <div class="section-title">🧠 Мысли/Выводы ИИ</div>
        <pre>{{ gpt_thoughts }}</pre>
    </div>
</body>
</html>
"""

def get_logs_tail(lines=50):
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            return f.readlines()[-lines:]
    except Exception as e:
        return [f"Ошибка чтения логов: {e}"]

@app.route("/", methods=["GET"])
def index():
    return render_template_string(TEMPLATE, logs=get_logs_tail(), gpt_thoughts=gpt_thoughts)

@app.route("/git_pull", methods=["POST"])
def git_pull():
    now = datetime.utcnow().strftime("%a %b %d %H:%M:%S UTC %Y")
    try:
        result = subprocess.run(["git", "pull"], capture_output=True, text=True)
        logs.append(f"🕒 Git Pull @ {now}\n{result.stdout or result.stderr}")
    except Exception as e:
        logs.append(f"❌ Ошибка Git Pull: {e}")
    return redirect(url_for("index"))

@app.route("/clear_logs", methods=["POST"])
def clear_logs():
    try:
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("")
        logs.clear()
        logs.append("🧹 Логи очищены.")
    except Exception as e:
        logs.append(f"❌ Ошибка очистки логов: {e}")
    return redirect(url_for("index"))

@app.route("/chat", methods=["POST"])
def chat():
    global gpt_thoughts
    message = request.form.get("message", "").strip()
    now = datetime.utcnow().strftime("%a %b %d %H:%M:%S UTC %Y")

    if not message:
        logs.append(f"⚠️ Пустое сообщение @ {now}")
        return redirect(url_for("index"))

    logs.append(f"📩 Ты отправил: {message}")
    logging.info(f"Пользователь: {message}")

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": message}],
        )
        reply = response.choices[0].message.content.strip()
        gpt_thoughts = reply
        logs.append(f"🤖 Ответ ИИ @ {now}:\n{reply}")
        logging.info(f"Ответ GPT: {reply}")
    except Exception as e:
        gpt_thoughts = "⚠️ Ошибка запроса к ИИ."
        logs.append(f"❌ Ошибка ChatGPT: {e}")
        logging.error(f"Ошибка ChatGPT: {e}")

    return redirect(url_for("index"))

if __name__ == "__main__":
    logging.info("=== Запуск MaksimGPT ===")
    app.run(host="0.0.0.0", port=10000)
