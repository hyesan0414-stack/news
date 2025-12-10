import feedparser
import requests
from datetime import datetime, timedelta
import os

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
NOTION_VERSION = "2022-06-28"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION,
}

# KST 기준 날짜
KST = datetime.utcnow() + timedelta(hours=9)
TODAY = KST.date()

def fetch_google_news(keyword):
    url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
    return feedparser.parse(url)

def add_to_notion(title, link, published, category, source):
    create_url = "https://api.notion.com/v1/pages"

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "제목": {"title": [{"text": {"content": title}}]},
            "링크": {"url": link},
            "날짜": {"date": {"start": published}},
            "매체": {"select": {"name": source}},
            "카테고리": {"select": {"name": category}},
        },
    }

    response = requests.post(create_url, headers=headers, json=data)
    response.raise_for_status()

def parse_date(entry):
    if getattr(entry, "published_parsed", None):
        dt = datetime(*entry.published_parsed[:6])
        return dt.isoformat
