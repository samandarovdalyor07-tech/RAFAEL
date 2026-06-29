"""
RAFAEL - Notes / Todo
Oddiy ro'yxat (xarid, ishlar...). JSON faylda saqlanadi.
"""

import json
from pathlib import Path
from core.utils.logger import get_logger

logger = get_logger(__name__)

NOTES_FILE = Path("data/memory/notes.json")


class NotesManager:
    def __init__(self):
        self.notes: list[str] = []
        self._load()

    def _load(self):
        if NOTES_FILE.exists():
            try:
                self.notes = json.loads(NOTES_FILE.read_text(encoding="utf-8"))
            except Exception:
                self.notes = []

    def _save(self):
        NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
        NOTES_FILE.write_text(
            json.dumps(self.notes, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add(self, text: str) -> str:
        text = (text or "").strip()
        if not text:
            return "Ro'yxatga nima qo'shay?"
        self.notes.append(text)
        self._save()
        logger.info(f"Ro'yxatga qo'shildi: {text}")
        return f"Ro'yxatga qo'shildi: {text}. Jami {len(self.notes)} ta."

    def list_notes(self) -> str:
        if not self.notes:
            return "Ro'yxatingiz bo'sh."
        items = ". ".join(f"{i}. {n}" for i, n in enumerate(self.notes, 1))
        return f"Ro'yxatingizda {len(self.notes)} ta: {items}"

    def clear(self) -> str:
        self.notes = []
        self._save()
        return "Ro'yxat tozalandi."
