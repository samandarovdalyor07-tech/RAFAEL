"""
RAFAEL - Info Controller
Internetdan kundalik ma'lumotlar: ob-havo (wttr.in) va valyuta kursi (CBU).
Ikkalasi ham API kalit talab qilmaydi.
"""

import urllib.parse
import requests
from core.utils.logger import get_logger

logger = get_logger(__name__)

# Valyuta nomi → CBU kodi
CURRENCY_CODES = {
    "usd": "USD", "dollar": "USD", "доллар": "USD", "dollor": "USD",
    "eur": "EUR", "evro": "EUR", "euro": "EUR", "евро": "EUR",
    "rub": "RUB", "rubl": "RUB", "рубль": "RUB", "рубл": "RUB",
}


class InfoController:
    def weather(self, city: str = "") -> str:
        """wttr.in orqali ob-havo (API kalit kerak emas)."""
        city = (city or "Tashkent").strip()
        try:
            url = f"https://wttr.in/{urllib.parse.quote(city)}?format=%C,+%t&lang=ru"
            r = requests.get(url, timeout=8, headers={"User-Agent": "curl/8"})
            txt = r.text.strip()
            if r.ok and txt and "Unknown location" not in txt and "Sorry" not in txt:
                return f"{city} da hozir: {txt}"
            return f"{city} uchun ob-havoni topa olmadim."
        except requests.RequestException as e:
            logger.error(f"Ob-havo xatosi: {e}")
            return "Ob-havoni olishda internet xatosi."

    def currency(self, which: str = "usd") -> str:
        """O'zbekiston Markaziy banki (CBU) kursi — UZS so'mda."""
        code = CURRENCY_CODES.get((which or "usd").lower().strip(), "USD")
        try:
            url = f"https://cbu.uz/uz/arkhiv-kursov-valyut/json/{code}/"
            r = requests.get(url, timeout=8)
            data = r.json()
            if data and isinstance(data, list):
                rate = data[0].get("Rate")
                diff = data[0].get("Diff", "0")
                return f"1 {code} = {rate} so'm. Kechagiga nisbatan farq: {diff} so'm."
            return f"{code} kursini topa olmadim."
        except Exception as e:
            logger.error(f"Valyuta xatosi: {e}")
            return "Valyuta kursini olishda xato."
