from nltk.tokenize import sent_tokenize

EVENT_VERBS = [
    "said", "announced", "confirmed", "reported",
    "claimed", "blamed", "launched", "held",
    "accused", "warned", "requested", "approved",
    "banned", "met", "protested", "arrested"
]

def event_summary(text):
    sentences = sent_tokenize(text)
    best = None
    best_score = -1

    for s in sentences:
        score = sum(1 for v in EVENT_VERBS if v in s.lower())
        if score > best_score:
            best = s
            best_score = score

    return best.strip() if best else sentences[0].strip()
