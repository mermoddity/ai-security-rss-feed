import feedparser
import requests
import datetime

NOTION_TOKEN = "secret_xxx"  # Replace with your actual Notion API token
NOTION_DATABASE_ID = "your_database_id"  # Replace with your Notion database ID

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def post_to_notion(entry, source_name):
    title = entry.get("title", "Untitled")
    url = entry.get("link", "")
    date = entry.get("published", "") or datetime.datetime.utcnow().isoformat()

    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Title": {"title": [{"text": {"content": title}}]},
            "URL": {"url": url},
            "Source": {"rich_text": [{"text": {"content": source_name}}]},
            "Published Date": {"date": {"start": date}}
        }
    }

    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
    print(source_name, res.status_code, res.text)

def fetch_rss_and_post(feed_url, source_name):
    feed = feedparser.parse(feed_url)
    for entry in feed.entries[:5]:
        post_to_notion(entry, source_name)

if __name__ == "__main__":
    fetch_rss_and_post("https://export.arxiv.org/api/query?search_query=all:llm+security&start=0&max_results=10&sortBy=lastUpdatedDate&sortOrder=descending", "Arxiv - LLM Security")
    fetch_rss_and_post("https://feeds.feedburner.com/TheHackersNews", "The Hacker News")
    fetch_rss_and_post("https://www.darkreading.com/rss.xml", "DarkReading")
    fetch_rss_and_post("https://aisnakeoil.substack.com/feed", "AI Snake Oil")
    fetch_rss_and_post("https://attack.mitre.org/rss/", "MITRE ATT&CK / ATLAS")
    fetch_rss_and_post("https://openai.com/blog/rss.xml", "OpenAI Blog")
    fetch_rss_and_post("https://www.anthropic.com/news/rss", "Anthropic News")
    fetch_rss_and_post("https://www.deepmind.com/blog/rss.xml", "Google DeepMind")
