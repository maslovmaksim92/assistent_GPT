# bots/assistent.py

import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
BITRIX_TASK_ADD_URL = os.getenv("BITRIX_TASK_ADD_URL")

logger = logging.getLogger(__name__)

class AssistentBot:
    """
    Бот для управления задачами Bitrix24, который может (при желании) обращаться к GPT,
    например, чтобы анализировать текст задачи, приоритизировать, и т.д.
    """

    def create_task(self, title: str, description: str, responsible_id: int):
        """
        Создает задачу в Bitrix24 (task.item.add).
        """
        payload = {
            "fields": {
                "TITLE": title,
                "DESCRIPTION": description,
                "RESPONSIBLE_ID": responsible_id
            }
        }

        try:
            response = requests.post(BITRIX_TASK_ADD_URL, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ Задача '{title}' успешно создана в Bitrix24.")
                return "Задача успешно создана!"
            else:
                logger.error(f"❌ Ошибка создания задачи Bitrix24: {response.text}")
                return "Ошибка создания задачи в Bitrix24."
        except requests.exceptions.RequestException as e:
            logger.error(f"⚠ Сетевая ошибка при создании задачи: {e}", exc_info=True)
            return "Сетевая ошибка при создании задачи в Bitrix24."

    def handle_task_flow(self, dialog_id: str, user_message: str, start_new: bool = False) -> str:
        """
        Простейшая логика: если "создай задачу" встречается в user_message, создаём задачу,
        иначе возвращаем дежурный ответ.
        
        Вы можете внедрить GPT для анализа user_message:
           1. Подключить GPTBot или gpt_analyzer
           2. Определять, что хотел пользователь (Function Calling)
        """
        logger.info(f"✉ [AssistentBot] dialog_id={dialog_id}, user_message='{user_message}'")

        if "создай задачу" in user_message.lower():
            self.create_task(
                title="Задача из чата",
                description="Описание задачи из чата",
                responsible_id=1  # Укажите реальный ID ответственного
            )
            return "Задача создана в Bitrix24!"
        else:
            return "Я — AssistentBot! Чем могу помочь?"
