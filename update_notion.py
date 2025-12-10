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

# 오늘 날짜(KST)
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
        return dt.isoformat(), dt.date()
    return None, None

# 키워드 목록
with open("keywords.txt", "r", encoding="utf-8") as f:
    KEYWORDS = [line.strip() for line in f if line.strip()]

for kw in KEYWORDS:
    feed = fetch_google_news(kw)

    for entry in feed.entries:
        published_iso, published_date = parse_date(entry)

        # 오늘 뉴스만
        if published_date != TODAY:
            continue

        title = entry.title
        link = entry.link
        source = entry.source.title if hasattr(entry, "source") else "Google News"

        add_to_notion(
            title=title,
            link=link,
            published=published_iso,
            category=kw,
            source=source,
        )
