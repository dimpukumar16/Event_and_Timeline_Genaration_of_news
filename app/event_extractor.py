# app/event_extractor.py (TEMPORARY: Rule-Based Fallback)
import json
import re

# NOTE: This temporary solution allows the rest of your pipeline (process.py, 
# graph_compressor.py) to run without an LLM API key.

def extract_causal_event(text_chunk, query_topic):
    """
    TEMPORARY: Simulates LLM analysis using simple rule-based extraction 
    and date parsing to get structured data.
    """
    
    # 1. Simple Summary Extraction (Using the first few sentences)
    # The real LLM would be abstractive; we use the lead sentences.
    sentences = re.split(r'(?<=[.!?])\s+', text_chunk.strip())
    milestone_summary = sentences[0] if sentences else text_chunk[:100] + "..."
    
    # 2. Mock Date Extraction (Simplified)
    # The actual date parsing is already handled in clean.py, but we ensure YYYY-MM-DD format here.
    event_date = "2025-01-01" # Placeholder or use dateparser if available
    
    # 3. Rule-Based Causal Link (Mocking the Causal Agent)
    # We look for common causal phrases to simulate the link.
    
    # Look for a preceding sentence/phrase that seems like a cause
    causal_phrases = ["due to", "following the", "in response to", "after the"]
    causal_agent = f"General {query_topic} development" 
    causal_link_strength = "TEMPORAL_SEQUENCE" # Default weakest link
    
    for phrase in causal_phrases:
        if phrase in text_chunk.lower():
            causal_agent = f"Preceding event related to '{phrase}'"
            causal_link_strength = "ENABLING_CONDITION"
            break

    # Final Structured Output (Matches the format required by graph_compressor.py)
    return {
        "event_date": event_date,
        "milestone_summary": milestone_summary,
        "causal_agent": causal_agent,
        "causal_link_strength": causal_link_strength,
        "doc_date": "2025-01-01" # Add doc_date fallback
    }

# 🚨 Remove or comment out the LLM client placeholder from the previous step.
# You now only need the extract_causal_event function.