#!/usr/bin/env python3
"""
RAG System - Retrieval Augmented Generation
=============================================
Hệ thống RAG cục bộ cho miniZ MCP v4.3.0

Features:
1. DuckDuckGo Search - Tìm kiếm thông tin mới nhất từ Internet
2. Local Knowledge Base - Tài liệu nội bộ với TF-IDF ranking
3. Hybrid RAG - Kết hợp cả 2 nguồn thông tin
4. Smart Context Builder - Xây dựng context thông minh cho LLM
5. Crypto API - Real-time prices from CoinGecko/Binance

Copyright © 2025 miniZ Team
"""

import asyncio
import json
import os
import re
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import Counter
import math

# Crypto API
try:
    from crypto_api import get_crypto_price, get_crypto_price_binance, detect_crypto_query
    CRYPTO_API_AVAILABLE = True
except ImportError:
    CRYPTO_API_AVAILABLE = False
    print("⚠️ [CryptoAPI] Module not available")

# ============================================================
# CONFIGURATION
# ============================================================

RAG_CONFIG_FILE = Path(__file__).parent / "rag_config.json"
RAG_CACHE_FILE = Path(__file__).parent / "rag_cache.json"

DEFAULT_RAG_CONFIG = {
    "web_search": {
        "enabled": True,
        "max_results": 5,
        "cache_ttl_minutes": 30,
        "timeout_seconds": 10,
        "region": "vn-vi",  # Vietnam Vietnamese
        "safe_search": "moderate"
    },
    "knowledge_base": {
        "enabled": True,
        "folder_path": "",
        "max_results": 5,
        "chunk_size": 500,
        "chunk_overlap": 100
    },
    "hybrid": {
        "web_weight": 0.4,
        "local_weight": 0.6,
        "rerank_enabled": True
    }
}

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class SearchResult:
    """Kết quả tìm kiếm"""
    title: str
    snippet: str
    url: str = ""
    source: str = "web"  # "web" or "local"
    score: float = 0.0
    timestamp: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RAGContext:
    """Context đã được xây dựng cho LLM"""
    query: str
    web_results: List[SearchResult] = field(default_factory=list)
    local_results: List[SearchResult] = field(default_factory=list)
    combined_context: str = ""
    sources: List[str] = field(default_factory=list)
    search_time_ms: float = 0.0
    timestamp: str = ""

# ============================================================
# DUCKDUCKGO SEARCH MODULE
# ============================================================

