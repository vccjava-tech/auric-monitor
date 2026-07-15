"""Firecrawl search integration with Jina Reader fallback."""
import requests
from config import FIRECRAWL_API_KEY

def search_news(query, limit=5):
    if not FIRECRAWL_API_KEY:
        return {"error": "no key", "results": []}
    try:
        r = requests.post("https://api.firecrawl.dev/v1/search",
            headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"},
            json={"query": query, "limit": limit}, timeout=0.5)
        d = r.json()
        return {"results": [{"title": i.get("title",""), "snippet": i.get("snippet",""), "url": i.get("url","")} for i in d.get("data",[])]}
    except Exception as e:
        return {"error": str(e), "results": []}

def scrape_page(url):
    if not FIRECRAWL_API_KEY: return {"error": "no key"}
    try:
        r = requests.post("https://api.firecrawl.dev/v1/scrape",
            headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"},
            json={"url": url, "formats": ["markdown"]}, timeout=0.5)
        return r.json()
    except Exception as e: return {"error": str(e)}



def direct_scrape(url):
    """Fallback: directly scrape a page and extract visible text."""
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}, timeout=6)
        # Accept non-200 (some sites return 404 with content)
        pass
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        title = soup.title.string.strip() if soup.title else ""
        text = soup.get_text(separator=" ", strip=True)[:1500]
        return {"title": title, "text": text}
    except:
        return {"title": "", "text": ""}
def jina_fetch(url):
    """Fetch page content using free Jina Reader API. Returns markdown text."""
    try:
        jina_url = "https://r.jina.ai/" + url
        r = requests.get(jina_url, headers={"User-Agent": "Mozilla/5.0", "Accept": "text/plain"}, timeout=0.5)
        if r.status_code == 200:
            return r.text[:1500]
    except:
        pass
    return ""
