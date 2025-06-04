import feedparser
import requests
import datetime
import os
import json # Added json import
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
        # database_id is now part of the URL, not the query_data body
        query_data = {
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
            f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query", # Corrected URL
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
    
    # Get summary content from the entry
    summary = entry.get("summary", "")
    # Some feeds use 'content' instead of 'summary'
    if not summary and entry.get("content"):
        summary = "".join(c.value for c in entry.get("content", []))
    # Fallback to description if available
    if not summary and entry.get("description"):
        summary = entry.get("description")

    # Convert to ISO 8601 date
    raw_date = entry.get("published", "")
    try:
        # First try parsing as ISO 8601 format
        if raw_date and ('T' in raw_date or '-' in raw_date):
            # Handle ISO 8601 format directly
            try:
                # Try parsing with datetime directly
                parsed_date = datetime.datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
                iso_date = parsed_date.isoformat()
            except ValueError:
                # If direct parsing fails, try with parsedate_to_datetime
                iso_date = parsedate_to_datetime(raw_date).isoformat()
        else:
            # Use email parser for RFC 2822 format
            iso_date = parsedate_to_datetime(raw_date).isoformat()
    except Exception as e:
        print(f"Date parsing error for '{raw_date}': {str(e)}")
        iso_date = datetime.datetime.utcnow().isoformat()

    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Title": {"title": [{"text": {"content": title}}]},
            "URL": {"url": url},
            "Source": {"rich_text": [{"text": {"content": source_name}}]},
            "Published Date": {"date": {"start": iso_date}},
            "Summary": {"rich_text": [{"text": {"content": summary[:2000] if summary else ""}}]}
        }
    }

    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
    print(f"{source_name} - {title}: {res.status_code}")

def fetch_rss_and_post(feed_url, source_name, filters, existing_urls): # Added 'filters' parameter
    """
    Fetch RSS feed and post entries that don't already exist in the Notion database.
    """
    feed = feedparser.parse(feed_url)

    # Check for HTTP errors or other parsing issues
    if hasattr(feed, 'status') and feed.status == 404:
        print(f"Error: Feed URL {feed_url} returned HTTP 404 Not Found. Skipping this feed.")
        return # Skip processing this feed
    elif feed.bozo:
        # bozo is 1 if the feed is ill-formed (e.g., XML errors, network issues other than 404)
        # feed.bozo_exception often contains the specific error
        bozo_reason = str(feed.get('bozo_exception', 'Unknown parsing error'))
        print(f"Warning: Feed {feed_url} may be ill-formed or inaccessible. Reason: {bozo_reason}. Attempting to process...")

    new_entries = 0
    skipped_entries_duplicate = 0
    skipped_entries_filter = 0
    
    for entry in feed.entries[:100]:  # Increased from 5 to 10 to get more content
        url = entry.get("link", "")

        # Keyword filtering logic
        if filters: # Only filter if filters are provided
            title_content = entry.get("title", "").lower()
            summary_content = entry.get("summary", "").lower() # feedparser uses 'summary' for <description>
            # Some feeds might use 'content' instead of 'summary'
            content_details = "".join(c.value for c in entry.get("content", [])) if entry.get("content") else ""
            content_details = content_details.lower()

            match_found = False
            for keyword in filters:
                if keyword.lower() in title_content or keyword.lower() in summary_content or keyword.lower() in content_details:
                    match_found = True
                    break
            if not match_found:
                skipped_entries_filter += 1
                continue # Skip this entry if no keyword matches

        if url and url not in existing_urls:
            post_to_notion(entry, source_name)
            existing_urls.add(url)  # Add to set to prevent duplicates within the same run
            new_entries += 1
        else:
            skipped_entries_duplicate += 1
    
    print(f"{source_name}: {new_entries} new entries added, {skipped_entries_duplicate} duplicates skipped, {skipped_entries_filter} filtered out")

if __name__ == "__main__":
    # Get all existing entries once at the beginning
    print("Fetching existing entries from Notion database...")
    existing_urls = get_existing_entries()
    print(f"Found {len(existing_urls)} existing entries")

    # Load RSS feed configurations from JSON file
    feeds_config_path = os.path.join(os.path.dirname(__file__), 'ai_security_feeds.json')
    try:
        with open(feeds_config_path, 'r') as f:
            rss_feeds_config = json.load(f)
    except FileNotFoundError:
        print(f"Error: 'ai_security_feeds.json' not found at {feeds_config_path}")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode 'ai_security_feeds.json'. Make sure it's valid JSON.")
        exit(1)

    # Process each feed from the configuration
    for feed_info in rss_feeds_config:
        source_name = feed_info.get("name")
        feed_url = feed_info.get("url")
        filters = feed_info.get("filters", []) # Default to empty list if not present

        if not feed_url: # Skip if no URL is provided (e.g. for manual feeds)
            print(f"Skipping {source_name} as no URL is provided.")
            continue

        print(f"Processing {source_name} with URL {feed_url}...")
        fetch_rss_and_post(feed_url, source_name, filters, existing_urls)
