import time
from code_writer import generate_code_from_task
from deployer import deploy_code
import os

TASKS_FILE = "tasks_wiki.txt"
OUTPUT_FILE = "generated_patch.py"
LOG_FILE = "logs/self_update.log"


def read_task():
    if not os.path.exists(TASKS_FILE):
        print(f"[⚠️] Файл задач {TASKS_FILE} не найден.")
        return None

    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def write_code_to_file(code: str):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"[📦] Код сохранён в {OUTPUT_FILE}")


def append_log(entry: str):
    os.makedirs("logs", exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


if __name__ == "__main__":
    print("[🤖] Саморедактирующий цикл начат")
    while True:
        task = read_task()
        if not task:
            print("[🟡] Нет задачи для выполнения. Засыпаю на 10 минут...")
            time.sleep(600)
            continue

        print("[🧠] Отправляю задачу в GPT...")
        try:
            result = generate_code_from_task(task)
            write_code_to_file(result)
            log_entry = deploy_code()
            append_log(log_entry)
        except Exception as e:
            print(f"[❌] Ошибка при обновлении: {e}")
            append_log(f"[❌] Ошибка: {e}")

        print("[🕒] Сплю 10 минут...\n")
        time.sleep(600)
