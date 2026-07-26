"""
Build FAISS vector index using sentence-transformers.
Mac-compatible: forces CPU, small batches to avoid segfault.
"""
import os
# Set BEFORE importing torch
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

import json
import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from pathlib import Path
from tqdm import tqdm

KB_FILE = Path("kb_data/kb_docs.jsonl")
INDEX_DIR = Path("vector_store")
INDEX_DIR.mkdir(exist_ok=True)

# Force CPU - avoids MPS-related segfaults on Mac
DEVICE = "cpu"
print(f"Using device: {DEVICE}")

print("Loading embedding model...")
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2", device=DEVICE)

print("Loading docs...")
docs = [json.loads(l) for l in KB_FILE.open()]
texts = [d["text"] for d in docs]
print(f"  Loaded {len(docs)} documents")

print("Embedding in batches (smaller batch = stabler on Mac)...")
# Smaller batch size to prevent memory pressure
all_embeddings = []
BATCH_SIZE = 8  # was 32 - smaller is safer on Mac

for i in tqdm(range(0, len(texts), BATCH_SIZE)):
    batch = texts[i:i+BATCH_SIZE]
    embs = model.encode(
        batch,
        batch_size=BATCH_SIZE,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    all_embeddings.append(embs)

embeddings = np.vstack(all_embeddings).astype(np.float32)
print(f"  Generated embeddings shape: {embeddings.shape}")

# Save FAISS index (inner product since embeddings are normalized = cosine sim)
dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)
index.add(embeddings)
faiss.write_index(index, str(INDEX_DIR / "kb.faiss"))

# Save doc metadata (include full text - we need it for retrieval display)
meta = [
    {"id": d["id"], "title": d["title"], "source": d["source"], "text": d["text"]}
    for d in docs
]
with open(INDEX_DIR / "kb_meta.json", "w") as f:
    json.dump(meta, f)

print(f"\n✓ Built FAISS index: {len(docs)} vectors, dim {dim}")
print(f"  Index: {INDEX_DIR}/kb.faiss")
print(f"  Metadata: {INDEX_DIR}/kb_meta.json")

# Sanity test
print("\n--- Sanity check ---")
test_query = "Who founded Tesla Motors?"
print(f"Query: {test_query}")
q_emb = model.encode([test_query], normalize_embeddings=True, convert_to_numpy=True)
distances, indices = index.search(q_emb.astype(np.float32), k=3)
for rank, (idx, dist) in enumerate(zip(indices[0], distances[0]), 1):
    print(f"  {rank}. (sim={dist:.3f}) {meta[idx]['title']}")
