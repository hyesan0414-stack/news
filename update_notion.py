import os
import feedparser
import requests
from datetime import datetime
from urllib.parse import quote

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["DATABASE_ID"]

NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_VERSION = "2022-06-28"

headers = {
    "Authorization": f"Bearer NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION,
}

def add_to_notion(title, url, date_iso, source, category):
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "제목": {
                "title": [
                    {"text": {"content": title[:2000]}}
                ]
            },
            "링크": {"url": url},
            "날짜": {"date": {"start": date_iso}},
            "매체": {"select": {"name": source}},
            "카테고리": {"select": {"name": category}},
        },
    }

    resp = requests.post(NOTION_API_URL, headers=headers, json=data)
    if resp.status_code >= 300:
        print("Notion error:", resp.status_code, resp.text)

def parse_date(entry):
    if getattr(entry, "published_parsed", None):
        return datetime(*entry.published_parsed[:6]).isoformat()
    return datetime.utcnow().isoformat()

def main():
    with open("keywords.txt", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    for kw in keywords:
        q = quote(kw)
        rss_url = (
            f"https://news.google.com/rss/search?q={q}"
            f"&hl=ko&gl=KR&ceid=KR:ko"
        )
        print("Fetch keyword:", kw, "->", rss_url)

        feed = feedparser.parse(rss_url)

        for entry in feed.entries:
            title = entry.title
            link = entry.link
            date_iso = parse_date(entry)
            source = entry.get("source", {}).get("title", "Google News")
            category = kw

            add_to_notion(title, link, date_iso, source, category)

if __name__ == "__main__":
    main()
