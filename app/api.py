# app/api.py (FINAL VERSION WITH SUBPROCESS FIX)
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from app.crawler import crawl
from app.timeline import load_causal_events, to_timeline, choose_processed_path
import os, json
import subprocess 
from pathlib import Path # 🚨 NEW: Required for robust path handling

# --- Configuration for Subprocess ---
# 🚨 CRITICAL FIX: Define the path to your VENV's Python executable 🚨
# This ensures the subprocess uses the Python interpreter where bs4, etc., are installed.
# We build the path relative to the current working directory (os.getcwd())
# The path is constructed as: CWD / venv / Scripts / python.exe
VENV_PYTHON = str(Path(os.getcwd()) / "venv" / "Scripts" / "python.exe")


# DEFINE THE 'app' VARIABLE HERE BEFORE ANY ROUTE DECORATORS
app = FastAPI(title="🗂 News Timeline Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "✅ News Timeline Generator API is running!"}


@app.get("/timeline")
def generate_timeline(q: str = Query(..., min_length=3, description="Search topic (e.g., 'Women's Cricket World Cup 2025')")):
    """
    Crawl, process, and generate a **CAUSAL** timeline for the given query.
    """

    # 1️⃣ Crawl new data
    print(f"🚀 Crawling fresh news for '{q}'...")
    crawl(q)

    # 2️⃣ Run processor (THIS NOW RUNS LLM EXTRACTION)
    print("⚙️ Starting data processing and causal event extraction...")
    try:
        # 💡 FINAL FIX: Use the VENV_PYTHON executable to run the module.
        subprocess.run([VENV_PYTHON, "-m", "app.process"], 
                       check=True, 
                       capture_output=True, 
                       text=True)
        print("✅ Processing complete.")
    except subprocess.CalledProcessError as e:
        # If process.py fails, print the error output from the subprocess
        print(f"❌ Error during processing:\n{e.stderr}")
        return {"query": q, "timeline": [], "error": f"❌ Data processing failed: {e.stderr}"}

    # 3️⃣ Dynamically choose the latest *CAUSAL EVENT* file
    latest_path = choose_processed_path()
    if not latest_path or "causal_events" not in latest_path:
        return {"query": q, "timeline": [], "error": "❌ No causal event files found after process."}

    print(f"🧠 Using latest processed file: {latest_path}")

    # 4️⃣ Load structured causal events (NEW)
    causal_events = load_causal_events(latest_path)
    if not causal_events:
        return {"query": q, "timeline": [], "error": "⚠️ No structured causal events found."}

    # 5️⃣ Run Causal Graph Compression (NEW)
    tl = to_timeline(causal_events)
    print(f"✅ Causal Timeline generated with {len(tl)} events.")

    return {"query": q, "timeline": tl}