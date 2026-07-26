"""
Build a small KB of ~5000 Wikipedia documents.
Uses the modern HuggingFace `wikimedia/wikipedia` dataset (Parquet-based).
"""
from datasets import load_dataset
import json
from pathlib import Path
from tqdm import tqdm

OUTPUT_DIR = Path("kb_data")
OUTPUT_DIR.mkdir(exist_ok=True)

TARGET_COUNT = 5000

print(f"Downloading Wikipedia subset (target: {TARGET_COUNT} docs)...")

# Use the modern Parquet-based Wikipedia dataset
ds = load_dataset(
    "wikimedia/wikipedia",
    "20231101.en",
    split="train",
    streaming=True
)

docs = []
for item in tqdm(ds, total=TARGET_COUNT, desc="Streaming"):
    if len(docs) >= TARGET_COUNT:
        break
    # Filter out stubs and very short docs
    if not item.get("text") or len(item["text"]) < 200:
        continue
    docs.append({
        "id": f"wiki_{len(docs)}",
        "title": item["title"],
        "text": item["text"][:2000],   # First 2000 chars per doc
        "source": "wikipedia",
        "url": item.get("url", ""),
    })

output_file = OUTPUT_DIR / "kb_docs.jsonl"
with open(output_file, "w") as f:
    for doc in docs:
        f.write(json.dumps(doc) + "\n")

print(f"✓ Saved {len(docs)} documents to {output_file}")
print(f"  Avg doc length: {sum(len(d['text']) for d in docs) / len(docs):.0f} chars")
print(f"  First doc: '{docs[0]['title']}'")
