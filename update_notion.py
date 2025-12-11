import feedparser
import requests
from datetime import datetime, timedelta
import os

# -------------------------
# 환경 변수
# -------------------------
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# -------------------------
# RSS 목록
# -------------------------
RSS_FEEDS = [
    "https://www.ytn.co.kr/rss/environment.xml",
    "https://www.me.go.kr/board/rss.do"
]

# -------------------------
# 키워드 로드
# -------------------------
def load_keywords():
    with open("keywords.txt", "r", encoding="utf-8") as f:
        return [kw.strip() for kw in f.readlines() if kw.strip()]

KEYWORDS = load_keywords()

# -------------------------
# 기사 가져오기
# -------------------------
def fetch_articles():
    today = datetime.utcnow() + timedelta(hours=9)  # 한국시간
    today_date = today.date()

    results = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for item in feed.entries:
            # 날짜 파싱
            try:
                pub_date = datetime(*item.published_parsed[:6])
            except:
                continue

            pub_date_kst = pub_date + timedelta(hours=9)
            if pub_date_kst.date() != today_date:
                continue

            # 키워드 필터
            text = f"{item.title} {item.get('summary', '')}"
            if not any(k in text for k in KEYWORDS):
                continue

            # 저장
            results.append({
                "title": item.title,
                "url": item.link,
                "summary": item.get("summary", ""),
                "date": pub_date_kst.strftime("%Y-%m-%d %H:%M")
            })

    return results

# -------------------------
# Notion 업로드
# -------------------------
def push_to_notion(article):
    url = "https://api.notion.com/v1/pages"
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Title": {
                "title": [{"text": {"content": article["title"]}}]
            },
            "URL": {
                "url": article["url"]
            },
            "Date": {
                "date": {"start": article["date"]}
            },
            "Summary": {
                "rich_text": [{"text": {"content": article["summary"]}}]
            }
        }
    }
    requests.post(url, headers=headers, json=data)

# -------------------------
# 실행
# -------------------------
if __name__ == "__main__":
    articles = fetch_articles()
    print(f"Found {len(articles)} articles")

    for article in articles:
        push_to_notion(article)

    print("Done. Uploaded to Notion.")
