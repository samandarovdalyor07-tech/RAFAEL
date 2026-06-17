"""
RAFAEL - System Controller
"""

import os, subprocess, shutil, psutil, time, webbrowser
from datetime import datetime
from pathlib import Path
from core.utils.logger import get_logger

logger = get_logger(__name__)

# Ish stolida o'rnatilmagan bo'lsa — brauzerda ochiladigan ilovalar
WEB_APPS = {
    "spotify":  "https://open.spotify.com",
    "youtube":  "https://www.youtube.com",
    "whatsapp": "https://web.whatsapp.com",
    "telegram_web": "https://web.telegram.org",
}

APP_PATHS = {
    "chrome":      [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"],
    "firefox":     [r"C:\Program Files\Mozilla Firefox\firefox.exe"],
    "edge":        [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"],
    "vscode":      [os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
                    r"C:\Program Files\Microsoft VS Code\Code.exe"],
    "telegram":    [os.path.expandvars(r"%APPDATA%\Telegram Desktop\Telegram.exe"),
                    os.path.expandvars(r"%LOCALAPPDATA%\Telegram Desktop\Telegram.exe")],
    "spotify":     [os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe")],
    "notepad":     ["notepad.exe"],
    "calculator":  ["calc.exe"],
    "explorer":    ["explorer.exe"],
    "taskmgr":     ["taskmgr.exe"],
    "cmd":         ["cmd.exe"],
    "powershell":  ["powershell.exe"],
    "terminal":    ["wt.exe", "cmd.exe"],
    "word":        [os.path.expandvars(r"%PROGRAMFILES%\Microsoft Office\root\Office16\WINWORD.EXE")],
    "excel":       [os.path.expandvars(r"%PROGRAMFILES%\Microsoft Office\root\Office16\EXCEL.EXE")],
    "vlc":         [r"C:\Program Files\VideoLAN\VLC\vlc.exe"],
    "notepad++":   [r"C:\Program Files\Notepad++\notepad++.exe"],
}

NAME_MAP = {
    "xrom":"chrome","xrome":"chrome","brauzer":"chrome","google":"chrome",
    "firefox":"firefox","edge":"edge",
    "telegaram":"telegram","telegarm":"telegram","telegramm":"telegram",
    "bloknot":"notepad","matn muharriri":"notepad",
    "kalkulyator":"calculator","hisoblash":"calculator","kalьkulyator":"calculator",
    "fayl menejeri":"explorer","papkalar":"explorer","mening kompyuterim":"explorer",
    "terminal":"terminal","konsol":"terminal","buyruq satri":"cmd",
    "powershell":"powershell",
    "vazifa menejeri":"taskmgr","task manager":"taskmgr",
    "vs kod":"vscode","vs code":"vscode","kod muharriri":"vscode","visual studio":"vscode",
    "spotify":"spotify","musiqa":"spotify",
    "vlc":"vlc","video":"vlc",
    "word":"word","excel":"excel",
    # Russian
    "хром":"chrome","браузер":"chrome","телеграм":"telegram",
    "блокнот":"notepad","калькулятор":"calculator","проводник":"explorer",
    "терминал":"terminal","музыка":"spotify",
}


def _find_exe(key: str) -> str | None:
    for path in APP_PATHS.get(key, []):
        p = path if os.path.isabs(path) else shutil.which(path)
        if p and os.path.exists(p):
            return p
    found = shutil.which(key)
    return found


class SystemController:
    def open_app(self, app_name: str) -> str:
        name = app_name.lower().strip()
        name = NAME_MAP.get(name, name)

        # 1. Haqiqiy EXE topib ishga tushirish
        exe = _find_exe(name)
        if exe:
            try:
                subprocess.Popen([exe], shell=False)
                logger.info(f"Ochildi: {exe}")
                return f"{app_name} ochildi."
            except Exception as e:
                logger.warning(f"Popen xato: {e}")

        # 2. ms-settings: yoki to'liq yo'l bo'lsa
        if name.startswith("ms-settings") or os.path.isabs(name):
            try:
                os.startfile(name)
                logger.info(f"startfile: {name}")
                return f"{app_name} ochildi."
            except Exception as e:
                logger.warning(f"startfile xato: {e}")

        # 3. Web-ilova fallback (spotify, youtube, ...)
        if name in WEB_APPS:
            webbrowser.open(WEB_APPS[name])
            logger.info(f"Web ochildi: {WEB_APPS[name]}")
            return f"{app_name} brauzerda ochildi."

        # 4. Rostini ayt — topilmadi (YOLG'ON 'ochildi' DEMAYMIZ)
        logger.warning(f"Ilova topilmadi: {app_name} ({name})")
        return f"Kechirasiz, {app_name} ilovasini topa olmadim."

    def close_app(self, app_name: str) -> str:
        name = NAME_MAP.get(app_name.lower().strip(), app_name.lower())
        closed = []
        for proc in psutil.process_iter(["name", "pid"]):
            try:
                pname = proc.info["name"].lower()
                if name in pname or pname.startswith(name[:5]):
                    proc.terminate()
                    closed.append(proc.info["name"])
            except Exception:
                pass
        return f"{set(closed)} yopildi." if closed else f"{app_name} topilmadi."

    def shutdown(self) -> str:
        subprocess.run("shutdown /s /t 3", shell=True)
        return "Noutbuk 3 soniyadan keyin o'chadi."

    def restart(self) -> str:
        subprocess.run("shutdown /r /t 3", shell=True)
        return "Noutbuk qayta ishga tushadi."

    def sleep(self) -> str:
        subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        return "Uxlash rejimi."

    def lock(self) -> str:
        subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
        return "Ekran qulflandi."

    def cancel_shutdown(self) -> str:
        subprocess.run("shutdown /a", shell=True)
        return "O'chirish bekor qilindi."

    def create_file(self, path: str, content: str = "") -> str:
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return f"Fayl yaratildi: {path}"
        except Exception as e:
            return f"Xato: {e}"

    def delete_file(self, path: str) -> str:
        try:
            p = Path(path)
            if p.is_file():
                p.unlink(); return f"O'chirildi: {path}"
            elif p.is_dir():
                shutil.rmtree(p); return f"Papka o'chirildi: {path}"
            return f"Topilmadi: {path}"
        except Exception as e:
            return f"Xato: {e}"

    def run_command(self, command: str) -> str:
        try:
            r = subprocess.run(command, shell=True, capture_output=True,
                               text=True, timeout=30, encoding="utf-8", errors="replace")
            out = (r.stdout or r.stderr or "").strip()
            return (out[:400] + "...") if len(out) > 400 else (out or "Bajarildi.")
        except subprocess.TimeoutExpired:
            return "Vaqt tugadi."
        except Exception as e:
            return f"Xato: {e}"

    def get_time(self) -> str:
        oylar = ["", "yanvar", "fevral", "mart", "aprel", "may", "iyun",
                 "iyul", "avgust", "sentyabr", "oktyabr", "noyabr", "dekabr"]
        n = datetime.now()
        return f"Soat {n.hour:02d}:{n.minute:02d}, {n.day}-{oylar[n.month]}."

    def screenshot(self, path: str = None) -> str:
        try:
            import pyautogui
            if not path:
                path = str(Path.home() / "Desktop" / f"screen_{int(time.time())}.png")
            pyautogui.screenshot(path)
            return f"Ekran rasm saqlandi: {path}"
        except Exception as e:
            return f"Xato: {e}"
