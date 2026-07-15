import json, os
from datetime import date as _date

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "daily_cache.json")

def load():
    if not os.path.exists(CACHE_FILE):
        return None, None
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get("date") != str(_date.today()):
            return None, None
        return d.get("fc_cache", {}), d.get("etf_data", {})
    except:
        return None, None

def save(fc_cache, etf_data):
    d = {"date": str(_date.today()), "fc_cache": fc_cache, "etf_data": etf_data}
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def clear():
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
