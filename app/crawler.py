# app/crawler.py
from ddgs import DDGS
import requests, json, os, time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def to_naive(dt):
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt

def crawl(query, start_date=None, end_date=None, n=40):
    os.makedirs("data/raw", exist_ok=True)
    out = []

    # 🕒 Auto-select the last 30 days if no range is given
    if not start_date or not end_date:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = to_naive(datetime.fromisoformat(start_date))
        end_date = to_naive(datetime.fromisoformat(end_date))

    print(f"⏳ Searching '{query}' between {start_date.date()} and {end_date.date()}")

    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, region="in-en", safesearch="Off"))
            if not results:
                print("⚠️ No direct news results — falling back to general web search.")
                results = list(ddgs.text(query, region="in-en", safesearch="Off"))

            for r in results:
                if len(out) >= n:
                    break

                url = r.get("url")
                if not url:
                    continue

                # 📰 Parse article date if available
                date_str = r.get("date")
                article_date = None
                if date_str:
                    try:
                        article_date = to_naive(datetime.fromisoformat(date_str.replace("Z", "")))
                    except Exception:
                        pass

                # Apply date filter only if date available
                if article_date and not (start_date <= article_date <= end_date):
                    continue

                try:
                    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).text
                    soup = BeautifulSoup(html, "html.parser")
                    text = soup.get_text(" ", strip=True)
                    if len(text) < 400:
                        continue

                    out.append({
                        "source_url": url,
                        "raw_html": html,
                        "date": article_date.strftime("%Y-%m-%d") if article_date else None
                    })
                    print(f"✅ Fetched: {url}")
                    time.sleep(0.5)
                except Exception as e:
                    print(f"⚠️ Error fetching {url}: {e}")

    except Exception as e:
        print(f"❌ DuckDuckGo search failed: {e}")

    # 📁 Save results
    if not out:
        print("⚠️ No articles found for this query.")
    else:
        out_path = f"data/raw/{query.replace(' ', '_').lower()}_{start_date.date()}_{end_date.date()}.jsonl"
        with open(out_path, "w", encoding="utf-8") as f:
            for o in out:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
        print(f"\n🎯 Saved {len(out)} usable articles to {out_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 4:
        crawl(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 2:
        crawl(sys.argv[1])  # ✅ Auto 30-day range
    else:
        print("Usage: python app/crawler.py '<query>' [<start_date> <end_date>]")
