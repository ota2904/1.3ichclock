"""
Quick rebuild vector index from knowledge_index.json
"""
import json
import sys
import os
from pathlib import Path

# Import vector search engine
sys.path.insert(0, str(Path(__file__).parent))
from vector_search import VectorSearchEngine

def get_knowledge_data_dir():
    """Get AppData knowledge directory"""
    if os.name == 'nt':  # Windows
        appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
        data_dir = Path(appdata) / "miniZ_MCP" / "knowledge"
    else:  # Linux/Mac
        data_dir = Path.home() / ".miniz_mcp" / "knowledge"
    return data_dir

def main():
    # Load knowledge index from AppData
    knowledge_dir = get_knowledge_data_dir()
    index_file = knowledge_dir / "knowledge_index.json"
    
    print(f"📂 Looking for: {index_file}")
    
    if not index_file.exists():
        print("❌ knowledge_index.json not found in AppData!")
        print(f"   Checked: {index_file}")
        return
    
    with open(index_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    documents = data.get("documents", [])
    if not documents:
        print("❌ No documents in knowledge index!")
        return
    
    print(f"📚 Found {len(documents)} documents")
    
    # Initialize vector engine
    print("🔧 Initializing vector engine...")
    engine = VectorSearchEngine(index_path="test_vector")
    
    # Prepare documents data
    docs_data = []
    for i, doc in enumerate(documents):
        content = doc.get("content", "")
        if len(content.strip()) < 50:
            print(f"⏭️ Skipping {doc.get('file_name', 'unknown')}: too short")
            continue
        
        docs_data.append({
            "id": f"doc_{i}",
            "text": content,
            "metadata": {
                "file_name": doc.get("file_name", "unknown"),
                "file_path": doc.get("file_path", ""),
                "index": i
            }
        })
    
    print(f"📦 Building index for {len(docs_data)} documents...")
    engine.build_index(docs_data)
    
    print("💾 Saving index...")
    engine.save_index()
    
    stats = engine.get_statistics()
    print(f"✅ Done! {stats['num_vectors']} vectors, {stats['embedding_dim']} dims")
    
    # Test search
    print("\n🔍 Testing search: 'Nguyễn Công Huy'")
    results = engine.vector_search("Nguyễn Công Huy", top_k=3)
    for i, r in enumerate(results, 1):
        print(f"   {i}. {r.metadata.get('file_name', 'unknown')}: {r.score:.3f}")

if __name__ == "__main__":
    main()
