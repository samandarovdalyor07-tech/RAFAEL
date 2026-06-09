"""
RAPHAIL - Code Writer
Tasvirga asoslanib kod yozadi va faylga saqlaydi.
"""

import os
import subprocess
from pathlib import Path
import anthropic
from core.utils.logger import get_logger

logger = get_logger(__name__)

CODE_SYSTEM = """Sen tajribali dasturchi assistentsan.
Foydalanuvchi so'ragan kodni FAQAT kod bilan qaytarishing kerak.
Izoh yoki tushuntirish BERMA — faqat ishlaydigan kod.
Kod blokidan tashqari hech narsa yozma."""


class CodeWriter:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def write_code(self, language: str, description: str, filename: str = None) -> dict:
        """Tasvirlangan kodni yozadi"""
        try:
            prompt = f"Yoz: {description}\nTil: {language}"

            response = self.client.messages.create(
                model="claude-opus-4-8",
                max_tokens=4096,
                system=CODE_SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            )
            code = response.content[0].text.strip()

            # Kod bloklarni tozalaymiz
            if code.startswith("```"):
                lines = code.split("\n")
                code = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

            # Fayl nomini aniqlaymiz
            if not filename:
                ext_map = {
                    "python": "py", "javascript": "js", "typescript": "ts",
                    "html": "html", "css": "css", "java": "java",
                    "c": "c", "cpp": "cpp", "rust": "rs", "go": "go",
                }
                ext = ext_map.get(language.lower(), "txt")
                filename = f"raphail_code.{ext}"

            # Desktop ga saqlaymiz
            desktop = Path.home() / "Desktop" / filename
            desktop.parent.mkdir(parents=True, exist_ok=True)
            with open(desktop, "w", encoding="utf-8") as f:
                f.write(code)

            logger.info(f"Kod yozildi: {desktop}")
            return {
                "success": True,
                "path": str(desktop),
                "language": language,
                "lines": len(code.splitlines()),
            }

        except Exception as e:
            logger.error(f"Kod yozishda xato: {e}")
            return {"success": False, "error": str(e)}

    def run_python_file(self, file_path: str) -> str:
        """Python faylini ishga tushiradi"""
        try:
            result = subprocess.run(
                ["python", file_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout or result.stderr
            return output[:500] if output else "Kod bajarildi, chiqish yo'q."
        except Exception as e:
            return f"Ishga tushirishda xato: {e}"

    def open_in_vscode(self, path: str) -> str:
        """Faylni VS Code da ochadi"""
        try:
            subprocess.Popen(["code", path], shell=True)
            return f"VS Code da ochildi: {path}"
        except Exception as e:
            return f"VS Code da ochib bo'lmadi: {e}"
