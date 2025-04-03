# bots/transcribe.py

import os
import logging
import whisper  # Нужно установить, напр. pip install git+https://github.com/openai/whisper.git
from dotenv import load_dotenv

load_dotenv()
WHISPER_MODEL_PATH = os.getenv("WHISPER_MODEL_PATH", "large")

logger = logging.getLogger(__name__)

class TranscribeBot:
    """
    Бот для транскрибации аудио/видео.
    Использует модель Whisper.
    """

    def __init__(self):
        logger.info(f"Загружаем модель Whisper: {WHISPER_MODEL_PATH}")
        self.model = whisper.load_model(WHISPER_MODEL_PATH)

    def transcribe_audio(self, file_path: str) -> str:
        """
        Транскрибирует аудио файл в текст.
        """
        logger.info(f"Транскрибация файла: {file_path}")
        result = self.model.transcribe(file_path)
        return result["text"]
