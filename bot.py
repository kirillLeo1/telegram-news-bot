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
import pytz

# 🔎 Вставь свой ключ
TOKEN = "7918775198:AAFCyInMQMed_GDo0HXBnRPxTrGB-IhaGnY"
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
    "https://news.liga.net/news/rss.xml",     # Лига.Новости
]

# 🧠 Инициализация бота
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# 📂 Храним последние опубликованные новости, чтобы не дублировать
posted_links = set()

def clean_html(text):
    """Удаляет HTML-теги, оставляя только текст"""
    return re.sub(r"<[^>]+>", "", text)

async def fetch_news():
    """ 🖉 Публикует новости в зависимости от времени суток."""
    global posted_links
    tz = pytz.timezone("Europe/Kyiv")

    while True:
        now = datetime.now(tz)
        if 0 <= now.hour < 7:
            num_posts = 3
            total_minutes = (7 * 60) - (now.hour * 60 + now.minute)
            if num_posts > total_minutes:
                await asyncio.sleep(60)
                continue
            post_times = sorted([datetime.now() + timedelta(minutes=random.randint(1, total_minutes)) for _ in range(num_posts)])
        else:
            num_posts = 4
            post_times = sorted([datetime.now() + timedelta(minutes=random.randint(1, 59)) for _ in range(num_posts)])

        news_posts = []
        for feed_url in RSS_FEEDS:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:3]:
                title = entry.title
                link = entry.link
                summary = entry.summary if hasattr(entry, "summary") else "Нет описания"
                summary = clean_html(summary)
                if link in posted_links:
                    continue
                post_text = f"<b>{hbold(title)}</b>\n\n{summary}\n\n<a href='{link}'>Читати повністью</a>"
                news_posts.append(post_text)
                posted_links.add(link)

        selected_posts = random.sample(news_posts, min(num_posts, len(news_posts)))

        for post_text, post_time in zip(selected_posts, post_times):
            wait_time = (post_time - datetime.now()).total_seconds()
            print(f"⏳ Ожидание до публикации: {wait_time // 60:.0f} минут")
            await asyncio.sleep(wait_time)
            await bot.send_message(CHANNEL_ID, post_text)

        print("📰 Посты опубликованы, ждем следующий цикл")
        await asyncio.sleep(60)  # Короткая пауза до нового цикла

async def main():
    await fetch_news()

if __name__ == "__main__":
    asyncio.run(main())


