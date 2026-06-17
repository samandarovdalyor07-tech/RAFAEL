"""
RAFAEL v2.0 — Main Assistant
Wake-word asosida ishlaydi. Event emitter: UI queue orqali holat yuboradi.
Multi-command: "chrome och va spotify ham och" → 2 ta amal ketma-ket.
"""

import asyncio
import json
import queue
import re
import threading
from typing import Optional

from core.voice.listener     import VoiceListener
from core.voice.speaker      import VoiceSpeaker
from core.voice.wake_word    import contains_wake_word, is_stop_command
from core.brain.llm          import RaphailBrain
from core.brain.memory       import ConversationMemory
from core.brain.parser       import parse
from core.brain.reminder     import ReminderManager
from core.control.system     import SystemController
from core.control.browser    import BrowserController
from core.control.code_writer import CodeWriter
from core.control.messenger  import MessengerController
from core.control.bluetooth  import BluetoothController
from core.utils.logger       import get_logger

logger = get_logger(__name__)

# ── Javob iboralari ──────────────────────────────────────────────────────────
CONFIRMS = [
    "Hop bo'ladi, janob.",
    "Bajarildi, janob.",
    "Darhol, janob.",
    "Xo'p bo'ladi.",
    "Tayyor, janob.",
    "Qayd etildi.",
]
_ci = 0
def _confirm() -> str:
    global _ci
    msg = CONFIRMS[_ci % len(CONFIRMS)]
    _ci += 1
    return msg

REMINDER_WORDS = [
    "eslatib tur","eslatib ber","eslat","eslatma qo'y",
    "напомни","remind me","reminder",
]

def _is_reminder(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in REMINDER_WORDS)

# ── Tarjima ──────────────────────────────────────────────────────────────────
TRANSLATE_WORDS = [
    "tarjima qil","tarjima qilib ber","tarjima","translate","перевод","переведи",
    "inglizchaga o'gir","inglizcha qil","o'zbekchaga o'gir","o'zbekcha qil",
    "nima degani","nima deyiladi","qanday tarjima",
]

def _is_translate(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in TRANSLATE_WORDS)

def _extract_translate_phrase(text: str) -> str:
    """Buyruqdan tarjima qilinadigan iborani ajratib oladi."""
    t = text
    for w in sorted(TRANSLATE_WORDS, key=len, reverse=True):
        t = re.sub(re.escape(w), " ", t, flags=re.IGNORECASE)
    # Yordamchi qo'shimchalarni tozalaymiz
    for p in [" ni ", " ging ", " degan ", " sozni ", " so'zni ", " gapni ",
              " iborani ", " degani "]:
        t = t.replace(p, " ")
    return re.sub(r"\s+", " ", t).strip(" ,.:-\"'")

# ── Dars / o'qish yordami ────────────────────────────────────────────────────
STUDY_WORDS = [
    "tushuntir","tushuntirib ber","o'rgat","o'rgatib ber","misol yech",
    "masalani yech","masala yech","yechib ber","hisoblab ber","isbotla",
    "qanday yechiladi","qanday hisoblanadi","formula","teorema","qoidasini",
    "explain","solve","homework","uy vazifa","uy ishi","dars ber","dars qil",
    "matematika","fizika","kimyo","biologiya","geometriya","algebra",
    "grammatika","ingliz tili qoida","masala",
]

def _is_study(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in STUDY_WORDS)


