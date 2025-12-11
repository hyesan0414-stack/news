import feedparser
import requests
from datetime import datetime, timedelta

NOTION_API_KEY = "***"
DATABASE_ID = "***"

KEYWORDS_FILE = "keywords.txt"

RSS_FEEDS = [
    "https://www.me.go.kr/board/rss.do",
    "https://www.ytn.co.kr/rss/environment.xml"
]

def load_keywords():
    try:
        with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("❌ keywords.txt 파일이 없습니다.")
        return []

def fetch_articles():
    today = datetime.utcnow().date()
    articles = []

    for url in RSS_FEEDS:
        print(f"🔍 Fetching: {url}")
        feed = feedparser.parse(url)

        for entry in feed.entries:
            try:
                published = datetime(*entry.published_parsed[:6]).date()
            except:
                continue

            if published != today:
                continue

            articles.append({
                "title": entry.title,
                "link": entry.link,
                "summary": getattr(entry, "summary", ""),
                "category": getattr(entry, "category", "기타"),
            })

    return articles

def filter_by_keywords(articles, keywords):
    filtered = []
    for article in articles:
        text = f"{article['title']} {article['summary']}"
        if any(keyword in text for keyword in keywords):
            filtered.append(article)
    return filtered

def create_notion_page(article):
    url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Title": {"title": [{"text": {"content": article["title"]}}]},
            "URL": {"url": article["link"]},
            "Category": {"rich_text": [{"text": {"content": article["category"]}}]},
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": article["summary"]}}]
                }
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"✅ 노션 저장 완료: {article['title']}")
    else:
        print(f"❌ 노션 저장 실패: {response.status_code} - {response.text}")

def main():
    print("🚀 Auto News Clipping Started")

    keywords = load_keywords()
    articles = fetch_articles()

    print(f"🔎 오늘 기사 수: {len(articles)}")

    filtered = filter_by_keywords(articles, keywords)
    print(f"✨ 키워드 필터링 결과: {len(filtered)}개 기사")

    for article in filtered:
        create_notion_page(article)

    print("🎉 작업 완료!")

if __name__ == "__main__":
    main()
