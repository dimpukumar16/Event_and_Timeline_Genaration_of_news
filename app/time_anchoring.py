import re
import dateparser
import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt', quiet=True)

def tag_sentences(text, doc_date=None):
    sents = sent_tokenize(text)
    out = []
    for s in sents:

        # try to detect YYYY-MM-DD explicitly
        m = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", s)
        if m:
            d = m.group(1)
        else:
            # fallback: use document date only
            d = doc_date

        out.append({"sentence": s, "date": d})
    return out
