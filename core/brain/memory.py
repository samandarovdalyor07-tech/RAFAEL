"""
RAPHAIL - Memory System
Suhbat tarixini va kontekstni eslab qoladi.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from core.utils.logger import get_logger

logger = get_logger(__name__)


class ConversationMemory:
    def __init__(self, memory_file: str, context_window: int = 20):
        self.memory_file = Path(memory_file)
        self.context_window = context_window
        self.messages: list[dict] = []
        self.session_start = datetime.now().isoformat()
        self._load()

    def _load(self):
        """Avvalgi suhbatni yuklaydi"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.messages = data.get("messages", [])
                    # Faqat oxirgi N xabarni olamiz
                    self.messages = self.messages[-self.context_window:]
                    logger.info(f"Memory yuklandi: {len(self.messages)} xabar")
            except Exception as e:
                logger.warning(f"Memory o'qishda xato: {e}")
                self.messages = []

    def save(self):
        """Suhbatni diskka saqlaydi"""
        try:
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "session_start": self.session_start,
                "last_updated": datetime.now().isoformat(),
                "messages": self.messages,
            }
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Memory saqlashda xato: {e}")

    def add_user(self, text: str):
        self.messages.append({"role": "user", "content": text})
        self._trim()
        self.save()

    def add_assistant(self, text: str):
        self.messages.append({"role": "assistant", "content": text})
        self._trim()
        self.save()

    def _trim(self):
        """Context window dan oshsa, eskisini o'chiradi"""
        if len(self.messages) > self.context_window * 2:
            self.messages = self.messages[-(self.context_window):]

    def get_messages(self) -> list[dict]:
        return self.messages.copy()

    def clear(self):
        self.messages = []
        self.save()
        logger.info("Memory tozalandi.")
