#!/usr/bin/env python3
"""
Test Vector Search Integration
Kiểm tra xem vector_search.py có hoạt động với knowledge base thực không
"""

import json
from pathlib import Path
from vector_search import VectorSearchEngine

# Paths
KNOWLEDGE_DATA_DIR = Path.home() / ".miniz_mcp" / "knowledge"
KNOWLEDGE_INDEX_FILE = KNOWLEDGE_DATA_DIR / "knowledge_index.json"
VECTOR_INDEX_PATH = KNOWLEDGE_DATA_DIR / "vector_index"

def load_knowledge_index():
    """Load knowledge base index"""
    if KNOWLEDGE_INDEX_FILE.exists():
        with open(KNOWLEDGE_INDEX_FILE, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    return {"documents": [], "total_chunks": 0, "last_update": ""}

def build_vector_index():
    """Build vector index from knowledge base"""
    print("=" * 60)
    print("📚 LOADING KNOWLEDGE BASE")
    print("=" * 60)
    
    index_data = load_knowledge_index()
    documents = index_data.get("documents", [])
    
    if not documents:
        print("❌ No documents found in knowledge base")
        print(f"   Index file: {KNOWLEDGE_INDEX_FILE}")
        return None
    
    print(f"✅ Loaded {len(documents)} documents")
    for i, doc in enumerate(documents[:3], 1):
        print(f"   {i}. {doc['file_name']} ({len(doc['content'])} chars)")
    
    print("\n" + "=" * 60)
    print("🔨 BUILDING VECTOR INDEX")
    print("=" * 60)
    
    # Initialize engine
    engine = VectorSearchEngine(index_path=str(VECTOR_INDEX_PATH))
    
    # Prepare data in correct format: [{"id": str, "text": str, "metadata": dict}]
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
    engine.build_index(documents_data)
    
    # Save index (uses path from __init__)
    engine.save_index()
    
    stats = engine.get_statistics()
    print(f"✅ Index built and saved!")
    print(f"   Vectors: {stats['num_vectors']}")
    print(f"   Dimensions: {stats['embedding_dim']}")
    print(f"   Model: {stats.get('model_info', 'N/A')}")
    
    return engine

def test_search(engine):
    """Test vector search"""
    print("\n" + "=" * 60)
    print("🔍 TESTING VECTOR SEARCH")
    print("=" * 60)
    
    test_queries = [
        "ngày 24 tháng 11 năm 2025 nhóm nghiên cứu thu thập mẫu thực",
        "dự án nghiên cứu",
        "báo cáo tiến độ"
    ]
    
    for query in test_queries:
        print(f"\n🔎 Query: '{query}'")
        print("-" * 60)
        
        # Vector search
        results = engine.vector_search(query, top_k=3)
        print(f"📊 Vector Search Results ({len(results)}):")
        for i, r in enumerate(results, 1):
            print(f"   {i}. {r.metadata['file_name']}")
            print(f"      Score: {r.score:.4f}")
            print(f"      Preview: {r.text[:100]}...")
        
        # Note: Hybrid search requires keyword_results parameter
        # Skip for now as it needs TF-IDF keyword matching implementation

def test_load_saved_index():
    """Test loading saved index"""
    print("\n" + "=" * 60)
    print("📂 TESTING INDEX LOADING")
    print("=" * 60)
    
    # Check for .faiss file
    index_file = Path(str(VECTOR_INDEX_PATH) + '.faiss')
    if not index_file.exists():
        print(f"❌ No saved index found at {index_file}")
        # List files in directory
        if VECTOR_INDEX_PATH.parent.exists():
            files = list(VECTOR_INDEX_PATH.parent.glob("vector_index*"))
            if files:
                print(f"   Found files: {[f.name for f in files]}")
        return None
    
    engine = VectorSearchEngine(index_path=str(VECTOR_INDEX_PATH))
    engine.load_index()
    
    stats = engine.get_statistics()
    print(f"✅ Index loaded successfully!")
    print(f"   Vectors: {stats['num_vectors']}")
    print(f"   Dimensions: {stats['embedding_dim']}")
    
    return engine

if __name__ == "__main__":
    print("\n🚀 VECTOR SEARCH INTEGRATION TEST")
    print("=" * 60)
    
    # Option 1: Build new index
    print("\nOption 1: Build new vector index")
    engine = build_vector_index()
    
    if engine:
        # Test search
        test_search(engine)
        
        # Option 2: Load saved index
        print("\n" + "=" * 60)
        print("Option 2: Load saved index")
        loaded_engine = test_load_saved_index()
        
        if loaded_engine:
            print("\n🔍 Quick search with loaded index:")
            results = loaded_engine.vector_search("dự án", top_k=2)
            for i, r in enumerate(results, 1):
                print(f"   {i}. {r.metadata['file_name']}: {r.score:.4f}")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60)
