# app/timeline.py (FINAL CRITICAL VERSION with choose_processed_path FIX)
import os
import sys
import json
import numpy as np
from typing import List

# 💡 NEW IMPORTS: Use the Graph Compressor instead of the old cluster logic
try:
    from app.embed import embed 
    from app.graph_compressor import generate_causal_timeline 
except ImportError:
    # Fallback for direct execution (e.g., python app/timeline.py)
    # Assumes local imports are available
    from embed import embed
    from graph_compressor import generate_causal_timeline


def choose_processed_path():
    """
    Dynamically pick the newest *causal event* file in data/processed/.
    This utility function must be defined here so app/api.py can import it.
    """
    processed_dir = "data/processed"
    if not os.path.exists(processed_dir):
        return None

    # Collect all processed .jsonl files that start with 'causal_events_'
    files = [
        os.path.join(processed_dir, f)
        for f in os.listdir(processed_dir)
        if f.endswith(".jsonl") and f.startswith("causal_events_")
    ]

    if not files:
        return None

    # Prefer newest by modification time (this relies on the os module)
    latest = max(files, key=os.path.getmtime)
    print(f"🧠 Using latest processed file: {latest}")
    return latest


# 🚨 New Function: Load the structured causal events
def load_causal_events(processed_path: str):
    """Loads structured causal events (JSONL format) created by app/process.py."""
    if not os.path.exists(processed_path):
        return []

    causal_events = []
    with open(processed_path, encoding="utf-8") as f:
        for line in f:
            try:
                event_data = json.loads(line)
                causal_events.append(event_data)
            except Exception:
                continue
    return causal_events


def to_timeline(causal_events: List[dict]):
    """
    Runs Causal Graph Modeling and Compression to select salient events.
    This replaces the simple semantic clustering.
    """
    if not causal_events:
        return []

    print(f"🧠 Running Causal Graph Analysis on {len(causal_events)} extracted events...")
    
    # 🔑 CORE NOVELTY: Call the Graph Compressor
    # top_k=10 is the max events to display
    compressed_timeline = generate_causal_timeline(causal_events, top_k=10) 

    final_output = []
    for event in compressed_timeline:
        # Use the structured data fields for clean output
        final_output.append({
            # Prioritize the LLM-extracted event_date, fallback to doc_date
            "date": event.get("event_date", event.get("doc_date")), 
            "summary": event.get("milestone_summary", "Summary not available."),
            "url": event.get("source_url"),
            "causal_agent": event.get("causal_agent") 
        })
        
    print(f"✅ Final Causal Timeline generated with {len(final_output)} milestone events.")
    return final_output


def main(keyword: str = "Operation Sindoor"):
    # Find the NEW file path created by the updated process.py
    processed_dir = "data/processed"
    if not os.path.exists(processed_dir):
        print("Error: Directory 'data/processed' not found. Please run `python app/process.py` first.")
        return
    
    # Use the defined utility function to find the latest file
    processed_path = choose_processed_path() 
    if not processed_path:
         print("Error: No 'causal_events_' files found. Please run `python app/process.py` first.")
         return
         
    print(f"Loading structured causal events from: {processed_path}")
    
    causal_events = load_causal_events(processed_path)
    if not causal_events:
        print(f"No structured events found for '{keyword}'.")
        return

    timeline = to_timeline(causal_events)
    
    # 📝 Print for console review
    for e in timeline:
        print(f'[{e["date"]}] — {e["summary"]}')
        if e.get("causal_agent"):
            print(f' ➡️ Caused by: {e["causal_agent"]}')
        print(f'   Source: {e.get("url")}\n')

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "Operation Sindoor"
    main(q)