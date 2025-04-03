# self_editor.py
import os
import time
from code_writer import write_code
from tester import run_tests
from deployer import deploy

PROJECT_PATH = "./"

def get_all_py_files():
    files = []
    for root, _, filenames in os.walk(PROJECT_PATH):
        for f in filenames:
            if f.endswith(".py") and "venv" not in root:
                files.append(os.path.join(root, f))
    return files

def read_all_code():
    codebase = ""
    for path in get_all_py_files():
        with open(path, "r", encoding="utf-8") as f:
            codebase += f"# FILE: {path}\n{f.read()}\n\n"
    return codebase

def self_improve_cycle():
    print("[🤖] Саморедактирующий цикл начат")
    codebase = read_all_code()

    print("[🧠] Отправляю код на анализ и улучшение...")
    idea = "Проанализируй и улучшай код проекта. Устраняй дублирование, баги, улучшай архитектуру."
    
    if not write_code(idea, full_context=codebase):
        print("[❌] Не удалось улучшить код.")
        return
    
    if run_tests():
        print("[✅] Изменения прошли тесты, деплоим.")
        deploy()
    else:
        print("[⚠️] Тесты провалены, откат или ручная проверка.")

if __name__ == "__main__":
    while True:
        self_improve_cycle()
        print("[🕒] Спим 10 минут...\n")
        time.sleep(600)
