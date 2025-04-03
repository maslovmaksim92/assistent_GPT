# tester.py
import subprocess
import os


def run_tests() -> bool:
    print("[🧪] Запуск тестов...")

    if os.path.exists("tests"):
        command = ["pytest", "tests"]
    elif os.path.exists("unittest_main.py"):
        command = ["python", "unittest_main.py"]
    else:
        print("[⚠️] Тестов не найдено, считаем, что всё ок.")
        return True

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        print("[📋] Результат тестов:\n", result.stdout)
        if result.returncode == 0:
            print("[✅] Все тесты пройдены успешно.")
            return True
        else:
            print("[❌] Некоторые тесты не прошли.")
            return False

    except Exception as e:
        print(f"[❌] Ошибка при запуске тестов: {e}")
        return False
