"""
Vector Search Engine using Sentence-BERT + FAISS
Phase 2: Hybrid Search (Vector + Keyword + RRF)
Inspired by DeepSeek-OCR RAG architecture
"""

import os
import json
import pickle
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
    import faiss
except ImportError:
    print("⚠️  [Vector] Please install: pip install sentence-transformers faiss-cpu")
    raise


@dataclass
class SearchResult:
    """Search result with metadata"""
    doc_id: str
    score: float
    text: str
    metadata: Dict
    rank: int = 0


class VectorSearchEngine:
    """
    Hybrid search engine combining:
    - Vector similarity (FAISS)
    - Keyword matching (TF-IDF)
    - Reciprocal Rank Fusion (RRF)
    """
    
    def __init__(
        self, 
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        index_path: str = None
    ):
        """
        Initialize vector search engine
        
        Args:
            model_name: Sentence-BERT model (supports Vietnamese)
            index_path: Path to save/load FAISS index
        """
        print(f"🔧 [Vector] Loading model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        # FAISS index
        self.index = None
        self.doc_ids = []
        self.doc_texts = []
        self.doc_metadata = []
        
        # Index path
        if index_path:
            # If path doesn't end with .faiss, add it
            if not index_path.endswith('.faiss'):
                self.index_path = index_path + '.faiss'
            else:
                self.index_path = index_path
        else:
            self.index_path = "vector_index.faiss"
        
        # Metadata path: replace .faiss with _metadata.pkl
        self.metadata_path = self.index_path.replace(".faiss", "_metadata.pkl")
        
        print(f"✅ [Vector] Model loaded (dim={self.embedding_dim})")
    
    def build_index(self, documents: List[Dict]) -> None:
        """
        Build FAISS index from documents
        
        Args:
            documents: List of {"id": str, "text": str, "metadata": dict}
        """
        print(f"📦 [Vector] Building index for {len(documents)} documents...")
        
        # Extract texts
        texts = [doc["text"] for doc in documents]
        self.doc_ids = [doc["id"] for doc in documents]
        self.doc_texts = texts
        self.doc_metadata = [doc.get("metadata", {}) for doc in documents]
        
        # Generate embeddings
        print("🔄 [Vector] Generating embeddings...")
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            normalize_embeddings=True  # L2 normalize for cosine similarity
        )
        
        # Create FAISS index (Inner Product = Cosine similarity after normalization)
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.index.add(embeddings.astype('float32'))
        
        print(f"✅ [Vector] Index built: {self.index.ntotal} vectors")
    
    def save_index(self) -> None:
        """Save FAISS index and metadata to disk"""
        if self.index is None:
            print("⚠️  [Vector] No index to save")
            return
        
        print(f"💾 [Vector] Saving index to {self.index_path}")
        faiss.write_index(self.index, self.index_path)
        
        # Save metadata
        metadata = {
            "doc_ids": self.doc_ids,
            "doc_texts": self.doc_texts,
            "doc_metadata": self.doc_metadata
        }
        with open(self.metadata_path, "wb") as f:
            pickle.dump(metadata, f)
        
        print(f"✅ [Vector] Index saved ({self.index.ntotal} vectors)")
    
    def load_index(self, index_path: str = None) -> bool:
        """Load FAISS index and metadata from disk"""
        # Use provided path or default path
        if index_path:
            if not index_path.endswith('.faiss'):
                target_index_path = index_path + '.faiss'
            else:
                target_index_path = index_path
            target_metadata_path = target_index_path.replace(".faiss", "_metadata.pkl")
        else:
            target_index_path = self.index_path
            target_metadata_path = self.metadata_path
        
        if not os.path.exists(target_index_path):
            print(f"⚠️  [Vector] Index not found: {target_index_path}")
            return False
        
        print(f"📂 [Vector] Loading index from {target_index_path}")
        self.index = faiss.read_index(target_index_path)
        
        # Load metadata
        with open(target_metadata_path, "rb") as f:
            metadata = pickle.load(f)
        
        self.doc_ids = metadata["doc_ids"]
        self.doc_texts = metadata["doc_texts"]
        self.doc_metadata = metadata["doc_metadata"]
        
        print(f"✅ [Vector] Index loaded ({self.index.ntotal} vectors)")
        return True
    
    def vector_search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """
        Pure vector similarity search
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of SearchResult objects
        """
        if self.index is None:
            print("⚠️  [Vector] Index not built")
            return []
        
        # Encode query
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Build results
        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), 1):
            if idx < len(self.doc_ids):  # Valid index
                results.append(SearchResult(
                    doc_id=self.doc_ids[idx],
                    score=float(score),
                    text=self.doc_texts[idx][:500],  # Preview
                    metadata=self.doc_metadata[idx],
                    rank=rank
                ))
        
        return results
    
    def hybrid_search(
        self,
        query: str,
        keyword_results: List[Tuple[str, float]],
        top_k: int = 10,
        alpha: float = 0.5
    ) -> List[SearchResult]:
        """
        Hybrid search with Reciprocal Rank Fusion (RRF)
        
        Args:
            query: Search query
            keyword_results: [(doc_id, score), ...] from keyword search
            top_k: Number of results
            alpha: Weight for vector vs keyword (0=keyword only, 1=vector only)
            
        Returns:
            Fused results using RRF
        """
        # Get vector results
        vector_results = self.vector_search(query, top_k=top_k*2)
        
        # Convert keyword results to dict
        keyword_scores = {doc_id: score for doc_id, score in keyword_results}
        
        # Reciprocal Rank Fusion (RRF)
        # RRF score = sum(1 / (k + rank)) for each system
        # k = 60 is standard value from research
        k = 60
        rrf_scores = {}
        
        # Add vector scores
        for rank, result in enumerate(vector_results, 1):
            doc_id = result.doc_id
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + alpha / (k + rank)
        
        # Add keyword scores
        for rank, (doc_id, score) in enumerate(sorted(keyword_results, key=lambda x: x[1], reverse=True), 1):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1 - alpha) / (k + rank)
        
        # Sort by RRF score
        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        # Build final results
        doc_id_to_idx = {doc_id: idx for idx, doc_id in enumerate(self.doc_ids)}
        
        final_results = []
        for rank, (doc_id, rrf_score) in enumerate(sorted_results, 1):
            idx = doc_id_to_idx.get(doc_id)
            if idx is not None:
                final_results.append(SearchResult(
                    doc_id=doc_id,
                    score=rrf_score,
                    text=self.doc_texts[idx][:500],
                    metadata=self.doc_metadata[idx],
                    rank=rank
                ))
        
        return final_results
    
    def get_statistics(self) -> Dict:
        """Get index statistics"""
        if self.index is None:
            return {"status": "not_built"}
        
        return {
            "status": "ready",
            "num_vectors": self.index.ntotal,
            "embedding_dim": self.embedding_dim,
            "model": str(self.model._modules),
            "index_size_mb": os.path.getsize(self.index_path) / 1024 / 1024 if os.path.exists(self.index_path) else 0
        }


