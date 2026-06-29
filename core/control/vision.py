"""
RAFAEL - Vision (Ko'z)
Ekranni yoki rasmni suratga oladi va Claude ko'ra oladigan formatga (base64) o'tkazadi.
"""

import base64
import io
from pathlib import Path
from core.utils.logger import get_logger

logger = get_logger(__name__)


def capture_screen_b64() -> tuple[str, str] | None:
    """Ekranni suratga olib, (base64_data, media_type) qaytaradi.

    Xato bo'lsa None qaytaradi.
    """
    try:
        import pyautogui
        img = pyautogui.screenshot()

        # Juda katta ekranni biroz kichraytiramiz (token tejash + tezlik)
        max_w = 1600
        if img.width > max_w:
            ratio = max_w / img.width
            img = img.resize((max_w, int(img.height * ratio)))

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        data = base64.b64encode(buf.getvalue()).decode("ascii")
        logger.info(f"Ekran suratga olindi: {img.width}x{img.height}")
        return data, "image/png"
    except Exception as e:
        logger.error(f"Ekranni olishda xato: {e}")
        return None


def load_image_b64(path: str) -> tuple[str, str] | None:
    """Diskdagi rasm faylini base64 ga o'tkazadi: (data, media_type)."""
    try:
        p = Path(path)
        if not p.is_file():
            return None
        ext = p.suffix.lower()
        media = {
            ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".gif": "image/gif", ".webp": "image/webp",
        }.get(ext, "image/png")
        data = base64.b64encode(p.read_bytes()).decode("ascii")
        return data, media
    except Exception as e:
        logger.error(f"Rasmni o'qishda xato: {e}")
        return None
