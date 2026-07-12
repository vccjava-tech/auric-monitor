"""Firecrawl search integration."""
import requests
from config import FIRECRAWL_API_KEY

def search_news(query, limit=5):
    if not FIRECRAWL_API_KEY:
        return {"error": "no key", "results": []}
    try:
        r = requests.post("https://api.firecrawl.dev/v1/search", 
            headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"},
            json={"query": query, "limit": limit}, timeout=5)
        d = r.json()
        return {"results": [{"title": i.get("title",""), "snippet": i.get("snippet",""), "url": i.get("url","")} for i in d.get("data",[])]}
    except Exception as e:
        return {"error": str(e), "results": []}

def scrape_page(url):
    if not FIRECRAWL_API_KEY: return {"error": "no key"}
    try:
        r = requests.post("https://api.firecrawl.dev/v1/scrape",
            headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"},
            json={"url": url, "formats": ["markdown"]}, timeout=8)
        return r.json()
    except Exception as e: return {"error": str(e)}