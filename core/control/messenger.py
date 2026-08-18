"""
RAFAEL - Messenger Controller
Telegram orqali xabar yuboradi.
"""

import time, subprocess, os
import pyautogui, pyperclip
from core.utils.logger import get_logger

logger = get_logger(__name__)

TELEGRAM_EXE = os.path.expandvars(r"%APPDATA%\Telegram Desktop\Telegram.exe")
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.25


def _save_clipboard():
    """Ish boshlanishidan oldingi clipboard mazmunini saqlaydi."""
    try:
        return pyperclip.paste()
    except Exception:
        return None


def _restore_clipboard(original):
    """Foydalanuvchining asl clipboard mazmunini tiklaydi.

    pyperclip.copy() foydalanuvchining clipboard'ini butunlay bosib
    o'tadi; buni qaytarmasak, Rafael'dan foydalangandan keyin
    foydalanuvchi nusxalagan narsa yo'qolib qoladi.
    """
    if original is None:
        return
    try:
        pyperclip.copy(original)
    except Exception:
        pass


def _find_telegram_window():
    """Telegram oynasini subprocess orqali topadi"""
    import ctypes
    user32 = ctypes.windll.user32

    result = []
    def enum_cb(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value
                if "telegram" in title.lower():
                    result.append(hwnd)
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
    return result[0] if result else None


def _open_telegram():
    """Telegramni ochadi yoki fokusga keltiradi"""
    import ctypes
    hwnd = _find_telegram_window()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 9)   # SW_RESTORE
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        time.sleep(0.8)
        return True

    # Ochilmagan — ishga tushir
    exe = TELEGRAM_EXE if os.path.exists(TELEGRAM_EXE) else "telegram"
    subprocess.Popen(exe, shell=not os.path.exists(TELEGRAM_EXE))
    time.sleep(4)

    hwnd = _find_telegram_window()
    if hwnd:
        import ctypes
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        return True
    return False


class MessengerController:
    def send_telegram(self, contact: str, message: str) -> str:
        original_clip = _save_clipboard()
        try:
            if not _open_telegram():
                return "Telegram ochilmadi."

            # Ctrl+K — qidiruv
            pyautogui.hotkey("ctrl", "k")
            time.sleep(0.7)

            # Kontakt nomini yoz
            pyperclip.copy(contact.capitalize())
            pyautogui.hotkey("ctrl", "v")
            time.sleep(1.2)

            # Birinchi natijani tanlash
            pyautogui.press("down")
            time.sleep(0.3)
            pyautogui.press("enter")
            time.sleep(0.8)

            # Xabarni yoz va yubor
            pyperclip.copy(message)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.4)
            pyautogui.press("enter")

            logger.info(f"Telegram: {contact} → '{message[:40]}'")
            return f"{contact} ga xabar yuborildi."

        except Exception as e:
            logger.error(f"Telegram xato: {e}")
            return f"Xabar yuborishda muammo: Telegram ochiq bo'lsin."
        finally:
            time.sleep(0.15)
            _restore_clipboard(original_clip)

    def open_telegram_contact(self, contact: str) -> str:
        original_clip = _save_clipboard()
        try:
            if not _open_telegram():
                return "Telegram ochilmadi."
            pyautogui.hotkey("ctrl", "k")
            time.sleep(0.6)
            pyperclip.copy(contact.capitalize())
            pyautogui.hotkey("ctrl", "v")
            time.sleep(1.2)
            pyautogui.press("down")
            time.sleep(0.2)
            pyautogui.press("enter")
            return f"{contact} bilan chat ochildi."
        except Exception as e:
            return f"Xato: {e}"
        finally:
            time.sleep(0.15)
            _restore_clipboard(original_clip)

    def search_contact(self, name: str) -> str:
        original_clip = _save_clipboard()
        try:
            if not _open_telegram():
                return "Telegram ochilmadi."
            pyautogui.hotkey("ctrl", "k")
            time.sleep(0.5)
            pyperclip.copy(name)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(1.0)
            return f"{name} qidirildi."
        except Exception as e:
            return f"Xato: {e}"
        finally:
            time.sleep(0.15)
            _restore_clipboard(original_clip)
