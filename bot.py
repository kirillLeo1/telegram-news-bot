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

# 🔑 Вставь свои ключи
TOKEN = "7918775198:AAFCYlnMQMed_GDo0HXBnRPxTrGB-IhaGnY"
CHANNEL_ID = "@newspoliticcccals"

# 📡 Только украиноязычные и политически-военные источники
RSS_FEEDS = [
    "https://censor.net/rss/all.xml",
    "https://glavcom.ua/rss/all.xml",
    "https://focus.ua/rss/all.xml",
    "https://telegraf.com.ua/rss.xml",
    "https://www.pravda.com.ua/rss/view_news/",
    "https://tsn.ua/rss/full.rss",
    "https://24tv.ua/rss/all.xml",
    "https://rss.unian.net/site/news_ukr.rss",
    "https://news.liga.net/news/rss.xml",
]

# ⚙️ Инициализация бота
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# 🧠 Храним последние опубликованные новости, чтобы не дублировать
posted_links = set()


def clean_html(text):
    """🧹Удаляет HTML-теги, оставляя только текст"""
    return re.sub(r"<[^>]+>", "", text)


async def fetch_news():
    """📬 Публикует новости в зависимости от времени суток"""
    global posted_links
    while True:
        now = datetime.now()
        current_hour = now.hour

        if 0 <= current_hour < 7:
            num_posts = 3
            interval_minutes = 60  # на 7 часов — посты в среднем каждые ~2 часа
            period_minutes = 420   # 7 часов * 60 мин
        else:
            num_posts = 4
            interval_minutes = 60  # каждый час
            period_minutes = 60

        try:
            news_posts = []
            for feed_url in RSS_FEEDS:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]:  # Берем последние 3 новости из каждого источника
                    title = entry.title
                    link = entry.link
                    summary = entry.summary if hasattr(entry, "summary") else "Немає опису"
                    summary = clean_html(summary)

                    if link in posted_links:
                        continue

                    post_text = f"📰 <b>{hbold(title)}</b>\n\n{summary}\n\n🔗 <a href='{link}'>Читати повністю</a>"
                    news_posts.append(post_text)
                    posted_links.add(link)

            if news_posts:
                selected_posts = random.sample(news_posts, min(num_posts, len(news_posts)))
                post_times = sorted([now + timedelta(minutes=random.randint(1, interval_minutes))
                                     for _ in range(len(selected_posts))])

                for post_text, post_time in zip(selected_posts, post_times):
                    wait_time = (post_time - datetime.now()).total_seconds()
                    print(f"⏱ Очікування до публікації: {wait_time // 60:.0f} хв ({post_time.strftime('%H:%M')})")
                    await asyncio.sleep(wait_time)
                    await bot.send_message(CHANNEL_ID, post_text)

            print("✅ Новини опубліковані. Чекаємо наступного періоду.")
        except Exception as e:
            print(f"⚠️ Помилка при публікації новин: {e}")

        await asyncio.sleep(period_minutes * 60)


async def main():
    """🚀 Запускає процес публікації новин"""
    await fetch_news()


if __name__ == "__main__":
    asyncio.run(main())

