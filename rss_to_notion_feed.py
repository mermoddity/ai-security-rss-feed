import feedparser
import requests
import datetime
import os
from email.utils import parsedate_to_datetime

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_existing_entries():
    """
    Query the Notion database to get all existing entries.
    Returns a set of URLs that are already in the database.
    """
    existing_urls = set()
    has_more = True
    start_cursor = None
    
    while has_more:
        query_data = {
            "database_id": NOTION_DATABASE_ID,
            "filter": {
                "property": "URL",
                "url": {
                    "is_not_empty": True
                }
            },
            "page_size": 100  # Maximum allowed by Notion API
        }
        
        if start_cursor:
            query_data["start_cursor"] = start_cursor
            
        response = requests.post(
            "https://api.notion.com/v1/databases/query",
            headers=headers,
            json=query_data
        )
        
        if response.status_code == 200:
            result = response.json()
            for page in result.get("results", []):
                url = page.get("properties", {}).get("URL", {}).get("url", "")
                if url:
                    existing_urls.add(url)
                    
            has_more = result.get("has_more", False)
            start_cursor = result.get("next_cursor")
        else:
            print(f"Error querying Notion database: {response.status_code}, {response.text}")
            break
    
    return existing_urls

def post_to_notion(entry, source_name):
    title = entry.get("title", "Untitled")
    url = entry.get("link", "")

    # Convert to ISO 8601 date
    raw_date = entry.get("published", "")
    try:
        iso_date = parsedate_to_datetime(raw_date).isoformat()
    except Exception:
        iso_date = datetime.datetime.utcnow().isoformat()

    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Title": {"title": [{"text": {"content": title}}]},
            "URL": {"url": url},
            "Source": {"rich_text": [{"text": {"content": source_name}}]},
            "Published Date": {"date": {"start": iso_date}}
        }
    }

    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
    print(f"{source_name} - {title}: {res.status_code}")

def fetch_rss_and_post(feed_url, source_name, existing_urls):
    """
    Fetch RSS feed and post entries that don't already exist in the Notion database.
    """
    feed = feedparser.parse(feed_url)
    new_entries = 0
    skipped_entries = 0
    
    for entry in feed.entries[:10]:  # Increased from 5 to 10 to get more content
        url = entry.get("link", "")
        if url and url not in existing_urls:
            post_to_notion(entry, source_name)
            existing_urls.add(url)  # Add to set to prevent duplicates within the same run
            new_entries += 1
        else:
            skipped_entries += 1
    
    print(f"{source_name}: {new_entries} new entries added, {skipped_entries} duplicates skipped")

if __name__ == "__main__":
    # Get all existing entries once at the beginning
    print("Fetching existing entries from Notion database...")
    existing_urls = get_existing_entries()
    print(f"Found {len(existing_urls)} existing entries")
    
    # List of RSS feeds to process
    rss_feeds = [
        ("https://export.arxiv.org/api/query?search_query=all:llm+security&start=0&max_results=10&sortBy=lastUpdatedDate&sortOrder=descending", "Arxiv - LLM Security"),
        ("https://feeds.feedburner.com/TheHackersNews", "The Hacker News"),
        ("https://www.darkreading.com/rss.xml", "DarkReading"),
        ("https://www.aisnakeoil.com/feed", "AI Snake Oil"),
        ("https://attack.mitre.org/rss/", "MITRE ATT&CK / ATLAS"),
        ("https://openai.com/blog/rss.xml", "OpenAI Blog"),
        ("https://rsshub.app/anthropic/news", "Anthropic News"),
        ("https://www.deepmind.com/blog/rss.xml", "Google DeepMind")
    ]
    
    # Process each feed
    for feed_url, source_name in rss_feeds:
        print(f"Processing {source_name}...")
        fetch_rss_and_post(feed_url, source_name, existing_urls)
