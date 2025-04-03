# deployer.py
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


def deploy():
    print("[🚀] Публикация файлов в GitHub через API...")
    try:
        for root, _, files in os.walk("."):
            for file in files:
                if file.endswith(".py") or file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    if ".git" in full_path or "__pycache__" in full_path:
                        continue

                    with open(full_path, "rb") as f:
                        content = base64.b64encode(f.read()).decode("utf-8")

                    github_path = os.path.relpath(full_path, ".").replace("\\", "/")
                    url = f"{API_URL}/{github_path}"
                    message = f"auto-update: {datetime.now().isoformat()}"

                    # Проверка: существует ли файл
                    r = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
                    if r.status_code == 200:
                        sha = r.json()["sha"]
                    else:
                        sha = None

                    data = {
                        "message": message,
                        "content": content,
                        "branch": "main"
                    }
                    if sha:
                        data["sha"] = sha

                    res = requests.put(url, json=data, headers={"Authorization": f"token {GITHUB_TOKEN}"})
                    if res.status_code in [200, 201]:
                        print(f"[✅] Обновлён файл: {github_path}")
                    else:
                        print(f"[❌] Ошибка при пуше {github_path}: {res.status_code}, {res.text}")

    except Exception as e:
        print(f"[❌] Ошибка при деплое: {e}")
