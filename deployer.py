import os
import base64
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents"


EXCLUDED_DIRS = {".git", "__pycache__", "logs", ".venv", ".idea"}
EXCLUDED_FILES = {".env", "requirements.txt", "README.md", "logs/app.log", "logs/self_update.log"}


def deploy_code():
    print("[🚀] Публикация файлов в GitHub через API...")
    try:
        results = []

        for root, _, files in os.walk("."):
            parts = set(root.split(os.sep))
            if parts & EXCLUDED_DIRS:
                continue

            for file in files:
                if not (file.endswith(".py") or file.endswith(".md")):
                    continue

                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, ".").replace("\\", "/")

                if rel_path in EXCLUDED_FILES:
                    continue

                with open(full_path, "rb") as f:
                    content = base64.b64encode(f.read()).decode("utf-8")

                url = f"{API_URL}/{rel_path}"
                message = f"🤖 auto-update: {datetime.now().isoformat()}"

                # Проверка: существует ли файл
                r = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
                sha = r.json()["sha"] if r.status_code == 200 else None

                data = {
                    "message": message,
                    "content": content,
                    "branch": "main"
                }
                if sha:
                    data["sha"] = sha

                res = requests.put(url, json=data, headers={"Authorization": f"token {GITHUB_TOKEN}"})
                if res.status_code in [200, 201]:
                    print(f"[✅] Обновлён: {rel_path}")
                    results.append(f"✅ {rel_path}")
                else:
                    print(f"[❌] Ошибка при пуше {rel_path}: {res.status_code} {res.text}")
                    results.append(f"❌ {rel_path} — {res.status_code}")

        return "\n".join(results)

    except Exception as e:
        error_msg = f"[❌] Ошибка при деплое: {e}"
        print(error_msg)
        return error_msg