class RaphailAssistant:
    def __init__(self, config: dict,
                 ui_queue: Optional[queue.Queue] = None,
                 stop_event: Optional[threading.Event] = None):

        self.config      = config
        self.ui_queue    = ui_queue          # UI ga event yuborish uchun
        self.stop_event  = stop_event or threading.Event()
        self.running     = False
        self.user        = config.get("user_name", "Daler")

        # ── Ovoz ─────────────────────────────────────────────────────────
        self.speaker = VoiceSpeaker(
            config["voice"],
            on_speaking_start=lambda: self.listener.set_speaking(True),
            on_speaking_end  =lambda: self.listener.set_speaking(False),
        )
        self.listener = VoiceListener(config)

        # ── AI ───────────────────────────────────────────────────────────
        self.brain    = RaphailBrain(config["ai"])
        self.memory   = ConversationMemory(
            config["system"]["memory_file"],
            config["ai"].get("context_window", 20),
        )
        self.reminders = ReminderManager(speak_callback=self._speak_and_emit)

        # ── Boshqaruv ─────────────────────────────────────────────────────
        self.system    = SystemController()
        self.browser   = BrowserController()
        self.code      = CodeWriter()
        self.messenger = MessengerController()
        self.bluetooth = BluetoothController()

    # ─── UI event emitter ────────────────────────────────────────────────────

    def _emit(self, evt_type: str, **kwargs):
        """UI queue ga event yuboradi (UI mavjud bo'lsa)."""
        if self.ui_queue:
            try:
                self.ui_queue.put_nowait({"type": evt_type, **kwargs})
            except queue.Full:
                pass

    def _set_state(self, state: str):
        """Orb + status holati yangilash."""
        self._emit("state", value=state)

    async def _speak_and_emit(self, text: str):
        """Gapirish + UI ga rafael event yuborish."""
        self._emit("rafael", text=text)
        self._set_state("speaking")
        await self.speaker.speak(text)
        self._set_state("sleeping")

    # ─── Main loop ───────────────────────────────────────────────────────────

    async def start(self):
        self.running = True
        self.reminders.start()

        greeting = (
            f"Salom {self.user}! Men RAFAEL. "
            f"Bugun nima qilamiz — proekt qilamizmi yoki dars?"
        ) if self.user else "Tizim faollashtirildi. Men RAFAEL."

        self._emit("system", text="RAFAEL ishga tushdi.")
        await self._speak_and_emit(greeting)
        logger.info("RAFAEL tayyor — wake-word kutilmoqda.")

        while self.running and not self.stop_event.is_set():
            try:
                self._set_state("sleeping")

                # Ovoz ting — wake-word kutamiz
                text = await self.listener.listen()
                if not text:
                    continue

                logger.debug(f"Eshitildi (uxlash): {text!r}")

                found, cleaned = contains_wake_word(text)
                if not found:
                    continue

                logger.info(f"Wake word! Cleaned: {cleaned!r}")

                if cleaned.strip():
                    # "Rafael, chromeni och" — to'g'ridan buyruq
                    self._emit("user", text=cleaned)
                    await self._process(cleaned)
                else:
                    # Faqat "Rafael" deyildi → kutamiz
                    reply = f"Ha, {self.user}." if self.user else "Tinglamoqdaman."
                    await self._speak_and_emit(reply)

                    self._set_state("listening")
                    follow = await self.listener.listen()
                    if follow and follow.strip():
                        self._emit("user", text=follow)
                        await self._process(follow)

                self._set_state("sleeping")

            except KeyboardInterrupt:
                break
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Loop xatosi: {e}", exc_info=True)
                self._emit("error", text=str(e))
                await asyncio.sleep(0.5)

        self.listener.stop()
        logger.info("RAFAEL to'xtatildi.")

    # ─── Process ─────────────────────────────────────────────────────────────

    async def _process(self, text: str):
        if not text.strip():
            return

        logger.info(f"Buyruq: {text!r}")

        # 1. TO'XTATISH
        if is_stop_command(text):
            msg = (f"Xayr, {self.user}. Tizim uxlash rejimiga o'tdi."
                   if self.user else "Tizim to'xtatildi.")
            await self._speak_and_emit(msg)
            self.running = False
            return

        # 2. ESLATMA
        if _is_reminder(text):
            self._set_state("thinking")
            result = self.reminders.add(text)
            reply  = f"{_confirm()} {result}"
            self._emit("cmd", action="reminder", detail=result)
            await self._speak_and_emit(reply)
            return

        # 2.5 TARJIMA — "tarjima qil ...", "... nima degani"
        if _is_translate(text):
            phrase = _extract_translate_phrase(text)
            if not phrase:
                await self._speak_and_emit("Nimani tarjima qilay?")
                return
            self._set_state("thinking")
            self._emit("cmd", action="translate", detail=phrase)
            result = await self.brain.translate(phrase)
            self.memory.add_user(text)
            self.memory.add_assistant(result)
            await self._speak_and_emit(result)
            return

        # 2.6 DARS / O'QISH YORDAMI — repetitor rejimi (uzunroq, bosqichma-bosqich)
        if _is_study(text):
            self._set_state("thinking")
            self._emit("cmd", action="study", detail=text)
            history = self.memory.get_messages()
            result  = await self.brain.tutor(text, history)
            self.memory.add_user(text)
            self.memory.add_assistant(result)
            await self._speak_and_emit(result)
            return

        # 3. PARSER (tez — millisekundlar, multi-command)
        commands = parse(text)
        if commands:
            logger.info(f"Parser: {commands}")
            replies = []
            for cmd in commands:
                self._set_state("thinking")
                self._emit("cmd", action=cmd.get("action",""), detail=str(cmd))
                result = await self._execute(cmd)
                if result:
                    replies.append(result)
            reply = f"{_confirm()} " + ". ".join(replies) if replies else _confirm()
            self.memory.add_user(text)
            self.memory.add_assistant(reply)
            await self._speak_and_emit(reply)
            return

        # 4. Split-parser fallback (STT merge: "rafaelchromenioch")
        words = text.replace("'", " ").split()
        for i in range(len(words)):
            sub = " ".join(words[i:])
            cmds2 = parse(sub)
            if cmds2:
                logger.info(f"Parser (split@{i}): {cmds2}")
                replies = []
                for cmd in cmds2:
                    self._set_state("thinking")
                    self._emit("cmd", action=cmd.get("action",""), detail=str(cmd))
                    result = await self._execute(cmd)
                    if result:
                        replies.append(result)
                reply = f"{_confirm()} " + ". ".join(replies) if replies else _confirm()
                self.memory.add_user(text)
                self.memory.add_assistant(reply)
                await self._speak_and_emit(reply)
                return

        # 5. LLM (murakkab savol / suhbat)
        self._set_state("thinking")
        history  = self.memory.get_messages()
        response = await self.brain.think(text, history)
        logger.info(f"LLM javob: {response[:100]!r}")

        llm_cmd = self._extract_json(response)
        if llm_cmd:
            self._emit("cmd", action=llm_cmd.get("action",""), detail=str(llm_cmd))
            result = await self._execute(llm_cmd)
            reply  = (f"{_confirm()} {result}".strip()
                      if result else _confirm())
        else:
            reply = response

        self.memory.add_user(text)
        self.memory.add_assistant(reply)
        await self._speak_and_emit(reply)

    # ─── Execute ─────────────────────────────────────────────────────────────

    async def _execute(self, cmd: dict) -> str:
        a   = cmd.get("action", "")
        app = cmd.get("app", "")

        try:
            if a == "open_app":        return self.system.open_app(app)
            if a == "close_app":       return self.system.close_app(app)
            if a == "reminder":        return self.reminders.add(cmd.get("text",""))
            if a == "shutdown":        return self.system.shutdown()
            if a == "restart":         return self.system.restart()
            if a == "sleep":           return self.system.sleep()
            if a == "lock":            return self.system.lock()
            if a == "get_time":        return self.system.get_time()
            if a == "screenshot":      return self.system.screenshot()
            if a == "create_file":     return self.system.create_file(cmd.get("path",""), cmd.get("content",""))
            if a == "delete_file":     return self.system.delete_file(cmd.get("path",""))
            if a == "run_command":     return self.system.run_command(cmd.get("command","")) or "Bajarildi."

            if a == "search":
                e = cmd.get("engine","google"); q = cmd.get("query","")
                if e == "yandex":       return self.browser.search_yandex(q)
                if e == "youtube":      return self.browser.search_youtube(q)
                if e == "yandex_music": return self.browser.open_yandex_music(q)
                return self.browser.search_web(q)

            if a == "search_web":      return self.browser.search_web(cmd.get("query",""))
            if a == "search_yandex":   return self.browser.search_yandex(cmd.get("query",""))
            if a == "play_music":      return self.browser.play_music(cmd.get("query",""), cmd.get("service","youtube"))
            if a == "open_youtube":    return self.browser.open_youtube(cmd.get("query"))
            if a == "open_url":        return self.browser.open_url(cmd.get("url",""))
            if a == "open_site":       return self.browser.open_site(cmd.get("site",""))
            if a == "search_video":    return self.browser.search_video(cmd.get("query",""))

            if a == "bluetooth_open":    return self.bluetooth.open_settings()
            if a == "bluetooth_connect": return self.bluetooth.connect_device(cmd.get("device",""))
            if a == "bluetooth_list":    return self.bluetooth.list_devices()

            if a == "volume_up":
                import pyautogui
                for _ in range(5): pyautogui.press("volumeup")
                return "Ovoz oshirildi."
            if a == "volume_down":
                import pyautogui
                for _ in range(5): pyautogui.press("volumedown")
                return "Ovoz kamaytirildi."
            if a == "mute":
                import pyautogui; pyautogui.press("volumemute")
                return "Ovoz o'chirildi."

            if a == "send_telegram":   return self.messenger.send_telegram(cmd.get("contact",""), cmd.get("message",""))
            if a == "open_chat":       return self.messenger.open_telegram_contact(cmd.get("contact",""))
            if a == "search_contact":  return self.messenger.search_contact(cmd.get("name",""))

            if a == "clear_memory":
                self.memory.clear(); return "Xotira tozalandi."

            if a == "write_code":
                r = self.code.write_code(
                    cmd.get("language","python"),
                    cmd.get("description",""),
                    cmd.get("filename"),
                )
                if r.get("success"):
                    self.code.open_in_vscode(r["path"])
                    return "Kod tayyorlandi. VS Code da ochildi."
                return "Kod yozishda xato."

            if a == "run_file":
                return self.code.run_python_file(cmd.get("path",""))

            return ""  # Noma'lum action → LLM javobini ishlat

        except Exception as e:
            logger.error(f"_execute xatosi ({a}): {e}", exc_info=True)
            return "Amalni bajarishda xato."

    # ─── LLM JSON extract ────────────────────────────────────────────────────

    def _extract_json(self, text: str) -> Optional[dict]:
        for m in re.findall(r'\{[^{}]{4,}\}', text, re.DOTALL):
            try:
                d = json.loads(m)
                if d.get("action"):
                    return d
            except Exception:
                pass
        return None
