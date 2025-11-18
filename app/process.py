import os
import json
from datetime import datetime
from bs4 import BeautifulSoup
import re

# Import the new structural analysis tool using relative path
from .event_extractor import extract_causal_event 
# Note: extract_text_from_html is now defined within this file, 
# or should be fully imported from .clean. We will define it here 
# for simplicity, as we can assume the clean logic is self-contained.


# --- 1. UTILITY FUNCTIONS (Needed by the main logic) ---

def find_latest_raw():
    """Find the newest raw news file in data/raw."""
    raw_dir = "data/raw"
    files = [
        os.path.join(raw_dir, f)
        for f in os.listdir(raw_dir)
        if f.endswith(".jsonl")
    ]
    if not files:
        raise FileNotFoundError("No raw files found in data/raw/")
    latest = max(files, key=os.path.getmtime)
    # print(f"🧩 Using latest raw file: {latest}") # Commented out print to clean subprocess output
    return latest


BOILERPLATE_PATTERNS = [
    r"(?i)Advertisement", r"(?i)Subscribe", r"(?i)Read More", r"(?i)Most Popular",
    r"(?i)Latest Stories", r"(?i)Continue reading", r"(?i)Story continues",
    r"(?i)Click/Scan to Subscribe", r"(?i)Tags", r"(?i)©", r"(?i)Follow us",
    r"(?i)Contact Us", r"(?i)About Us", r"(?i)Related Articles", r"(?i)Sponsored"
]

def extract_text_from_html(html: str) -> str:
    """
    Robust heuristic article text extractor (uses BeautifulSoup only).
    Note: This is assumed to be the extraction logic now used after removing trafilatura.
    """
    try:
        soup = BeautifulSoup(html, "html.parser")

        # remove scripts/styles
        for t in soup(["script", "style", "noscript", "iframe", "svg"]):
            t.decompose()

        # 1) Try <article>
        article = soup.find("article")
        if article:
            text = article.get_text(" ", strip=True)
        else:
            # 2) Try common main/content ids/classes
            selectors = [
                {"id": "main"}, {"id": "content"}, {"class_": "article-body"},
                {"class_": "post-content"}, {"class_": "story-body"}, {"class_": "entry-content"}
            ]
            text = None
            for s in selectors:
                tag = soup.find(attrs=s)
                if tag:
                    text = tag.get_text(" ", strip=True)
                    break

            # 3) fallback: meta description / og:description
            if not text or len(text.split()) < 40:
                meta = soup.find("meta", {"name": "description"}) or soup.find("meta", {"property": "og:description"})
                if meta and meta.get("content"):
                    text = meta.get("content").strip()

            # 4) fallback to entire page text
            if not text:
                text = soup.get_text(" ", strip=True)

        # remove boilerplate patterns
        for pat in BOILERPLATE_PATTERNS:
            text = re.sub(pat, " ", text)

        # remove "Story continues" or "End of Article..." fragments
        text = re.sub(r"(?i)story continues.*", " ", text)
        text = re.sub(r"(?i)end of article.*", " ", text)

        # collapse whitespace
        text = " ".join(text.split())

        return text

    except Exception:
        # fallback to naive get_text
        return BeautifulSoup(html or "", "html.parser").get_text(" ", strip=True)


# --- 2. MAIN PROCESSING LOGIC (The updated function) ---

def process_raw_to_processed(input_path):
    """Convert raw JSONL to clean processed JSONL containing structured causal events."""
    os.makedirs("data/processed", exist_ok=True)
    
    # Extract the query topic from the filename for better LLM context
    topic_parts = os.path.basename(input_path).split('_')
    
    if len(topic_parts) >= 3 and re.match(r"\d{4}-\d{2}-\d{2}", topic_parts[-1].split('.')[0]):
        query_topic = " ".join(topic_parts[:-2]).replace("_", " ")
    else:
        query_topic = "General News Topic"


    output_path = os.path.join(
        "data/processed",
        f"causal_events_{os.path.basename(input_path)}"
    )

    processed_events = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                html = obj.get("raw_html", "")
                if not html.strip():
                    continue
                
                # 1. Clean Text & Get Date
                # We assume extract_text_from_html is correctly defined in app/clean.py
                text = extract_text_from_html(html)
                doc_date = obj.get("date") # Date retrieved by the crawler (e.g., "2025-11-15")

                # 🚨 DATE FIX 1: Ensure date is always a valid string
                if not doc_date:
                    doc_date = date.today().isoformat()

                # 2. 🔑 Core Novelty Step: Extract Structured Causal Event
                causal_data = extract_causal_event(text, query_topic)

                if causal_data and causal_data.get('milestone_summary'):
                    
                    # 🚨 DATE FIX 2: Correct the LLM's event_date if it's using the mock placeholder.
                    llm_extracted_date = causal_data.get('event_date')
                    
                    # If the LLM's mock date is static, use the crawler's date (doc_date)
                    # We check against the literal placeholder date that was used.
                    if llm_extracted_date in ["2025-01-01", "YYYY-MM-DD", None] or llm_extracted_date == date.today().isoformat():
                        causal_data['event_date'] = doc_date 
                    
                    # Store the original publication date from the document
                    causal_data['doc_date'] = doc_date 

                    # Merge structured data with source info
                    processed_events.append({
                        "source_url": obj.get("source_url"),
                        **causal_data # Add the structured event and causal links
                    })

            except Exception as e:
                # In a robust system, we would log this error.
                continue
                
    with open(output_path, "w", encoding="utf-8") as out:
        for p in processed_events:
            out.write(json.dumps(p, ensure_ascii=False) + "\n")

    # Final print statement without Unicode to avoid Windows console errors
    print(f"Processed {len(processed_events)} causal events -> {output_path}")

# --- 3. MAIN EXECUTION BLOCK (Where the NameError occurred) ---
if __name__ == "__main__":
    try:
        latest_raw = find_latest_raw()
        process_raw_to_processed(latest_raw)
    except FileNotFoundError as e:
        print(f" Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")