# agent.py
import subprocess
from idea_generator import generate_idea
from code_writer import write_code
from tester import run_tests
from deployer import deploy

def run_cycle():
    print("[🚀] Запуск цикла разработки")

    idea = generate_idea()
    print(f"[💡] Идея: {idea}")

    code_success = write_code(idea)
    if not code_success:
        print("[❌] Ошибка генерации кода")
        return

    if not run_tests():
        print("[❌] Тесты не прошли")
        return

    deploy()
    print("[✅] Готово! Всё задеплоено.")

if __name__ == "__main__":
    run_cycle()
