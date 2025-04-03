import os
import logging
import requests
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

logger = logging.getLogger(__name__)

# Забираем переменные окружения
BITRIX_DEAL_ADD_URL = os.getenv("BITRIX_DEAL_ADD_URL")
BITRIX_DEAL_LIST_URL = os.getenv("BITRIX_DEAL_LIST_URL")
BITRIX_DEAL_GET_URL = os.getenv("BITRIX_DEAL_GET_URL")
BITRIX_DEAL_UPDATE_URL = os.getenv("BITRIX_DEAL_UPDATE_URL")

BITRIX_LEAD_LIST_URL = os.getenv("BITRIX_LEAD_LIST_URL")
BITRIX_LEAD_GET_URL = os.getenv("BITRIX_LEAD_GET_URL")
BITRIX_LEAD_ADD_URL = os.getenv("BITRIX_LEAD_ADD_URL")
BITRIX_LEAD_UPDATE_URL = os.getenv("BITRIX_LEAD_UPDATE_URL")

BITRIX_CONTACT_LIST_URL = os.getenv("BITRIX_CONTACT_LIST_URL")
BITRIX_CONTACT_GET_URL = os.getenv("BITRIX_CONTACT_GET_URL")
BITRIX_CONTACT_ADD_URL = os.getenv("BITRIX_CONTACT_ADD_URL")
BITRIX_CONTACT_UPDATE_URL = os.getenv("BITRIX_CONTACT_UPDATE_URL")

BITRIX_COMPANY_LIST_URL = os.getenv("BITRIX_COMPANY_LIST_URL")
BITRIX_COMPANY_GET_URL = os.getenv("BITRIX_COMPANY_GET_URL")
BITRIX_COMPANY_ADD_URL = os.getenv("BITRIX_COMPANY_ADD_URL")
BITRIX_COMPANY_UPDATE_URL = os.getenv("BITRIX_COMPANY_UPDATE_URL")

class CRMbot:
    """
    Бот для взаимодействия с CRM Bitrix24 (сделки, лиды, контакты, компании).
    """

    def create_deal(self, title: str, stage_id: str = "NEW") -> dict:
        """
        Пример создания сделки по URL из окружения.
        """
        if not BITRIX_DEAL_ADD_URL:
            logger.error("Не задан BITRIX_DEAL_ADD_URL в окружении!")
            return None

        payload = {
            "fields": {
                "TITLE": title,
                "STAGE_ID": stage_id
            }
        }
        try:
            response = requests.post(BITRIX_DEAL_ADD_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info(f"✅ Сделка '{title}' успешно создана: {data}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка создания сделки: {e}")
            return None

    def list_deals(self, filter_params: dict = None, select: list = None) -> dict:
        if not BITRIX_DEAL_LIST_URL:
            logger.error("Не задан BITRIX_DEAL_LIST_URL в окружении!")
            return None

        payload = {
            "filter": filter_params if filter_params else {},
            "select": select if select else ["*"]
        }
        try:
            response = requests.post(BITRIX_DEAL_LIST_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info(f"✅ Получен список сделок: {data}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка при запросе списка сделок: {e}")
            return None

    # И так далее для остальных методов (get_deal, update_deal, list_leads, get_lead, create_lead, ...)

    # Пример для get_deal:
    def get_deal(self, deal_id: int) -> dict:
        if not BITRIX_DEAL_GET_URL:
            logger.error("Не задан BITRIX_DEAL_GET_URL в окружении!")
            return None

        payload = {"id": deal_id}
        try:
            response = requests.post(BITRIX_DEAL_GET_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info(f"✅ Данные сделки ID={deal_id}: {data}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка при получении сделки #{deal_id}: {e}")
            return None

    # ... и т.п. для лидов, контактов, компаний
