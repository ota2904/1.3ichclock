#!/usr/bin/env python3
"""
Simple Vector Index Builder - No xiaozhi_final import
"""

import json
from pathlib import Path
from vector_search import VectorSearchEngine

# Paths
KNOWLEDGE_DATA_DIR = Path.home() / ".miniz_mcp" / "knowledge"
KNOWLEDGE_INDEX_FILE = KNOWLEDGE_DATA_DIR / "knowledge_index.json"
VECTOR_INDEX_PATH = KNOWLEDGE_DATA_DIR / "vector_index"

print("=" * 60)
print("🔨 BUILD VECTOR INDEX")
print("=" * 60)

# Load KB
print("\n📚 Loading knowledge base...")
with open(KNOWLEDGE_INDEX_FILE, 'r', encoding='utf-8-sig') as f:
    index_data = json.load(f)

documents = index_data.get("documents", [])
print(f"✅ Loaded {len(documents)} documents")
for i, doc in enumerate(documents[:5], 1):
    print(f"   {i}. {doc['file_name']}")

# Build index
print("\n🔨 Building vector index...")
engine = VectorSearchEngine(index_path=str(VECTOR_INDEX_PATH))

documents_data = [
    {
        "id": f"doc_{i}",
        "text": doc["content"],
        "metadata": {
            "file_name": doc["file_name"],
            "file_path": doc["file_path"],
            "index": i
        }
    }
    for i, doc in enumerate(documents)
]

engine.build_index(documents_data)
engine.save_index()

stats = engine.get_statistics()
print(f"\n✅ Vector index built!")
print(f"   Vectors: {stats['num_vectors']}")
print(f"   Dimensions: {stats['embedding_dim']}")

# Test
print("\n🔍 Testing...")
query = "ngày 24 tháng 11 năm 2025 nhóm nghiên cứu thu thập mẫu"
results = engine.vector_search(query, top_k=3)

print(f"\nQuery: '{query[:50]}...'")
for i, r in enumerate(results, 1):
    print(f"{i}. {r.metadata['file_name']}: {r.score:.4f}")

print("\n✅ DONE! Restart server to use vector search")
