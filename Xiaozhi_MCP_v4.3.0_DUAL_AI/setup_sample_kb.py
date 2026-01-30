#!/usr/bin/env python3
"""
Setup Sample Knowledge Base for Testing
Tạo sample documents để test vector search
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
KNOWLEDGE_DATA_DIR = Path.home() / ".miniz_mcp" / "knowledge"
KNOWLEDGE_INDEX_FILE = KNOWLEDGE_DATA_DIR / "knowledge_index.json"

# Create directory
KNOWLEDGE_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Sample documents (Vietnamese content for realistic testing)
sample_documents = [
    {
        "file_path": "sample1.txt",
        "file_name": "testLLM.docx",
        "content": """Báo cáo thu thập mẫu ngày 24 tháng 11 năm 2025

Nhóm nghiên cứu đã tiến hành thu thập mẫu thực tại khu vực phía Bắc.

Kết quả thu thập:
- Số lượng mẫu: 45 mẫu
- Thời gian: 8:00 - 17:00
- Điều kiện thời tiết: Nắng, nhiệt độ 28-32°C

Mẫu được bảo quản trong tủ lạnh -20°C và sẽ được phân tích trong tuần sau.

Trưởng nhóm: Nguyễn Văn A
Thành viên: Trần Thị B, Lê Văn C
""",
        "summary": "Báo cáo thu thập 45 mẫu thực tại khu vực phía Bắc ngày 24/11/2025",
        "keywords": ["thu thập mẫu", "nghiên cứu", "24 tháng 11", "2025", "khu vực Bắc"],
        "category": "research",
        "indexed_at": datetime.now().isoformat()
    },
    {
        "file_path": "sample2.txt",
        "file_name": "project_report.docx",
        "content": """Báo cáo tiến độ dự án Q4/2024

Dự án phát triển hệ thống AI chatbot với các tính năng:
- Xử lý ngôn ngữ tự nhiên (NLP)
- Tích hợp với knowledge base
- Hỗ trợ đa ngôn ngữ (Việt, Anh)
- Vector search với FAISS

Tiến độ: 85% hoàn thành
Thời gian còn lại: 2 tuần

Các module hoàn thành:
1. PDF extraction với PyMuPDF
2. Vector search với sentence-transformers
3. Hybrid search với RRF

Còn lại: Testing và deployment
""",
        "summary": "Dự án AI chatbot đạt 85%, còn lại testing và deployment",
        "keywords": ["dự án", "AI", "chatbot", "vector search", "FAISS"],
        "category": "technical",
        "indexed_at": datetime.now().isoformat()
    },
    {
        "file_path": "sample3.txt",
        "file_name": "meeting_notes.txt",
        "content": """Biên bản họp ngày 15/12/2024

Tham dự: CEO, CTO, PM, 3 developers

Nội dung:
- Review tiến độ Q4: Đạt 80%
- Kế hoạch Q1/2025: Focus vào performance optimization
- Budget: Chấp thuận thêm 2 developers
- Timeline: Launch beta vào 31/01/2025

Action items:
1. CTO: Prepare infrastructure (deadline: 20/12)
2. PM: Update project plan
3. Dev team: Complete remaining features

Meeting kế tiếp: 22/12/2024
""",
        "summary": "Họp review Q4 (80% hoàn thành) và lên kế hoạch Q1/2025",
        "keywords": ["họp", "Q4", "Q1 2025", "launch beta", "31/01/2025"],
        "category": "meeting",
        "indexed_at": datetime.now().isoformat()
    },
    {
        "file_path": "sample4.txt",
        "file_name": "customer_feedback.txt",
        "content": """Customer Feedback - December 2024

Positive:
- UI/UX rất dễ sử dụng (rating: 4.8/5)
- Response time nhanh (< 2s)
- Hỗ trợ tiếng Việt tốt

Negative:
- Đôi khi kết quả search không chính xác
- Cần thêm tính năng export PDF
- Mobile app chưa stable

Suggestion:
- Add more templates
- Improve search relevance with vector embeddings
- Better error handling

Overall satisfaction: 4.5/5
""",
        "summary": "Feedback tích cực về UI/UX và speed, cần cải thiện search và mobile",
        "keywords": ["feedback", "customer", "UI/UX", "search", "mobile"],
        "category": "feedback",
        "indexed_at": datetime.now().isoformat()
    },
    {
        "file_path": "sample5.txt",
        "file_name": "technical_spec.md",
        "content": """Technical Specification - Vector Search Module

Architecture:
- Model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- Index: FAISS IndexFlatIP (cosine similarity)
- Embedding dimension: 384
- Hybrid search: RRF (k=60)

Performance:
- Index build time: ~0.5s per 100 documents
- Search latency: < 50ms
- Memory usage: ~1MB per 1000 vectors

API:
- build_index(texts, metadata)
- vector_search(query, top_k)
- hybrid_search(query, top_k, alpha)
- save_index(path)
- load_index(path)

Dependencies:
- sentence-transformers==5.2.0
- faiss-cpu==1.13.1
- numpy>=1.24.0
""",
        "summary": "Spec của vector search: FAISS + sentence-transformers, latency < 50ms",
        "keywords": ["technical", "vector search", "FAISS", "sentence-transformers", "API"],
        "category": "technical",
        "indexed_at": datetime.now().isoformat()
    }
]

# Save to index
index_data = {
    "documents": sample_documents,
    "total_chunks": len(sample_documents),
    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M")
}

with open(KNOWLEDGE_INDEX_FILE, 'w', encoding='utf-8') as f:
    json.dump(index_data, f, ensure_ascii=False, indent=2)

print(f"✅ Created sample knowledge base with {len(sample_documents)} documents")
print(f"   Saved to: {KNOWLEDGE_INDEX_FILE}")
print("\nDocuments:")
for i, doc in enumerate(sample_documents, 1):
    print(f"   {i}. {doc['file_name']} - {doc['category']}")
