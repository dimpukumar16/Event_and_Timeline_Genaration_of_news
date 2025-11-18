import shutil

files = [
    "data/processed/articles.jsonl",
    "data/processed/articles_old.jsonl"
]

with open("data/processed/articles_all.jsonl", "wb") as w:
    for fpath in files:
        with open(fpath, "rb") as f:
            shutil.copyfileobj(f, w)

print("✅ Merged successfully → data/processed/articles_all.jsonl")
