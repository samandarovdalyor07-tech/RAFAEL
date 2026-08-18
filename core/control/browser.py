"""
RAFAEL - Browser Controller
Google, Yandex, YouTube, Yandex Music va boshqalarni boshqaradi.
"""

import webbrowser
import urllib.parse
from core.utils.logger import get_logger

logger = get_logger(__name__)

ENGINES = {
    "google":        "https://www.google.com/search?q=",
    "yandex":        "https://yandex.ru/search/?text=",
    "youtube":       "https://www.youtube.com/results?search_query=",
    "yandex_music":  "https://music.yandex.ru/search?text=",
    "yandex_video":  "https://yandex.ru/video/search?text=",
    "yandex_images": "https://yandex.ru/images/search?text=",
}

# TTS chiroyli o'qishi uchun ko'rsatiladigan nomlar
ENGINE_NAMES = {
    "google":        "Google",
    "yandex":        "Yandeks",
    "youtube":       "YouTube",
    "yandex_music":  "Yandeks Muzika",
    "yandex_video":  "Yandeks Video",
    "yandex_images": "Yandeks Rasmlar",
}

SITES = {
    "google":       "https://www.google.com",
    "yandex":       "https://yandex.ru",
    "youtube":      "https://www.youtube.com",
    "yandex music": "https://music.yandex.ru",
    "yandex muzika":"https://music.yandex.ru",
    "yandex muzika":"https://music.yandex.ru",
    "github":       "https://github.com",
    "gmail":        "https://mail.google.com",
    "telegram web": "https://web.telegram.org",
    "chatgpt":      "https://chat.openai.com",
    "wikipedia":    "https://uz.wikipedia.org",
}

SITE_NAMES = {
    "google":       "Google",
    "yandex":       "Yandeks",
    "youtube":      "YouTube",
    "yandex music": "Yandeks Muzika",
    "github":       "GitHub",
    "gmail":        "Gmail",
    "telegram web": "Telegram",
    "chatgpt":      "ChatGPT",
    "wikipedia":    "Vikipediya",
}


class BrowserController:
    def open_url(self, url: str) -> str:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        webbrowser.open(url)
        logger.info(f"URL: {url}")
        return "ochib berdim"

    def search(self, query: str, engine: str = "google") -> str:
        """Istalgan qidiruv tizimida qidiradi"""
        base = ENGINES.get(engine.lower(), ENGINES["google"])
        url = base + urllib.parse.quote(query)
        webbrowser.open(url)
        logger.info(f"{engine} qidiruv: {query}")
        return f"{ENGINE_NAMES.get(engine.lower(), engine)}dan qidirib berdim"

    def search_web(self, query: str) -> str:
        return self.search(query, "google")

    def search_yandex(self, query: str) -> str:
        return self.search(query, "yandex")

    def search_youtube(self, query: str) -> str:
        return self.search(query, "youtube")

    def play_music(self, query: str, service: str = "youtube") -> str:
        """Musiqa/qo'shiq topadi — YouTube yoki Yandex Music"""
        if service in ("yandex", "yandex music", "yandex_music"):
            return self.search(query, "yandex_music")
        return self.search(query, "youtube")

    def open_yandex_music(self, query: str = None) -> str:
        if query:
            return self.search(query, "yandex_music")
        webbrowser.open("https://music.yandex.ru")
        return "Yandeks Muzikani ochdim"

    def open_youtube(self, query: str = None) -> str:
        if query:
            return self.search(query, "youtube")
        webbrowser.open("https://www.youtube.com")
        return "YouTube ochildi"

    def open_site(self, site: str) -> str:
        """Mashhur saytlarni ochadi"""
        url = SITES.get(site.lower())
        if url:
            webbrowser.open(url)
            return f"{SITE_NAMES.get(site.lower(), site)}ni ochdim"
        return self.open_url(site)

    def search_video(self, query: str) -> str:
        """Yandex Video da qidiradi"""
        return self.search(query, "yandex_video")
