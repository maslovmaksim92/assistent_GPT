# bots/calendar.py

import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
BITRIX_EVENT_ADD_URL = os.getenv("BITRIX_EVENT_ADD_URL")

logger = logging.getLogger(__name__)

class CalendarBot:
    """
    Бот для управления событиями в календаре (Bitrix24).
    """

    def add_event(self, name: str, start: str, end: str):
        """
        Создает календарное событие.
        start, end — строки в формате "YYYY-MM-DD HH:MM:SS"
        """
        payload = {
            "fields": {
                "NAME": name,
                "DATE_FROM": start,
                "DATE_TO": end,
                "SKIP_TIME": "N"
            }
        }
        response = requests.post(BITRIX_EVENT_ADD_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Событие '{name}' успешно создано: {data}")
            return data
        else:
            logger.error(f"❌ Ошибка создания события: {response.text}")
            return None
