# bots/gpt_analyzer.py

import os
import logging
import json
from typing import Optional, Dict
from openai import OpenAI
import requests  # Для обращения к Bitrix REST
from rapidfuzz import fuzz  # pip install rapidfuzz

logger = logging.getLogger(__name__)

class GPTAnalyzer:
    """
    Анализатор (AI) на базе gpt-4o (или другой).

    Поле UF_CRM_1669561599956 (Адрес) содержит полный адрес, например:
    'улица Кубяка 5, Калуга, Калужская область, Россия, 248012'.
    Мы берем этот текст целиком и используем его в fuzzy matching,
    игнорируя любые записи, где в адресе присутствует 'не убираем'.
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Не найден OPENAI_API_KEY в переменных окружения.")
        self.client = OpenAI(api_key=api_key)

        # Модель gpt-4o (или другая)
        self.model = "gpt-4o"

        # -- URL и параметры для Bitrix24 (должны быть в .env) --
        self.BITRIX_WEBHOOK_URL = os.getenv("BITRIX_WEBHOOK_URL", "")
        self.CATEGORY_ID_CLEANING = os.getenv("CATEGORY_ID_CLEANING", "2")

        # ---- Расширяем описание функций ----
        self.functions = [
            {
                "name": "process_crm",
                "description": "Обработка CRM-запросов (создать/обновить сделку и т.д.)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Тип действия: create, update, close"
                        },
                        "deal_title": {
                            "type": "string",
                            "description": "Название сделки"
                        }
                    },
                    "required": ["action", "deal_title"]
                }
            },
            {
                "name": "process_logistic",
                "description": "Логистика (получить маршрут, распределить бригаду)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address_list": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Список адресов для маршрута"
                        }
                    },
                    "required": ["address_list"]
                }
            },
            {
                "name": "process_finance",
                "description": "Получить финансовую аналитику (отчёт, данные)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "report_type": {
                            "type": "string",
                            "description": "Тип отчёта: 'monthly', 'yearly' и т.д."
                        }
                    },
                    "required": ["report_type"]
                }
            },
            {
                "name": "process_cleaning_schedule",
                "description": (
                    "Получить дату (или даты) уборки в указанном месяце по адресу (UF_CRM_1669561599956). "
                    "Поле адреса хранит полный текст, напр. 'улица Кубяка 5, Калуга...'. "
                    "Исключаем адреса, где есть 'не убираем'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "Адрес МКД (UF_CRM_1669561599956)"
                        },
                        "month": {
                            "type": "string",
                            "description": "Месяц (пример: 'январь' или '01')"
                        },
                        "year": {
                            "type": "string",
                            "description": "Год (пример: '2025')"
                        }
                    },
                    "required": ["address", "month", "year"]
                }
            }
        ]

    def analyze(self, user_message: str, user_info: Optional[Dict] = None) -> str:
        logger.info(f"[GPTAnalyzer] user_message: {user_message}")
        if user_info:
            logger.info(f"[GPTAnalyzer] user_info: {user_info}")

        # Дополненный system_prompt
        system_prompt = (
            "Ты - умный маршрутизатор на gpt-4o. "
            "Если вопрос про даты уборки (дом, подъезд), вызывай process_cleaning_schedule, "
            "используя ТОЛЬКО поле UF_CRM_1669561599956 (полный адрес). "
            "Исключаем любые адреса, где в тексте 'не убираем'.\n"
            "Если про 'сделку' (CRM) - process_crm. Если про маршрут - process_logistic. "
            "Если про финансы - process_finance.\nИначе - обычный текст."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                functions=self.functions,
                function_call="auto",
                max_tokens=500,
                temperature=0.7
            )
            if not response.choices:
                return "Извините, я не получил ответа от gpt-4o."

            choice = response.choices[0]
            finish_reason = choice.finish_reason

            if finish_reason == "function_call":
                fn_call = choice.message.function_call
                if not fn_call:
                    return "GPT запросил вызов функции, но данных о вызове нет."

                try:
                    args_dict = json.loads(fn_call.arguments)
                except Exception as parse_error:
                    logger.error(f"Ошибка парсинга аргументов: {parse_error}")
                    return "Ошибка при разборе аргументов GPT."

                fn_name = fn_call.name
                logger.info(f"[GPTAnalyzer] GPT вызвал функцию: {fn_name}, аргументы={args_dict}")

                if fn_name == "process_crm":
                    return self.process_crm(**args_dict)
                elif fn_name == "process_logistic":
                    return self.process_logistic(**args_dict)
                elif fn_name == "process_finance":
                    return self.process_finance(**args_dict)
                elif fn_name == "process_cleaning_schedule":
                    return self.process_cleaning_schedule(**args_dict)
                else:
                    return f"Неизвестная функция: {fn_name}"

            # Иначе GPT вернул обычный текст
            return choice.message.content or "GPT не дал ответа."

        except Exception as e:
            logger.error(f"[GPTAnalyzer] Ошибка: {e}", exc_info=True)
            return "Произошла ошибка при обращении к GPT-4o."

    # -----------------------------------------------------------
    # ФУНКЦИИ - ИСПОЛЬЗУЕМ ТОЛЬКО UF_CRM_1669561599956 ДЛЯ АДРЕСА
    # -----------------------------------------------------------

    def process_crm(self, action: str, deal_title: str) -> str:
        logger.info(f"[process_crm] action={action}, deal_title={deal_title}")
        return f"CRM: Выполняю действие '{action}' со сделкой '{deal_title}'."

    def process_logistic(self, address_list: list) -> str:
        logger.info(f"[process_logistic] Маршрут: {address_list}")
        return f"Логистика: Оптимальный маршрут для {len(address_list)} адресов."

    def process_finance(self, report_type: str) -> str:
        logger.info(f"[process_finance] report_type={report_type}")
        return f"Финансы: Формирую {report_type} отчёт."

    def process_cleaning_schedule(self, address: str, month: str, year: str) -> str:
        """
        Опрашивает CRM/базу, чтобы узнать, на какие даты запланирована уборка
        по адресу (UF_CRM_1669561599956), в месяц `month` и год `year`.

        Исключаем сделки, если в адресе присутствует 'не убираем'.

        Возвращает строку-ответ для пользователя.
        """

        logger.info(f"[process_cleaning_schedule] address={address}, month={month}, year={year}")

        if not self.BITRIX_WEBHOOK_URL:
            return "Ошибка: не задан BITRIX_WEBHOOK_URL в окружении."

        # 1) Точный поиск (UF_CRM_1669561599956 = address)
        filter_params = {
            "CATEGORY_ID": self.CATEGORY_ID_CLEANING,
            "UF_CRM_1669561599956": address
        }
        params = {
            "filter": filter_params,
            "select": [
                "ID", "TITLE",
                "UF_CRM_1669561599956",
                "UF_CRM_1731051175467",
                "UF_CRM_1731051181129",
                "UF_CRM_1731051110108",
                "UF_CRM_1731051154828",
                "UF_CRM_1669704631166",
                "UF_CRM_1669705507390",
            ],
            "start": 0
        }

        list_url = f"{self.BITRIX_WEBHOOK_URL}crm.deal.list"
        try:
            resp = requests.post(list_url, json=params)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к Bitrix24: {e}", exc_info=True)
            return f"Сетевая ошибка при запросе к Bitrix24: {str(e)}"

        deals_data = resp.json()
        result_list = deals_data.get("result", [])

        # Фильтруем по 'не убираем'
        result_list = [deal for deal in result_list
                       if 'не убираем' not in (deal.get("UF_CRM_1669561599956") or "").lower()]

        # 2) Частичное совпадение (LIKE) - только UF_CRM_1669561599956
        if not result_list:
            logger.info("Точный поиск не дал результатов (или адрес 'не убираем'). Пробуем LIKE.")
            partial_filter = {
                "CATEGORY_ID": self.CATEGORY_ID_CLEANING,
                "LOGIC": "OR",
                "%UF_CRM_1669561599956": address
            }
            params_partial = {
                "filter": partial_filter,
                "select": params["select"],
                "start": 0
            }
            try:
                resp2 = requests.post(list_url, json=params_partial)
                resp2.raise_for_status()
                deals_data2 = resp2.json()
                result_list = deals_data2.get("result", [])
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка partial-match запроса: {e}", exc_info=True)
                return f"Сетевая ошибка partial-match: {str(e)}"

            # Фильтруем 'не убираем'
            result_list = [d for d in result_list
                           if 'не убираем' not in (d.get("UF_CRM_1669561599956") or "").lower()]

        # 3) Fuzzy matching - только UF_CRM_1669561599956
        if not result_list:
            logger.info("LIKE не помог (или адрес 'не убираем'). Собираем все сделки, делаем fuzzy UF_CRM_1669561599956.")
            all_in_cat_params = {
                "filter": {"CATEGORY_ID": self.CATEGORY_ID_CLEANING},
                "select": params["select"],
                "start": 0
            }
            try:
                resp3 = requests.post(list_url, json=all_in_cat_params)
                resp3.raise_for_status()
                deals_data3 = resp3.json()
                all_cat_list = deals_data3.get("result", [])
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка all-cat запроса: {e}", exc_info=True)
                return f"Сетевая ошибка all-cat: {str(e)}"

            # Исключаем 'не убираем'
            all_cat_list = [
                d for d in all_cat_list
                if 'не убираем' not in (d.get("UF_CRM_1669561599956") or "").lower()
            ]

            best_score = 0
            best_deals = []
            address_lower = address.lower()
            fuzzy_threshold = 70

            for deal in all_cat_list:
                candidate_addr = str(deal.get("UF_CRM_1669561599956") or "").lower()
                score_addr = fuzz.partial_ratio(candidate_addr, address_lower)

                if score_addr > best_score:
                    best_score = score_addr
                    best_deals = [deal]
                elif score_addr == best_score:
                    best_deals.append(deal)

            logger.info(f"Fuzzy match score={best_score}, deals found={len(best_deals)}")

            if best_score < fuzzy_threshold:
                return f"Не найдена (даже fuzzy) сделка по '{address}' в категории {self.CATEGORY_ID_CLEANING}."

            result_list = best_deals

        if not result_list:
            return f"Не найдена (даже после фильтрации 'не убираем') сделка по '{address}' в категории {self.CATEGORY_ID_CLEANING}."

        # Формируем ответ
        all_responses = []
        for deal in result_list:
            deal_title = deal.get("TITLE", "Без названия")
            addr_field = deal.get("UF_CRM_1669561599956", "")
            date1 = deal.get("UF_CRM_1731051175467", "")
            date2 = deal.get("UF_CRM_1731051181129", "")
            type1 = deal.get("UF_CRM_1731051110108", "")
            type2 = deal.get("UF_CRM_1731051154828", "")
            floors = deal.get("UF_CRM_1669704631166", "не указано")
            entrances = deal.get("UF_CRM_1669705507390", "не указано")

            response_text = (
                f"Сделка: {deal_title}\n"
                f"Адрес (МКД): {addr_field}\n"
                f"Этажей: {floors}, Подъездов: {entrances}\n"
                f"Уборка 1: {date1} — {type1}\n"
                f"Уборка 2: {date2} — {type2}\n"
                f"(Запрошено: месяц '{month}', год '{year}')"
            )
            all_responses.append(response_text)

        return "\n\n".join(all_responses)
