import json, numpy as np
import faiss
import networkx as nx


def build_index(vecs):
    d=vecs.shape[1]; index=faiss.IndexFlatIP(d); index.add(vecs.astype("float32"))
    return index

def knn_graph(embs, k=8, sim_thr=0.55):
    index=build_index(embs)
    D,I = index.search(embs.astype("float32"), k+1)  # self + neighbors
    G=nx.Graph()
    for i in range(len(embs)): G.add_node(i)
    for i in range(len(embs)):
        for j,sim in zip(I[i][1:], D[i][1:]):
            if sim>=sim_thr:
                G.add_edge(i, int(j), weight=float(sim))
    return G

def connected_components(G):
    return [list(c) for c in nx.connected_components(G)]
