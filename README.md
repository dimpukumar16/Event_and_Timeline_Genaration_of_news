# Causal Narrative Timeline Generator

This project implements a **novel Open-Domain Timeline Summarization (TLS)** pipeline that generates **narrative-driven, causally coherent timelines** instead of simple chronological lists.  
It explicitly models **cause–effect relationships** between events using a causal graph and structural influence scoring.

Built as a **FastAPI microservice**, the system runs an end-to-end pipeline from search → event extraction → graph compression → final narrative timeline generation.


## 🧠 Methodology: Three-Phase Pipeline

### **1. Acquisition & Cleaning**
- `crawler.py` fetches articles via DuckDuckGo  
- `clean.py` extracts clean text using BeautifulSoup  
- Produces clean, ready-to-parse documents  

---

### **2. Structural Causal Analysis (Core Novelty)**

#### **Causal Extraction — `event_extractor.py`**
- Identifies **event**, **cause**, **effect**  
- Assigns a **causal link strength**  
- Uses rule-based patterns mimicking LLM behavior  

#### **Graph Modeling — `graph_compressor.py`**
- Builds a **Directed Causal Graph**
  - Nodes = events  
  - Edges = causal influence  
- Applies **PageRank** to compute event importance  
- Compresses to essential **“backbone events”**  

---

### **3. Final Timeline Generation — `timeline.py`**
- Selects **top-K most influential events**  
- Produces a short, coherent, narrative timeline  
- Explains the chain of events clearly and abstractively  

---

## 🛠️ Setup & Execution

### **1. Prerequisites**
- Python **3.9+**

---

## **2. Installation**

Clone the repo:

```bash
git clone https://github.com/dimpukumar16/Event_and_Timeline_Genaration_of_news.git
cd Event_and_Timeline_Genaration_of_news
```
## **3. Running the Application**

Start FastAPI server:
```bash
uvicorn app.api:app --reload
```

Server starts at:

```bash
http://127.0.0.1:8000
```

## **4. Using the Web UI**

```bash
UI/index.html
```

