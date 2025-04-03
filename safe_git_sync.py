import os
import subprocess
import shutil

ENV_FILE = ".env"
BACKUP_FILE = ".env_local_backup"
GITIGNORE_FILE = ".gitignore"

def run(cmd):
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"[❌] Ошибка выполнения: {cmd}")
        exit(1)

def backup_env():
    if os.path.exists(ENV_FILE):
        shutil.move(ENV_FILE, BACKUP_FILE)
        print("[📦] Файл .env переименован в .env_local_backup")

def restore_env():
    if os.path.exists(BACKUP_FILE):
        shutil.move(BACKUP_FILE, ENV_FILE)
        print("[✅] .env восстановлен из бэкапа")

def add_to_gitignore():
    if os.path.exists(GITIGNORE_FILE):
        with open(GITIGNORE_FILE, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    else:
        lines = []

    if ENV_FILE not in lines:
        with open(GITIGNORE_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{ENV_FILE}\n")
        run("git add .gitignore")
        run('git commit -m "🛡 Добавлен .env в .gitignore"')
        print("[🛡] .env добавлен в .gitignore и закоммичен")

def safe_git_pull():
    backup_env()
    run("git pull origin main --rebase")
    restore_env()
    add_to_gitignore()
    print("[🚀] Git pull с защитой от .env завершён успешно!")

if __name__ == "__main__":
    safe_git_pull()
