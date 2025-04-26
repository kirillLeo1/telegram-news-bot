import asyncio
import feedparser
import requests
import re
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from aiogram.utils.markdown import hbold
from aiogram.enums.parse_mode import ParseMode
import pytz

# 🔎 Вставь свой ключ
TOKEN = "7918775198:AAFCYlnMQMed_GDo0HXBnRPxTrGB-IhaGnY"
CHANNEL_ID = "@newspoliticcccals"

# 🌍 Список RSS-источников (Только на укр языке и по теме политики/война)
RSS_FEEDS = [
    "https://censor.net/rss/all.xml",         # Цензор.НЕТ (политика, война)
    "https://glavcom.ua/rss/all.xml",        # Главком (политика, аналитика)
    "https://telegraf.com.ua/rss.xml",       # Телеграф (новости, экономика)
    "https://focus.ua/rss/all.xml",          # Фокус (аналитика, политика, война)
    "https://tsn.ua/rss/full.rss",           # ТСН
    "https://24tv.ua/rss/all.xml",           # 24 канал
    "https://rss.unian.net/site/news_ukr.rss", # УНИАН
]

# 🧠 Инициализация бота
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# 📂 Храним последние опубликованные новости, чтобы не дублировать
posted_links = set()

def clean_html(text):
    """Удаляет HTML-теги, оставляя только текст"""
    return re.sub(r"<[^>]+>", "", text)

async def fetch_news():
    """Публикуем по одному посту в час только с 06:00 до 23:59 Kyiv time."""
    global posted_links
    tz = pytz.timezone("Europe/Kyiv")

    while True:
        now = datetime.now(tz)
        hour = now.hour
        # Проверяем, в разрешённом ли мы окне
        if 6 <= hour <= 23:
            # Собираем все непросланные новости
            news_posts = []
            for feed_url in RSS_FEEDS:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]:
                    if entry.link in posted_links:
                        continue
                    title = entry.title
                    summary = clean_html(entry.summary) if hasattr(entry, "summary") else "Нет описания"
                    post_text = (
                        f"<b>{hbold(title)}</b>\n\n"
                        f"{summary}\n\n"
                        f"<a href='{entry.link}'>Читати повністю</a>"
                    )
                    news_posts.append(post_text)
                    posted_links.add(entry.link)

            if news_posts:
                post = random.choice(news_posts)
                await bot.send_message(CHANNEL_ID, post)
                print(f"✅ {now.strftime('%H:%M')} — опубликовали 1 пост, ждём следующий час")
            else:
                print(f"⚠️ {now.strftime('%H:%M')} — новых новостей нет, ждём час")
        else:
            # Спим без постов
            print(f"😴 {now.strftime('%H:%M')} — спим до 6:00, очередная проверка через час")

        # Ждём ровно 1 час перед следующей итерацией
        await asyncio.sleep(3600)

async def main():
    await fetch_news()

if __name__ == "__main__":
    asyncio.run(main())


