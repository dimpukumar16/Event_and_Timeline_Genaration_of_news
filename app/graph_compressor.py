# app/graph_compressor.py
import networkx as nx
import numpy as np
import os

# Use existing embedding and clustering functions
from app.embed import embed 
from app.cluster import build_index 

# 1. Define Causal Link Weights (for structural analysis)
CAUSAL_WEIGHTS = {
    'DIRECT_CAUSE': 1.0,
    'ENABLING_CONDITION': 0.8,
    'TEMPORAL_SEQUENCE': 0.5,
}

def build_causal_graph(causal_events: list):
    """Builds a directed, weighted graph where nodes are events and edges are causal/semantic links."""
    G = nx.DiGraph() 
    
    for i, event in enumerate(causal_events):
        G.add_node(i, data=event) 

    summaries = [e.get('milestone_summary', '') for e in causal_events]
    # Filter out empty strings before embedding
    valid_summaries_indices = [i for i, s in enumerate(summaries) if s]
    valid_summaries = [summaries[i] for i in valid_summaries_indices]

    if not valid_summaries: return G

    embs = embed(valid_summaries)
    index = build_index(embs) 
    
    # 2. Add Edges based on LLM's explicit Causal Link
    for i in valid_summaries_indices:
        event_i = causal_events[i]
        agent = event_i.get('causal_agent')
        if not agent or agent in ["None", "none"]:
            continue
            
        try:
            # Embed the causal agent and search for the best match in the event summaries
            agent_emb = embed([agent])
            # Search against the embeddings of valid summaries
            D_agent, I_agent = index.search(agent_emb.astype("float32"), 2) 
            
            # Use index 1 of I_agent for the best match (index 0 is the agent itself if it was in the summaries)
            # We need to map the result index (I_agent) back to the original index (j)
            
            if D_agent.size > 1 and D_agent[0][1] > 0.65: # Threshold similarity
                valid_summaries_index = I_agent[0][1] # Index in the valid_summaries list
                j = valid_summaries_indices[valid_summaries_index] # Original index (the CAUSE)

                if i != j:
                    llm_link_type = event_i.get('causal_link_strength', 'TEMPORAL_SEQUENCE')
                    weight = CAUSAL_WEIGHTS.get(llm_link_type, 0.5)

                    # Add directed edge from the CAUSE (j) to the EFFECT (i)
                    G.add_edge(j, i, weight=weight) 
        except Exception as e:
            # print(f"⚠️ Error processing causal link for event {i}: {e}")
            continue

    return G

def compress_timeline(G: nx.DiGraph, top_k_events: int = 10):
    """Compresses the graph by selecting the most salient nodes using PageRank."""
    
    if not G.nodes:
        return []

    # Calculate Node Saliency (Centrality/Importance)
    salience_scores = nx.pagerank(G, weight='weight')
    
    # Rank Events by score
    ranked_indices = sorted(salience_scores, key=salience_scores.get, reverse=True)
    
    # Select Top K (Compression)
    final_timeline_events = []
    
    for rank_idx in ranked_indices:
        if len(final_timeline_events) >= top_k_events:
            break
        
        event_data = G.nodes[rank_idx]['data']
        final_timeline_events.append(event_data)
        
    # Final sort by date
    return sorted(final_timeline_events, key=lambda x: x.get('event_date') or "9999-99-99", reverse=True)


def generate_causal_timeline(causal_events: list, top_k: int = 10):
    """Orchestrates graph building and compression."""
    G = build_causal_graph(causal_events)
    return compress_timeline(G, top_k)