#!/usr/bin/env python3
"""Add gemini_smart_analyze tool definition to xiaozhi_final.py"""

import re

# Read file
with open('xiaozhi_final.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the pattern: after gemini_smart_kb_filter tool definition, before RAG SYSTEM section
# Look for the line with "output_format" in gemini_smart_kb_filter and web_search

# Pattern to find: end of gemini_smart_kb_filter tool and start of RAG SYSTEM section
old_pattern = '''            "output_format": {
                "type": "string",
                "description": "Format output: 'structured' (JSON), 'raw' (text thô), 'concise' (ngắn gọn nhất)",
                "required": False
            }
        }
    },
    
    # ====================================================='''

# Find it in content
if old_pattern in content:
    print("Found pattern!")
    
    # New content to insert
    new_content = '''            "output_format": {
                "type": "string",
                "description": "Format output: 'structured' (JSON), 'raw' (text thô), 'concise' (ngắn gọn nhất)",
                "required": False
            }
        }
    },
    
    # =====================================================
    # 🔥🌐 GEMINI SMART ANALYZE - PHÂN TÍCH + GOOGLE SEARCH
    # =====================================================
    
    "gemini_smart_analyze": {
        "handler": gemini_smart_analyze,
        "description": "🔥🌐 GEMINI PHÂN TÍCH THÔNG MINH + WEB SEARCH - ⚡ BẮT BUỘC DÙNG khi user yêu cầu 'phân tích', 'analyze', 'tìm hiểu về', 'nghiên cứu', 'đánh giá'. Tool này: 1) Gemini tạo search queries tối ưu, 2) Tìm kiếm Google/Web lấy thông tin mới nhất, 3) Gemini tổng hợp và phân tích, 4) Trả kết quả cho LLM. ✅ KHÔNG CẦN gọi web_search riêng, tool này TỰ ĐỘNG search. Triggers: 'phân tích', 'analyze', 'tìm hiểu', 'nghiên cứu', 'đánh giá thị trường', 'so sánh'. VD: 'Phân tích thị trường crypto 2025', 'Tìm hiểu về AI Agent', 'Đánh giá iPhone 16'.",
        "parameters": {
            "user_query": {
                "type": "string",
                "description": "Vấn đề cần phân tích. VD: 'Phân tích xu hướng AI 2025', 'Đánh giá thị trường bất động sản'",
                "required": True
            },
            "analysis_type": {
                "type": "string",
                "description": "Loại phân tích: 'comprehensive' (đầy đủ, mặc định), 'quick' (nhanh, tóm tắt), 'deep' (sâu, đa chiều)",
                "required": False
            },
            "include_web_search": {
                "type": "boolean",
                "description": "Có tìm kiếm web không? Mặc định True. Set False nếu chỉ cần phân tích từ KB.",
                "required": False
            },
            "include_kb": {
                "type": "boolean",
                "description": "Có tìm trong Knowledge Base không? Mặc định False. Set True để kết hợp cả web + KB.",
                "required": False
            },
            "max_search_results": {
                "type": "integer",
                "description": "Số kết quả web search tối đa (default: 8). Tăng lên 15 nếu cần nhiều nguồn hơn.",
                "required": False
            }
        }
    },
    
    # ====================================================='''
    
    content = content.replace(old_pattern, new_content)
    
    # Write back
    with open('xiaozhi_final.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Successfully added gemini_smart_analyze tool definition!")
else:
    print("❌ Pattern not found. Let's try another approach...")
    
    # Try to find by line
    lines = content.split('\n')
    print(f"Total lines: {len(lines)}")
    
    # Find the line with RAG SYSTEM
    for i, line in enumerate(lines):
        if 'RAG SYSTEM' in line and 'RETRIEVAL' in line:
            print(f"Line {i+1}: {line[:80]}")
