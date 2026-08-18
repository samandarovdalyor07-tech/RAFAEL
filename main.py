"""
RAFAEL v2.0 — Ishga tushirish
Supervisor loop + asyncio thread + tkinter mainloop.

Arxitektura:
  main thread  → tkinter UI (RafaelApp.run())
  bg thread    → asyncio event loop (RaphailAssistant.start())
  ui_queue     → thread-safe event kanal
  stop_event   → ikkala tomonni xushmuomalalik bilan to'xtatadi
"""

import asyncio
import os
import queue
import sys
import threading
import time
from pathlib import Path

import yaml
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
os.chdir(BASE_DIR)

CRASH_LIMIT   = 5     # Shuncha marta crash → to'xtash
RESTART_DELAY = 3     # Sekundlar

# ─── Config ──────────────────────────────────────────────────────────────────

def load_config() -> dict:
    path = BASE_DIR / "config.yaml"
    if not path.exists():
        print("XATO: config.yaml topilmadi!")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_full_config(config: dict) -> dict:
    """Barcha sub-seksiyalarni yassi dictga birlashtiradi."""
    full = dict(config.get("raphail", {}))
    full["voice"]        = config.get("voice",  {})
    full["ai"]           = config.get("ai",     {})
    full["system"]       = config.get("system", {})
    full["ui"]           = config.get("ui",     {})
    full["conversation"] = config.get("conversation", {})
    return full


def check_env():
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        print("XATO: .env faylida OPENAI_API_KEY topilmadi!")
        sys.exit(1)


# ─── Asyncio backend thread ──────────────────────────────────────────────────

def run_assistant(full_config: dict,
                  ui_q: queue.Queue,
                  stop_evt: threading.Event):
    """
    Supervisor loop: assistant crash bo'lsa qayta ishga tushiradi.
    CRASH_LIMIT marta ketma-ket crash → tamom.
    """
    from core.assistant import RaphailAssistant

    crashes = 0
    while not stop_evt.is_set() and crashes < CRASH_LIMIT:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            assistant = RaphailAssistant(full_config, ui_q, stop_evt)
            loop.run_until_complete(assistant.start())
            # Normalda chiqish — stop_evt orqali
            break
        except KeyboardInterrupt:
            break
        except Exception as e:
            crashes += 1
            msg = f"Tizim xatosi ({crashes}/{CRASH_LIMIT}): {e}"
            print(f"[SUPERVISOR] {msg}")
            try:
                ui_q.put_nowait({"type": "error", "text": msg})
            except queue.Full:
                pass
            if crashes < CRASH_LIMIT and not stop_evt.is_set():
                time.sleep(RESTART_DELAY)
        finally:
            try:
                loop.close()
            except Exception:
                pass

    if crashes >= CRASH_LIMIT:
        msg = "Tizim juda ko'p marta xato berdi. RAFAEL to'xtatildi."
        print(f"[SUPERVISOR] {msg}")
        try:
            ui_q.put_nowait({"type": "error", "text": msg})
        except queue.Full:
            pass

    stop_evt.set()
    print("[SUPERVISOR] Fon ip yakunlandi.")


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    # .env yuklash
    load_dotenv(BASE_DIR / ".env")
    check_env()

    config      = load_config()
    full_config = build_full_config(config)

    # Thread-safe kanal va to'xtatish signali
    ui_queue   = queue.Queue(maxsize=200)
    stop_event = threading.Event()

    # Asyncio backend — fon ip
    bg_thread = threading.Thread(
        target=run_assistant,
        args=(full_config, ui_queue, stop_event),
        daemon=True,
        name="RAFAEL-backend",
    )
    bg_thread.start()

    # UI — main thread (tkinter talab qiladi)
    show_ui = full_config.get("ui", {}).get("show_on_start", True)
    if show_ui:
        try:
            from ui.app import RafaelApp
            app = RafaelApp(ui_queue, stop_event, full_config)
            app.run()                           # Tkinter mainloop — bloklaydi
        except ImportError as e:
            print(f"UI yuklanmadi ({e}), faqat ovozli rejimda ishlamoqda.")
            # UI yo'q — stop_event ni kutamiz
            stop_event.wait()
        except Exception as e:
            print(f"UI xatosi: {e}")
            stop_event.wait()
    else:
        # Headless rejim
        print("RAFAEL fon rejimida ishlamoqda (UI o'chirilgan).")
        stop_event.wait()

    # Ikkala ipni to'xtatamiz
    stop_event.set()
    bg_thread.join(timeout=5)
    print("RAFAEL yakunlandi.")


if __name__ == "__main__":
    main()