class DuckDuckGoSearch:
    """
    DuckDuckGo Search - Tìm kiếm thông tin mới nhất từ Internet
    Sử dụng DuckDuckGo Instant Answer API và HTML scraping
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or DEFAULT_RAG_CONFIG["web_search"]
        self.cache = {}
        self.cache_ttl = self.config.get("cache_ttl_minutes", 30) * 60
        self._load_cache()
    
    def _load_cache(self):
        """Load cache từ file"""
        try:
            if RAG_CACHE_FILE.exists():
                with open(RAG_CACHE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cache = data.get("web_cache", {})
        except Exception:
            self.cache = {}
    
    def _save_cache(self):
        """Lưu cache vào file"""
        try:
            cache_data = {"web_cache": self.cache, "last_update": datetime.now().isoformat()}
            with open(RAG_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def _get_cache_key(self, query: str) -> str:
        """Tạo cache key từ query"""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Kiểm tra cache còn hợp lệ không"""
        if not cache_entry:
            return False
        cached_time = cache_entry.get("timestamp", 0)
        return (time.time() - cached_time) < self.cache_ttl
    
    async def search(self, query: str, max_results: int = None) -> List[SearchResult]:
        """
        Tìm kiếm trên DuckDuckGo
        
        Args:
            query: Từ khóa tìm kiếm
            max_results: Số kết quả tối đa
            
        Returns:
            List[SearchResult]: Danh sách kết quả
        """
        if not self.config.get("enabled", True):
            return []
        
        max_results = max_results or self.config.get("max_results", 5)
        
        # Check cache
        cache_key = self._get_cache_key(query)
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            cached = self.cache[cache_key]
            return [SearchResult(**r) for r in cached.get("results", [])]
        
        # Thực hiện tìm kiếm
        results = await self._perform_search(query, max_results)
        
        # Cache kết quả
        self.cache[cache_key] = {
            "timestamp": time.time(),
            "query": query,
            "results": [
                {
                    "title": r.title,
                    "snippet": r.snippet,
                    "url": r.url,
                    "source": r.source,
                    "score": r.score
                }
                for r in results
            ]
        }
        self._save_cache()
        
        return results
    
    async def _perform_search(self, query: str, max_results: int) -> List[SearchResult]:
        """Thực hiện tìm kiếm thực tế - Multi-provider với fallback"""
        results = []
        
        # 1. Thử Serper.dev API trước (Google Search - chính xác nhất)
        results = await self._search_with_serper(query, max_results)
        if results:
            print(f"✅ [RAG] Serper search: {len(results)} results")
            return results
        
        # 2. Thử DuckDuckGo library
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS
            
            with DDGS() as ddgs:
                search_results = list(ddgs.text(
                    query,
                    region=self.config.get("region", "vn-vi"),
                    safesearch=self.config.get("safe_search", "moderate"),
                    max_results=max_results
                ))
                
                for i, r in enumerate(search_results):
                    results.append(SearchResult(
                        title=r.get("title", ""),
                        snippet=r.get("body", ""),
                        url=r.get("href", ""),
                        source="web",
                        score=1.0 - (i * 0.1),  # Score giảm dần
                        timestamp=datetime.now().isoformat(),
                        metadata={"rank": i + 1, "provider": "duckduckgo"}
                    ))
                
                if results:
                    print(f"✅ [RAG] DuckDuckGo search: {len(results)} results")
                    return results
                    
        except ImportError:
            print("⚠️ [RAG] DuckDuckGo library not installed")
        except Exception as e:
            print(f"⚠️ [RAG] DuckDuckGo search error: {e}")
        
        # 3. Fallback to HTML scraping
        results = await self._fallback_search(query, max_results)
        if results:
            print(f"✅ [RAG] Fallback search: {len(results)} results")
        
        return results
    
    async def _search_with_serper(self, query: str, max_results: int) -> List[SearchResult]:
        """
        Tìm kiếm với Serper.dev API (Google Search)
        Miễn phí 2500 queries/tháng
        API Key: Đặt trong biến môi trường SERPER_API_KEY hoặc rag_config.json
        """
        try:
            import requests
            
            # Lấy API key từ config hoặc env
            api_key = os.environ.get("SERPER_API_KEY", "")
            if not api_key:
                # Thử đọc từ config
                try:
                    config_file = Path(__file__).parent / "rag_config.json"
                    if config_file.exists():
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                            api_key = config.get("serper_api_key", "")
                except:
                    pass
            
            if not api_key:
                return []
            
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "gl": "vn",  # Vietnam
                "hl": "vi",  # Vietnamese
                "num": max_results
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            results = []
            
            # Parse organic results
            organic = data.get("organic", [])
            for i, item in enumerate(organic[:max_results]):
                results.append(SearchResult(
                    title=item.get("title", ""),
                    snippet=item.get("snippet", ""),
                    url=item.get("link", ""),
                    source="web",
                    score=1.0 - (i * 0.1),
                    timestamp=datetime.now().isoformat(),
                    metadata={"rank": i + 1, "provider": "serper_google"}
                ))
            
            # Also check knowledge graph for quick answers
            knowledge_graph = data.get("knowledgeGraph", {})
            if knowledge_graph:
                title = knowledge_graph.get("title", "")
                description = knowledge_graph.get("description", "")
                if title and description:
                    results.insert(0, SearchResult(
                        title=f"[Knowledge] {title}",
                        snippet=description,
                        url=knowledge_graph.get("website", ""),
                        source="web",
                        score=1.0,
                        timestamp=datetime.now().isoformat(),
                        metadata={"provider": "serper_knowledge_graph"}
                    ))
            
            # Check answer box
            answer_box = data.get("answerBox", {})
            if answer_box:
                answer = answer_box.get("answer", "") or answer_box.get("snippet", "")
                if answer:
                    results.insert(0, SearchResult(
                        title="[Direct Answer]",
                        snippet=answer,
                        url=answer_box.get("link", ""),
                        source="web",
                        score=1.0,
                        timestamp=datetime.now().isoformat(),
                        metadata={"provider": "serper_answer_box"}
                    ))
            
            return results
            
        except Exception as e:
            print(f"⚠️ [RAG] Serper API error: {e}")
            return []
    
    async def _fallback_search(self, query: str, max_results: int) -> List[SearchResult]:
        """Fallback search sử dụng DuckDuckGo HTML API + Google Lite"""
        results = []
        
        # Try DuckDuckGo HTML first
        try:
            import requests
            from urllib.parse import quote_plus
            
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8"
            }
            
            timeout = self.config.get("timeout_seconds", 15)
            response = requests.get(url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                results = self._parse_ddg_html(response.text, max_results)
                if results:
                    return results
            
        except Exception as e:
            print(f"⚠️ [RAG] DuckDuckGo HTML error: {e}")
        
        # Fallback to Google Lite (mobile version - simpler HTML)
        try:
            import requests
            from urllib.parse import quote_plus
            
            url = f"https://www.google.com/search?q={quote_plus(query)}&hl=vi&gl=vn"
            headers = {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                "Accept-Language": "vi-VN,vi;q=0.9"
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Parse Google results (simpler)
                html = response.text
                
                # Tìm các div chứa kết quả
                pattern = r'<div class="[^"]*">([^<]{50,500})</div>'
                snippets = re.findall(pattern, html)
                
                # Lọc các snippet có ý nghĩa
                for i, snippet in enumerate(snippets[:max_results]):
                    # Clean HTML
                    clean = re.sub(r'<[^>]+>', '', snippet).strip()
                    if len(clean) > 30 and query.lower().split()[0] in clean.lower():
                        results.append(SearchResult(
                            title=f"Kết quả {i+1}",
                            snippet=clean[:300],
                            url="",
                            source="web",
                            score=1.0 - (i * 0.1),
                            timestamp=datetime.now().isoformat(),
                            metadata={"provider": "google_lite", "rank": i + 1}
                        ))
                        
        except Exception as e:
            print(f"⚠️ [RAG] Google Lite error: {e}")
        
        return results
    
    def _parse_ddg_html(self, html: str, max_results: int) -> List[SearchResult]:
        """Parse kết quả từ DuckDuckGo HTML"""
        results = []
        
        # Simple regex parsing
        # Pattern cho title và link
        title_pattern = r'class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
        snippet_pattern = r'class="result__snippet"[^>]*>([^<]*)</span>'
        
        titles = re.findall(title_pattern, html)
        snippets = re.findall(snippet_pattern, html)
        
        for i, (url, title) in enumerate(titles[:max_results]):
            snippet = snippets[i] if i < len(snippets) else ""
            
            # Clean up
            title = re.sub(r'<[^>]+>', '', title).strip()
            snippet = re.sub(r'<[^>]+>', '', snippet).strip()
            
            if title:
                results.append(SearchResult(
                    title=title,
                    snippet=snippet,
                    url=url,
                    source="web",
                    score=1.0 - (i * 0.1),
                    timestamp=datetime.now().isoformat(),
                    metadata={"rank": i + 1}
                ))
        
        return results

# ============================================================
# LOCAL KNOWLEDGE BASE MODULE (Enhanced)
# ============================================================

class LocalKnowledgeBase:
    """
    Knowledge Base nội bộ với TF-IDF ranking
    Hỗ trợ: TXT, PDF, DOCX, MD, JSON
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or DEFAULT_RAG_CONFIG["knowledge_base"]
        self.index = {}
        self.documents = {}
        self.idf_cache = {}
        self._load_index()
    
    def _load_index(self):
        """Load index từ file"""
        try:
            index_file = Path(__file__).parent / "knowledge_index.json"
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.index = data.get("index", {})
                    self.documents = data.get("documents", {})
        except Exception:
            pass
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize văn bản thành từ"""
        # Lowercase và loại bỏ ký tự đặc biệt
        text = text.lower()
        # Giữ lại tiếng Việt và tiếng Anh
        words = re.findall(r'[a-zA-ZÀ-ỹ]+', text)
        # Loại bỏ stopwords cơ bản
        stopwords = {'và', 'của', 'là', 'có', 'trong', 'cho', 'được', 'với', 'này', 'đó',
                     'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                     'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
                     'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as'}
        return [w for w in words if len(w) > 1 and w not in stopwords]
    
    def _calculate_tf(self, term: str, document: List[str]) -> float:
        """Tính Term Frequency"""
        if not document:
            return 0.0
        return document.count(term) / len(document)
    
    def _calculate_idf(self, term: str) -> float:
        """Tính Inverse Document Frequency"""
        if term in self.idf_cache:
            return self.idf_cache[term]
        
        total_docs = len(self.documents)
        if total_docs == 0:
            return 0.0
        
        docs_with_term = sum(1 for doc_id, doc in self.documents.items()
                           if term in self._tokenize(doc.get("content", "")))
        
        idf = math.log((total_docs + 1) / (docs_with_term + 1)) + 1
        self.idf_cache[term] = idf
        return idf
    
    def _calculate_tfidf_score(self, query: str, document: str) -> float:
        """Tính TF-IDF score cho document với query"""
        query_terms = self._tokenize(query)
        doc_terms = self._tokenize(document)
        
        if not query_terms or not doc_terms:
            return 0.0
        
        score = 0.0
        for term in query_terms:
            tf = self._calculate_tf(term, doc_terms)
            idf = self._calculate_idf(term)
            score += tf * idf
        
        return score
    
    def _extract_relevant_chunks(self, content: str, query: str, 
                                  chunk_size: int = 500, 
                                  chunk_overlap: int = 100) -> List[Tuple[str, float]]:
        """
        Trích xuất các đoạn văn liên quan nhất
        Sử dụng sliding window approach
        """
        if not content or not query:
            return []
        
        words = content.split()
        if len(words) <= chunk_size:
            score = self._calculate_tfidf_score(query, content)
            return [(content, score)]
        
        chunks = []
        step = chunk_size - chunk_overlap
        
        for i in range(0, len(words) - chunk_size + 1, step):
            chunk = ' '.join(words[i:i + chunk_size])
            score = self._calculate_tfidf_score(query, chunk)
            chunks.append((chunk, score))
        
        # Sắp xếp theo score giảm dần
        chunks.sort(key=lambda x: x[1], reverse=True)
        return chunks
    
    async def search(self, query: str, max_results: int = None) -> List[SearchResult]:
        """
        Tìm kiếm trong Knowledge Base
        
        Args:
            query: Từ khóa tìm kiếm
            max_results: Số kết quả tối đa
            
        Returns:
            List[SearchResult]: Danh sách kết quả
        """
        if not self.config.get("enabled", True):
            return []
        
        max_results = max_results or self.config.get("max_results", 5)
        chunk_size = self.config.get("chunk_size", 500)
        chunk_overlap = self.config.get("chunk_overlap", 100)
        
        results = []
        
        for doc_id, doc in self.documents.items():
            content = doc.get("content", "")
            title = doc.get("title", doc.get("filename", "Unknown"))
            file_path = doc.get("path", "")
            
            # Trích xuất chunks liên quan
            chunks = self._extract_relevant_chunks(content, query, chunk_size, chunk_overlap)
            
            if chunks:
                best_chunk, score = chunks[0]
                
                if score > 0:
                    results.append(SearchResult(
                        title=title,
                        snippet=best_chunk[:500] + "..." if len(best_chunk) > 500 else best_chunk,
                        url=f"file://{file_path}",
                        source="local",
                        score=score,
                        timestamp=datetime.now().isoformat(),
                        metadata={
                            "doc_id": doc_id,
                            "file_path": file_path,
                            "total_chunks": len(chunks)
                        }
                    ))
        
        # Sắp xếp theo score
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:max_results]
    
    async def get_full_context(self, query: str, max_chars: int = 10000) -> str:
        """
        Lấy context đầy đủ từ các documents liên quan
        
        Args:
            query: Câu hỏi
            max_chars: Số ký tự tối đa
            
        Returns:
            str: Context đầy đủ
        """
        results = await self.search(query, max_results=3)
        
        if not results:
            return ""
        
        context_parts = []
        current_chars = 0
        
        for result in results:
            if current_chars >= max_chars:
                break
            
            doc_id = result.metadata.get("doc_id", "")
            if doc_id and doc_id in self.documents:
                doc = self.documents[doc_id]
                content = doc.get("content", "")
                
                # Lấy nội dung phù hợp
                remaining = max_chars - current_chars
                if len(content) > remaining:
                    content = content[:remaining] + "..."
                
                context_parts.append(f"📄 **{result.title}**\n{content}")
                current_chars += len(content)
        
        return "\n\n---\n\n".join(context_parts)

# ============================================================
# HYBRID RAG ENGINE
# ============================================================

class HybridRAGEngine:
    """
    Hybrid RAG Engine - Kết hợp Web Search và Local Knowledge Base
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or DEFAULT_RAG_CONFIG
        self.web_search = DuckDuckGoSearch(self.config.get("web_search"))
        self.knowledge_base = LocalKnowledgeBase(self.config.get("knowledge_base"))
        self._load_config()
    
    def _load_config(self):
        """Load config từ file"""
        try:
            if RAG_CONFIG_FILE.exists():
                with open(RAG_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
        except Exception:
            pass
    
    def _save_config(self):
        """Lưu config vào file"""
        try:
            with open(RAG_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    async def search(self, query: str, 
                     sources: List[str] = None,
                     max_results: int = 10) -> RAGContext:
        """
        Tìm kiếm hybrid từ cả web và local
        
        Args:
            query: Câu hỏi/từ khóa
            sources: ["web", "local"] hoặc None cho cả hai
            max_results: Số kết quả tổng cộng
            
        Returns:
            RAGContext: Context đã được xây dựng
        """
        start_time = time.time()
        sources = sources or ["web", "local"]
        
        web_results = []
        local_results = []
        
        # Tìm kiếm song song
        tasks = []
        if "web" in sources:
            tasks.append(("web", self.web_search.search(query, max_results // 2 + 1)))
        if "local" in sources:
            tasks.append(("local", self.knowledge_base.search(query, max_results // 2 + 1)))
        
        # Chạy đồng thời
        for source_name, task in tasks:
            try:
                results = await task
                if source_name == "web":
                    web_results = results
                else:
                    local_results = results
            except Exception as e:
                print(f"⚠️ [RAG] {source_name} search error: {e}")
        
        # Kết hợp và xếp hạng
        combined_results = self._rerank_results(web_results, local_results, query)
        
        # Xây dựng context
        context = self._build_context(query, combined_results[:max_results])
        
        search_time = (time.time() - start_time) * 1000
        
        return RAGContext(
            query=query,
            web_results=web_results,
            local_results=local_results,
            combined_context=context,
            sources=[r.url for r in combined_results[:max_results] if r.url],
            search_time_ms=search_time,
            timestamp=datetime.now().isoformat()
        )
    
    def _rerank_results(self, web_results: List[SearchResult], 
                        local_results: List[SearchResult],
                        query: str) -> List[SearchResult]:
        """
        Xếp hạng lại kết quả với weighted scoring
        """
        hybrid_config = self.config.get("hybrid", {})
        web_weight = hybrid_config.get("web_weight", 0.4)
        local_weight = hybrid_config.get("local_weight", 0.6)
        
        all_results = []
        
        # Normalize và apply weights
        for r in web_results:
            r.score = r.score * web_weight
            all_results.append(r)
        
        for r in local_results:
            r.score = r.score * local_weight
            all_results.append(r)
        
        # Sắp xếp theo score
        all_results.sort(key=lambda x: x.score, reverse=True)
        
        return all_results
    
    def _build_context(self, query: str, results: List[SearchResult]) -> str:
        """
        Xây dựng context string cho LLM
        """
        if not results:
            return ""
        
        context_parts = [
            f"📊 **Thông tin tra cứu cho: \"{query}\"**",
            f"🕐 Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        web_section = []
        local_section = []
        
        for r in results:
            entry = f"### {r.title}\n{r.snippet}"
            if r.url and not r.url.startswith("file://"):
                entry += f"\n🔗 {r.url}"
            
            if r.source == "web":
                web_section.append(entry)
            else:
                local_section.append(entry)
        
        if web_section:
            context_parts.append("## 🌐 Từ Internet (DuckDuckGo)")
            context_parts.extend(web_section)
            context_parts.append("")
        
        if local_section:
            context_parts.append("## 📚 Từ Tài liệu nội bộ")
            context_parts.extend(local_section)
        
        return "\n\n".join(context_parts)
    
    async def get_answer_context(self, query: str, 
                                  prefer_source: str = "auto") -> str:
        """
        Lấy context tối ưu để trả lời câu hỏi
        
        Args:
            query: Câu hỏi
            prefer_source: "web", "local", hoặc "auto"
            
        Returns:
            str: Context sẵn sàng cho LLM
        """
        # Phân tích query để chọn source phù hợp
        if prefer_source == "auto":
            prefer_source = self._detect_best_source(query)
        
        if prefer_source == "local":
            # Ưu tiên local, fallback web
            local_context = await self.knowledge_base.get_full_context(query)
            if local_context:
                return f"📚 **Thông tin từ tài liệu nội bộ:**\n\n{local_context}"
            # Fallback to web
            prefer_source = "web"
        
        if prefer_source == "web":
            rag_context = await self.search(query, sources=["web"], max_results=5)
            if rag_context.combined_context:
                return rag_context.combined_context
        
        # Hybrid search
        rag_context = await self.search(query, max_results=8)
        return rag_context.combined_context
    
    def _detect_best_source(self, query: str) -> str:
        """
        Phát hiện source phù hợp nhất cho query
        """
        query_lower = query.lower()
        
        # Keywords gợi ý local
        local_keywords = [
            'tài liệu', 'file', 'document', 'hợp đồng', 'báo cáo',
            'ghi chú', 'notes', 'dự án', 'project', 'nội bộ',
            'của tôi', 'my', 'our', 'công ty', 'company'
        ]
        
        # Keywords gợi ý web
        web_keywords = [
            'tin tức', 'news', 'mới nhất', 'latest', 'hôm nay', 'today',
            'giá', 'price', 'thời tiết', 'weather', 'tỷ giá', 'exchange',
            'wiki', 'wikipedia', 'google', 'search', 'tra cứu online'
        ]
        
        local_score = sum(1 for kw in local_keywords if kw in query_lower)
        web_score = sum(1 for kw in web_keywords if kw in query_lower)
        
        if local_score > web_score:
            return "local"
        elif web_score > local_score:
            return "web"
        else:
            return "hybrid"

# ============================================================
# RAG TOOLS FOR MCP
# ============================================================

# Global RAG Engine instance
_rag_engine: Optional[HybridRAGEngine] = None

def get_rag_engine() -> HybridRAGEngine:
    """Get or create RAG engine instance"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = HybridRAGEngine()
    return _rag_engine

async def web_search(query: str, max_results: int = 5) -> dict:
    """
    🌐 Tìm kiếm trên Internet (DuckDuckGo)
    
    Args:
        query: Từ khóa tìm kiếm
        max_results: Số kết quả tối đa (mặc định 5)
        
    Returns:
        dict: Kết quả tìm kiếm
    """
    try:
        engine = get_rag_engine()
        results = await engine.web_search.search(query, max_results)
        
        if not results:
            return {
                "success": False,
                "message": "Không tìm thấy kết quả",
                "query": query,
                "results": []
            }
        
        # Thêm thông tin ngày hiện tại để LLM dễ so sánh thời gian
        now = datetime.now()
        
        return {
            "success": True,
            "query": query,
            "count": len(results),
            "results": [
                {
                    "title": r.title,
                    "snippet": r.snippet,
                    "url": r.url,
                    "score": r.score
                }
                for r in results
            ],
            "timestamp": now.isoformat(),
            "current_date": now.strftime("%d/%m/%Y"),
            "analysis_hint": f"⚠️ Hôm nay là {now.strftime('%d tháng %m năm %Y')}. Khi phân tích kết quả, nếu bài viết nói 'dự kiến' hoặc 'sắp ra mắt' vào một ngày ĐÃ QUA, nghĩa là sự kiện đó ĐÃ XẢY RA rồi!"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }

async def rag_search(query: str, 
                     sources: str = "auto",
                     max_results: int = 8) -> dict:
    """
    🔍 RAG Search - Tìm kiếm hybrid từ Internet + Tài liệu nội bộ
    
    Args:
        query: Câu hỏi hoặc từ khóa
        sources: "web", "local", "auto", hoặc "hybrid" (mặc định: auto)
        max_results: Số kết quả tối đa
        
    Returns:
        dict: Context và kết quả tìm kiếm
    """
    try:
        engine = get_rag_engine()
        
        # Xác định sources
        if sources == "auto":
            source_list = None  # Engine sẽ tự detect
        elif sources == "web":
            source_list = ["web"]
        elif sources == "local":
            source_list = ["local"]
        else:
            source_list = ["web", "local"]
        
        rag_context = await engine.search(query, source_list, max_results)
        
        return {
            "success": True,
            "query": query,
            "context": rag_context.combined_context,
            "web_count": len(rag_context.web_results),
            "local_count": len(rag_context.local_results),
            "sources": rag_context.sources,
            "search_time_ms": round(rag_context.search_time_ms, 2),
            "timestamp": rag_context.timestamp
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }

async def get_realtime_info(query: str) -> dict:
    """
    ⚡ Lấy thông tin THỜI GIAN THỰC từ Internet
    
    Tự động tra cứu DuckDuckGo để lấy thông tin mới nhất
    trước khi trả lời. Dùng cho: tin tức, giá cả, thời tiết,
    tỷ giá, sự kiện hiện tại, v.v.
    
    🆕 CRYPTO PRICES: Tự động dùng API chuyên dụng cho giá crypto
    
    Args:
        query: Câu hỏi cần thông tin thời gian thực
        
    Returns:
        dict: Thông tin đã tra cứu
    """
    try:
        # 🆕 CHECK IF CRYPTO QUERY - Use dedicated API
        if CRYPTO_API_AVAILABLE:
            crypto_symbol = await detect_crypto_query(query)
            if crypto_symbol:
                print(f"💰 [CryptoAPI] Detected crypto query: {crypto_symbol}")
                
                # Try CoinGecko first
                crypto_data = await get_crypto_price(crypto_symbol)
                
                # Fallback to Binance
                if not crypto_data and crypto_symbol == "bitcoin":
                    crypto_data = await get_crypto_price_binance("BTCUSDT")
                
                if crypto_data:
                    # Format context with accurate data
                    crypto_context = f"""📊 **Thông tin {crypto_data.get('name', crypto_symbol.upper())} (Realtime từ {crypto_data['source']})**

💵 **Giá hiện tại**: ${crypto_data['price_usd']:,.2f} USD
📈 **Thay đổi 24h**: {crypto_data['price_change_24h']:+.2f}%
💎 **Giá cao nhất (ATH)**: ${crypto_data.get('ath', 0):,.2f} USD"""
                    
                    if 'ath_date' in crypto_data:
                        crypto_context += f" (đạt vào {crypto_data['ath_date']})"
                    
                    if 'market_cap' in crypto_data:
                        crypto_context += f"\n📊 **Vốn hóa thị trường**: ${crypto_data['market_cap']:,.0f} USD"
                    
                    crypto_context += f"\n🕐 **Cập nhật**: {crypto_data['timestamp']}"
                    
                    return {
                        "success": True,
                        "query": query,
                        "realtime_context": crypto_context,
                        "sources": [crypto_data['source']],
                        "search_time_ms": 0,
                        "current_date": datetime.now().strftime("%d/%m/%Y"),
                        "data_type": "crypto_api",
                        "note": f"✅ Dữ liệu CHÍNH XÁC 100% từ {crypto_data['source']} API"
                    }
        
        # Default: Web search
        engine = get_rag_engine()
        
        # Luôn ưu tiên web cho realtime info
        rag_context = await engine.search(query, sources=["web"], max_results=5)
        
        if not rag_context.web_results:
            return {
                "success": False,
                "message": "Không thể tra cứu thông tin. Kiểm tra kết nối mạng.",
                "query": query
            }
        
        # Thêm thông tin ngày hiện tại để LLM dễ so sánh thời gian
        now = datetime.now()
        
        return {
            "success": True,
            "query": query,
            "realtime_context": rag_context.combined_context,
            "sources": rag_context.sources,
            "search_time_ms": round(rag_context.search_time_ms, 2),
            "current_date": now.strftime("%d/%m/%Y"),
            "analysis_hint": f"⚠️ NGÀY HIỆN TẠI: {now.strftime('%d tháng %m năm %Y')}. Khi có bài viết nói 'dự kiến ra mắt tháng X' mà tháng X ĐÃ QUA → sự kiện ĐÃ XẢY RA. Hãy dùng thì quá khứ hoặc hiện tại, KHÔNG nói 'dự kiến' cho sự kiện đã qua!",
            "note": "⚡ Thông tin được tra cứu từ Internet ngay lập tức"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }

async def smart_answer(query: str) -> dict:
    """
    🧠 Smart Answer - Tự động chọn nguồn phù hợp nhất
    
    AI sẽ phân tích câu hỏi và quyết định:
    - Dùng Knowledge Base nội bộ
    - Tra cứu Internet
    - Hoặc kết hợp cả hai
    
    Args:
        query: Câu hỏi của user
        
    Returns:
        dict: Context tối ưu cho câu trả lời
    """
    try:
        engine = get_rag_engine()
        
        # Detect best source
        best_source = engine._detect_best_source(query)
        
        # Get context
        context = await engine.get_answer_context(query, best_source)
        
        return {
            "success": True,
            "query": query,
            "detected_source": best_source,
            "context": context,
            "instruction": "Sử dụng context trên để trả lời câu hỏi. Nếu context không đủ, hãy trả lời dựa trên kiến thức của bạn và ghi chú rõ.",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }

# ============================================================
# RAG TOOL DEFINITIONS FOR MCP
# ============================================================

RAG_TOOLS = {
    "web_search": {
        "handler": web_search,
        "description": "🌐 TÌM KIẾM INTERNET (DuckDuckGo) - Tra cứu thông tin mới nhất từ web. Dùng khi cần: tin tức, giá cả, thời tiết, sự kiện hiện tại, thông tin về người/công ty/sản phẩm. VD: 'giá vàng hôm nay', 'tin tức công nghệ', 'thời tiết Hà Nội'.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Từ khóa tìm kiếm"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Số kết quả tối đa (mặc định 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    "rag_search": {
        "handler": rag_search,
        "description": "🔍 RAG SEARCH HYBRID - Tìm kiếm kết hợp từ Internet + Tài liệu nội bộ. Tự động chọn nguồn phù hợp nhất. Dùng sources='web' cho Internet only, 'local' cho tài liệu nội bộ only, 'hybrid' cho cả hai.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Câu hỏi hoặc từ khóa tìm kiếm"
                },
                "sources": {
                    "type": "string",
                    "description": "Nguồn: 'auto', 'web', 'local', 'hybrid'",
                    "default": "auto"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Số kết quả tối đa",
                    "default": 8
                }
            },
            "required": ["query"]
        }
    },
    "get_realtime_info": {
        "handler": get_realtime_info,
        "description": "⚡ THÔNG TIN THỜI GIAN THỰC - Tra cứu Internet NGAY LẬP TỨC trước khi trả lời. ⚠️ BẮT BUỘC dùng khi user hỏi về: tin tức, giá cả, tỷ giá, thời tiết, sự kiện đang diễn ra, thông tin cập nhật. Không dùng kiến thức cũ, LUÔN tra cứu mới!",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Câu hỏi cần thông tin thời gian thực"
                }
            },
            "required": ["query"]
        }
    },
    "smart_answer": {
        "handler": smart_answer,
        "description": "🧠 SMART ANSWER - AI tự động phân tích và chọn nguồn tốt nhất (Internet/Tài liệu nội bộ/Hybrid) để trả lời. Dùng khi không chắc chắn nguồn nào phù hợp. Tool này sẽ trả về context đã tối ưu.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Câu hỏi của user"
                }
            },
            "required": ["query"]
        }
    }
}

# ============================================================
# MAIN / TEST
# ============================================================

if __name__ == "__main__":
    async def test():
        print("🧪 Testing RAG System...")
        
        # Test web search
        print("\n1. Testing Web Search...")
        result = await web_search("tin tức công nghệ hôm nay")
        print(f"   Results: {result.get('count', 0)} items")
        
        # Test RAG search
        print("\n2. Testing RAG Search...")
        result = await rag_search("dự án phần mềm", sources="hybrid")
        print(f"   Web: {result.get('web_count', 0)}, Local: {result.get('local_count', 0)}")
        
        # Test realtime info
        print("\n3. Testing Realtime Info...")
        result = await get_realtime_info("giá vàng hôm nay")
        print(f"   Success: {result.get('success', False)}")
        
        print("\n✅ RAG System test completed!")
    
    asyncio.run(test())
