#!/usr/bin/env python3
"""
Rebuild Vector Index for Real Knowledge Base
Chạy script này để build vector index cho tất cả documents trong KB
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from xiaozhi_final import (
    load_knowledge_index,
    get_vector_engine,
    VECTOR_SEARCH_AVAILABLE,
    KNOWLEDGE_DATA_DIR
)

async def main():
    print("=" * 60)
    print("🔨 REBUILD VECTOR INDEX FOR KNOWLEDGE BASE")
    print("=" * 60)
    
    # Check if vector search available
    if not VECTOR_SEARCH_AVAILABLE:
        print("❌ Vector search not available!")
        print("   Install: pip install sentence-transformers faiss-cpu")
        return
    
    # Load knowledge base
    print("\n📚 Loading knowledge base...")
    index_data = load_knowledge_index()
    documents = index_data.get("documents", [])
    
    if not documents:
        print("❌ No documents in knowledge base!")
        print("   Please index files first via Web UI")
        return
    
    print(f"✅ Loaded {len(documents)} documents")
    for i, doc in enumerate(documents[:5], 1):
        print(f"   {i}. {doc['file_name']} ({len(doc['content'])} chars)")
    if len(documents) > 5:
        print(f"   ... and {len(documents) - 5} more")
    
    # Initialize vector engine
    print("\n🔨 Building vector index...")
    vector_engine = get_vector_engine()
    
    # Prepare documents
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
    
    # Build index
    vector_engine.build_index(documents_data)
    
    # Save index
    vector_engine.save_index()
    
    stats = vector_engine.get_statistics()
    print(f"\n✅ Vector index built and saved!")
    print(f"   Vectors: {stats['num_vectors']}")
    print(f"   Dimensions: {stats['embedding_dim']}")
    print(f"   Index path: {KNOWLEDGE_DATA_DIR / 'vector_index.faiss'}")
    
    # Test search
    print("\n🔍 Testing vector search...")
    test_query = "ngày 24 tháng 11 năm 2025 nhóm nghiên cứu thu thập mẫu"
    results = vector_engine.vector_search(test_query, top_k=3)
    
    print(f"\nQuery: '{test_query[:50]}...'")
    print("-" * 60)
    for i, r in enumerate(results, 1):
        print(f"{i}. {r.metadata['file_name']}")
        print(f"   Score: {r.score:.4f}")
        print(f"   Preview: {r.text[:80]}...")
        print()
    
    print("=" * 60)
    print("✅ DONE! Restart xiaozhi_final.py to use vector search")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
