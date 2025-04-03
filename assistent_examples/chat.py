# bots/chat.py

import logging

logger = logging.getLogger(__name__)

class ChatBot:
    """
    Бот для управления и автоматизации чатов (Bitrix24 Open Lines, групповые чаты).
    Может использовать GPT для генерации ответов.
    """

    def handle_incoming_message(self, message: str, user_id: str):
        logger.info(f"Принято сообщение от user_id={user_id}: {message}")
        # В реальности здесь можно вызвать GPT:
        # gpt_response = self.gpt_client.chat.completions.create(...)
        # return gpt_response.choices[0].message.content
        return f"Привет, пользователь {user_id}! Вы сказали: {message}"
