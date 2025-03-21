import asyncio
import feedparser
import requests
import re
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from aiogram.utils.markdown import hbold
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties

# 🔹 Вставь свои ключи
TOKEN = "7918775198:AAFCYlnMQMed_GDo0HXBnRPxTrGB-IhaGnY"
CHANNEL_ID = "@newspoliticcccals"
TOGETHER_AI_API_KEY = "9b98ca24fd81a201eb22ba1d9603f27b96cf7122f8e9a9e70b392b2ca678ab6c"

# 🔹 Список RSS-источников (новости из Украины)
RSS_FEEDS = [
    "https://www.pravda.com.ua/rss/view_news/",
    "https://tsn.ua/rss/full.rss",
    "https://24tv.ua/rss/all.xml",
    "https://rss.unian.net/site/news_ukr.rss",
    "https://news.liga.net/news/rss.xml",
    "https://www.rbc.ua/static/rss/all.rus.rss.xml",
]

# Инициализация бота
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Храним последние опубликованные новости, чтобы не дублировать
posted_links = set()

def clean_html(text):
    """Удаляет HTML-теги, оставляя только текст"""
    return re.sub(r'<[^>]+>', '', text)

async def fetch_news():
    """Публикует 5 постов в час в случайное время."""
    global posted_links
    while True:
        try:
            news_posts = []
            for feed_url in RSS_FEEDS:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]:  # Берем последние 3 новости из каждого источника
                    title = entry.title
                    link = entry.link
                    summary = entry.summary if hasattr(entry, "summary") else "Нет описания"
                    summary = clean_html(summary)

                    if link in posted_links:
                        continue

                    post_text = f"📰 {hbold(title)}\n\n{summary}\n\n🔗 <a href='{link}'>Читать полностью</a>"
                    news_posts.append(post_text)
                    posted_links.add(link)

            if news_posts:
                # Выбираем 5 случайных постов и 5 случайных времени в течение часа
                selected_posts = random.sample(news_posts, min(5, len(news_posts)))
                post_times = sorted([datetime.now() + timedelta(minutes=random.randint(1, 59)) for _ in range(len(selected_posts))])

                for post_text, post_time in zip(selected_posts, post_times):
                    wait_time = (post_time - datetime.now()).total_seconds()
                    print(f"🕒 Ожидание до публикации: {wait_time // 60:.0f} минут ({post_time.strftime('%H:%M')})")
                    await asyncio.sleep(wait_time)
                    await bot.send_message(CHANNEL_ID, post_text)

            print("✅ Новости опубликованы, ждем следующий час.")
        except Exception as e:
            print(f"⚠ Ошибка при публикации новостей: {e}")
        await asyncio.sleep(3600)  # Ждём 1 час перед следующим запуском

async def main():
    """Запускает процесс публикации новостей"""
    await fetch_news()

if __name__ == "__main__":
    asyncio.run(main())
