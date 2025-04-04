import os
from assistent_GPT.code_writer import generate_code_from_task
from assistent_GPT.deployer import deploy

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
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"[📦] Код сохранён в {OUTPUT_FILE}")
    except Exception as e:
        print(f"[❌] Ошибка сохранения кода: {e}")


def append_log(entry: str):
    try:
        os.makedirs("logs", exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception as e:
        print(f"[❌] Ошибка записи лога: {e}")


if __name__ == "__main__":
    print("[🤖] Саморедактирующий цикл начат")

    while True:
        task = read_task()
        if not task:
            print("[🟡] Нет задачи для выполнения. Начинаю заново...")
            continue

        print("[🧠] Отправляю задачу в GPT...")
        try:
            result = generate_code_from_task(task)
            write_code_to_file(result)
            deploy_log = deploy()
            append_log(deploy_log if deploy_log else "[⚠️] Пустой лог деплоя")
        except Exception as e:
            print(f"[❌] Ошибка при обновлении: {e}")
            append_log(f"[❌] Ошибка: {e}")

        print("[🔁] Переход к следующему циклу...\n")
