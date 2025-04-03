# bots/gpt.py

import os
import logging
from typing import Optional, List, Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)

class GPTBot:
    """
    Бот, возвращающий обычные текстовые ответы от GPT-4 (подобно ChatGPT),
    поддерживая дополнительный параметр user_info (если нужно).
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Не найден OPENAI_API_KEY в переменных окружения.")

        self.client = OpenAI(api_key=api_key)

        self.model = "gpt-4"
        self.temperature = 0.7
        self.max_tokens = 1000

    def ask_gpt(
        self,
        user_message: str,
        user_info: Optional[Dict] = None,
        context: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Отправляет user_message в GPT-4 и возвращает обычный текст ответа.
        :param user_message: сообщение пользователя
        :param user_info: словарь с доп.инфо о пользователе (имя, роль, и т.д.)
        :param context: история диалога в формате [{"role":"system"/"user"/"assistant", "content": "..."}]
        """

        logger.info(f"[GPTBot] Пришло сообщение: {user_message}")
        if user_info:
            logger.info(f"[GPTBot] user_info: {user_info}")

        # Формируем список messages
        messages = []

        # Можно сформировать system_prompt с учетом user_info:
        system_prompt = "Ты - Assistent GPT, помогаешь с любыми вопросами."
        if user_info:
            # Допустим, мы хотим отобразить имя пользователя/роль
            user_name = user_info.get("name", "Пользователь")
            system_prompt += f" Пользователь: {user_name}. "

        messages.append({"role": "system", "content": system_prompt})

        # Добавляем контекст диалога, если есть
        if context:
            messages.extend(context)

        # Добавляем текущее сообщение пользователя
        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            if not response.choices:
                return "Извините, я не получила ответ от GPT."

            answer = response.choices[0].message.content
            return answer

        except Exception as e:
            logger.error(f"[GPTBot] Ошибка при запросе к GPT: {e}", exc_info=True)
            return "Произошла ошибка при обращении к GPT."