def test_vector_search():
    """Test vector search with sample data"""
    print("=" * 60)
    print("🧪 Testing Vector Search Engine")
    print("=" * 60)
    
    # Sample documents
    documents = [
        {
            "id": "doc1",
            "text": "Python là ngôn ngữ lập trình phổ biến cho AI và machine learning",
            "metadata": {"source": "tutorial.txt"}
        },
        {
            "id": "doc2",
            "text": "JavaScript được sử dụng cho phát triển web frontend",
            "metadata": {"source": "web.txt"}
        },
        {
            "id": "doc3",
            "text": "Deep learning là một nhánh của machine learning sử dụng neural networks",
            "metadata": {"source": "ai.txt"}
        },
        {
            "id": "doc4",
            "text": "React là thư viện JavaScript phổ biến cho xây dựng giao diện người dùng",
            "metadata": {"source": "frontend.txt"}
        },
        {
            "id": "doc5",
            "text": "PyTorch và TensorFlow là các framework deep learning phổ biến",
            "metadata": {"source": "frameworks.txt"}
        }
    ]
    
    # Initialize engine
    engine = VectorSearchEngine(index_path="test_vector.faiss")
    
    # Build index
    engine.build_index(documents)
    engine.save_index()
    
    # Test queries
    queries = [
        "machine learning framework",
        "phát triển web",
        "neural network"
    ]
    
    print("\n" + "=" * 60)
    print("🔍 Vector Search Results")
    print("=" * 60)
    
    for query in queries:
        print(f"\n📝 Query: '{query}'")
        results = engine.vector_search(query, top_k=3)
        
        for result in results:
            print(f"  {result.rank}. [{result.doc_id}] (score={result.score:.4f})")
            print(f"     {result.text[:100]}...")
    
    # Test hybrid search
    print("\n" + "=" * 60)
    print("🔍 Hybrid Search Results (with mock keyword scores)")
    print("=" * 60)
    
    # Mock keyword results
    keyword_results = [
        ("doc1", 0.85),
        ("doc3", 0.75),
        ("doc5", 0.65)
    ]
    
    query = "machine learning"
    print(f"\n📝 Query: '{query}'")
    results = engine.hybrid_search(query, keyword_results, top_k=3, alpha=0.5)
    
    for result in results:
        print(f"  {result.rank}. [{result.doc_id}] (RRF score={result.score:.4f})")
        print(f"     {result.text[:100]}...")
    
    # Statistics
    print("\n" + "=" * 60)
    print("📊 Index Statistics")
    print("=" * 60)
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Test completed!")


if __name__ == "__main__":
    test_vector_search()
