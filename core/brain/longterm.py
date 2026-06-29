"""
RAFAEL - Long-term Memory (uzoq muddatli xotira)
Foydalanuvchi "eslab qol ..." deganda saqlanadigan doimiy faktlar.
Bu faktlar har bir LLM so'roviga kontekst sifatida qo'shiladi.
"""

import json
from pathlib import Path
from core.utils.logger import get_logger

logger = get_logger(__name__)

FACTS_FILE = Path("data/memory/facts.json")
MAX_FACTS = 50


class LongTermMemory:
    def __init__(self):
        self.facts: list[str] = []
        self._load()

    def _load(self):
        if FACTS_FILE.exists():
            try:
                self.facts = json.loads(FACTS_FILE.read_text(encoding="utf-8"))
            except Exception:
                self.facts = []

    def _save(self):
        FACTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        FACTS_FILE.write_text(
            json.dumps(self.facts, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add(self, fact: str) -> str:
        fact = (fact or "").strip()
        if not fact:
            return "Nimani eslab qolay?"
        if fact in self.facts:
            return "Buni allaqachon eslab qolganman."
        self.facts.append(fact)
        self.facts = self.facts[-MAX_FACTS:]
        self._save()
        logger.info(f"Uzoq xotira: {fact}")
        return f"Eslab qoldim: {fact}"

    def list_facts(self) -> str:
        if not self.facts:
            return "Hozircha siz haqingizda maxsus narsa eslamayman."
        items = ". ".join(f"{i}. {f}" for i, f in enumerate(self.facts, 1))
        return f"Siz haqingizda eslayman: {items}"

    def clear(self) -> str:
        self.facts = []
        self._save()
        return "Uzoq xotira tozalandi."

    def as_context(self) -> str:
        """LLM system prompt ga qo'shiladigan faktlar matni."""
        if not self.facts:
            return ""
        bullets = "\n".join(f"- {f}" for f in self.facts)
        return ("\n\nFOYDALANUVCHI HAQIDA ESLAB QOLGANLARING (kerak bo'lsa ishlat):\n"
                + bullets)
