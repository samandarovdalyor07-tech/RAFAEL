"""
RAFAEL - Reminder System
Vaqtga asoslangan eslatmalar.
"""

import asyncio, json, re
from datetime import datetime, timedelta
from pathlib import Path
from core.utils.logger import get_logger

logger = get_logger(__name__)

REMINDER_FILE = Path("data/memory/reminders.json")


def _parse_time(text: str) -> datetime | None:
    """Matndan vaqtni ajratib oladi"""
    t = text.lower().strip()
    now = datetime.now()

    # "soat 15:30 da" / "soat 3 da" / "15:00 da"
    m = re.search(r'soat\s*(\d{1,2})(?::(\d{2}))?\s*(?:da|de)?', t)
    if not m:
        m = re.search(r'(\d{1,2}):(\d{2})', t)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2)) if m.group(2) else 0
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return target

    # "N minutdan keyin" / "N daqiqadan keyin"
    m = re.search(r'(\d+)\s*(?:minut|daqiqa|минут|минуты|min)\w*\s*(?:dan|keyin|после|from now)?', t)
    if m:
        return now + timedelta(minutes=int(m.group(1)))

    # "N soatdan keyin"
    m = re.search(r'(\d+)\s*(?:soat|час|hour)\w*\s*(?:dan|keyin|через|from now)?', t)
    if m:
        return now + timedelta(hours=int(m.group(1)))

    # "yarim soatdan keyin"
    if "yarim soat" in t or "полчаса" in t or "30 min" in t:
        return now + timedelta(minutes=30)

    return None


def _parse_reminder_text(text: str) -> tuple[datetime | None, str]:
    """Matndan vaqt va eslatma mazmunini ajratadi"""
    t = text.lower()

    # Vaqtni topamiz
    dt = _parse_time(t)

    # Eslatma mazmunini topamiz — vaqt va kalit so'zlarni olib tashlaymiz
    msg = text
    # Vaqt iboralarini olib tashlaymiz
    msg = re.sub(r'soat\s*\d{1,2}(?::\d{2})?\s*(?:da|de)?', '', msg, flags=re.IGNORECASE)
    msg = re.sub(r'\d{1,2}:\d{2}', '', msg)
    msg = re.sub(r'\d+\s*(?:minut|daqiqa|soat|минут|час)\w*\s*(?:dan\s+keyin|keyin|после|through|from now)?', '', msg, flags=re.IGNORECASE)
    msg = re.sub(r'yarim soatdan keyin', '', msg, flags=re.IGNORECASE)
    # Kalit so'zlarni olib tashlaymiz (to'liq so'z sifatida)
    for kw in ["eslatib tur", "eslatib bergin", "eslatib ber", "eslatib", "eslat",
               "напомни мне", "напомни", "remind me", "reminder"]:
        msg = re.sub(r'\b' + re.escape(kw) + r'\b', '', msg, flags=re.IGNORECASE)
    msg = re.sub(r'\s+', ' ', msg).strip(" :,.-")
    return dt, msg or "Eslatma vaqti keldi!"


class ReminderManager:
    def __init__(self, speak_callback):
        self.speak = speak_callback
        self.reminders: list[dict] = []
        self._task: asyncio.Task | None = None
        self._load()

    def _load(self):
        if REMINDER_FILE.exists():
            try:
                data = json.loads(REMINDER_FILE.read_text(encoding="utf-8"))
                now = datetime.now().timestamp()
                self.reminders = [r for r in data if r["time"] > now]
            except Exception:
                self.reminders = []

    def _save(self):
        REMINDER_FILE.parent.mkdir(parents=True, exist_ok=True)
        REMINDER_FILE.write_text(
            json.dumps(self.reminders, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def add(self, text: str) -> str:
        dt, msg = _parse_reminder_text(text)
        if not dt:
            return "Vaqtni tushunmadim. Masalan: 'soat 15 da', '30 minutdan keyin'."

        reminder = {
            "time": dt.timestamp(),
            "message": msg,
            "display": dt.strftime("%H:%M"),
        }
        self.reminders.append(reminder)
        self._save()
        logger.info(f"Eslatma: {dt.strftime('%H:%M')} — {msg}")
        return f"Eslatma qo'yildi: soat {dt.strftime('%H:%M')} da — {msg}"

    def start(self):
        """Eslatmalarni tekshirishni boshlaydi"""
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._loop())

    async def _loop(self):
        while True:
            now = datetime.now().timestamp()
            fired = []
            for r in self.reminders:
                if now >= r["time"]:
                    fired.append(r)
                    text = f"Eslatma! Soat {r['display']}: {r['message']}"
                    logger.info(f"Eslatma o'tdi: {text}")
                    await self.speak(text)

            for r in fired:
                self.reminders.remove(r)
            if fired:
                self._save()

            await asyncio.sleep(20)  # har 20 sekundda tekshir
