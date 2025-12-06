#!/usr/bin/env python3
"""
miniZ MCP v4.3.0 - Professional Edition with License Management
Web UI + WebSocket MCP + 30 Tools + Hardware License Protection
Copyright © 2025 miniZ Team
"""

import asyncio
import json
import subprocess
import psutil
import time
import os
import sys
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import websockets
import pyautogui

# License Management
try:
    from license_manager import get_license_manager
    from activation_window import show_activation_window
    LICENSE_SYSTEM_AVAILABLE = True
except ImportError:
    LICENSE_SYSTEM_AVAILABLE = False
    print("⚠️ [License] License system not available")

# Gemini AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ [Gemini] google-generativeai not installed. Run: pip install google-generativeai")

# OpenAI GPT-4
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ [OpenAI] openai library not installed. Run: pip install openai")

# Selenium Browser Automation
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ [Selenium] Not installed. Run: pip install selenium webdriver-manager")

# RAG System - Retrieval Augmented Generation
try:
    from rag_system import (
        web_search, rag_search, get_realtime_info, smart_answer,
        RAG_TOOLS, get_rag_engine
    )
    RAG_AVAILABLE = True
    print("✅ [RAG] RAG System loaded - DuckDuckGo + Local KB")
except ImportError as e:
    RAG_AVAILABLE = False
    print(f"⚠️ [RAG] RAG System not available: {e}")

# ============================================================
# UTILITY FUNCTIONS (từ xiaozhi-esp32-server chính thức)
# ============================================================

import re

def sanitize_tool_name(name: str) -> str:
    """
    Chuẩn hóa tên tool theo quy tắc của Xiaozhi server
    - Thay thế các ký tự đặc biệt bằng underscore
    - Chuyển về lowercase
    """
    if not name:
        return name
    # Thay thế các ký tự không phải alphanumeric hoặc underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    # Loại bỏ underscore liên tiếp
    sanitized = re.sub(r'_+', '_', sanitized)
    # Loại bỏ underscore ở đầu và cuối
    sanitized = sanitized.strip('_')
    return sanitized.lower()

# Tool retry configuration (từ repo chính thức)
MAX_TOOL_RETRIES = 3
TOOL_RETRY_INTERVAL = 2  # seconds

# ============================================================
# 🧠 INTENT DETECTION LLM - Phân tích ý định trước khi xử lý
# (Từ xiaozhi-esp32-server chính thức)
# ============================================================

class IntentDetector:
    """
    Intent Detection LLM - Phân tích câu hỏi và xác định tool cần gọi
    Tương tự intent_llm trong repo chính thức
    """
    
    # Các intent patterns
    REALTIME_PATTERNS = [
        # Giá cả
        r'giá\s*(vàng|xăng|dầu|usd|đô|euro|bitcoin|btc|eth)',
        r'(vàng|xăng|dầu|bitcoin|btc)\s*giá',
        r'tỷ\s*giá',
        r'bao\s*nhiêu\s*tiền',
        # Thời tiết
        r'thời\s*tiết',
        r'trời\s*(nắng|mưa|nóng|lạnh)',
        r'nhiệt\s*độ',
        # Người/Chức vụ
        r'(tổng\s*thống|thủ\s*tướng|chủ\s*tịch|ceo|giám\s*đốc)',
        r'ai\s*(là|đang)',
        r'(là\s*ai|là\s*gì)',
        r'hiện\s*(tại|nay|giờ)',
        # Thời gian thực
        r'(hôm\s*nay|bây\s*giờ|hiện\s*tại|mới\s*nhất)',
        r'(2024|2025|năm\s*nay)',
        r'tin\s*(tức|mới)',
        r'sự\s*kiện',
        # Sản phẩm/Công ty
        r'(iphone|samsung|apple|google|microsoft|tesla)',
    ]
    
    MUSIC_PATTERNS = [
        r'(bài\s*tiếp|next|chuyển\s*bài)',
        r'(bài\s*trước|previous|quay\s*lại)',
        r'(dừng|pause|tạm\s*dừng|stop)',
        r'(tiếp\s*tục|resume|play)',
        r'(phát\s*nhạc|mở\s*nhạc|bật\s*nhạc)',
        r'(tắt\s*nhạc|ngừng\s*nhạc)',
        r'(tăng|giảm)\s*(âm\s*lượng|volume)',
    ]
    
    KNOWLEDGE_BASE_PATTERNS = [
        r'(tài\s*liệu|document|file)',
        r'(trong\s*thư\s*viện|knowledge\s*base)',
        r'(tra\s*cứu\s*nội\s*bộ)',
    ]
    
    @classmethod
    def detect_intent(cls, text: str) -> dict:
        """
        Phân tích text và trả về intent + suggested tool
        Returns: {
            "intent": "realtime|music|knowledge|general",
            "suggested_tool": "web_search|get_realtime_info|smart_music_control|...",
            "confidence": 0.0-1.0,
            "should_force_tool": True/False
        }
        """
        text_lower = text.lower()
        
        # Check realtime patterns
        for pattern in cls.REALTIME_PATTERNS:
            if re.search(pattern, text_lower):
                # Xác định tool cụ thể
                if any(word in text_lower for word in ['giá', 'tỷ giá', 'bao nhiêu']):
                    tool = "get_realtime_info"
                elif any(word in text_lower for word in ['thời tiết', 'nhiệt độ', 'trời']):
                    tool = "get_realtime_info"
                elif any(word in text_lower for word in ['tin tức', 'sự kiện', 'mới nhất']):
                    tool = "web_search"
                elif any(word in text_lower for word in ['là ai', 'ai là', 'tổng thống', 'thủ tướng', 'ceo']):
                    tool = "web_search"
                else:
                    tool = "smart_answer"
                    
                return {
                    "intent": "realtime",
                    "suggested_tool": tool,
                    "confidence": 0.9,
                    "should_force_tool": True,
                    "reason": f"Detected realtime pattern: {pattern}"
                }
        
        # Check music patterns
        for pattern in cls.MUSIC_PATTERNS:
            if re.search(pattern, text_lower):
                return {
                    "intent": "music",
                    "suggested_tool": "smart_music_control",
                    "confidence": 0.95,
                    "should_force_tool": True,
                    "reason": f"Detected music pattern: {pattern}"
                }
        
        # Check knowledge base patterns
        for pattern in cls.KNOWLEDGE_BASE_PATTERNS:
            if re.search(pattern, text_lower):
                return {
                    "intent": "knowledge",
                    "suggested_tool": "get_knowledge_context",
                    "confidence": 0.85,
                    "should_force_tool": True,
                    "reason": f"Detected knowledge pattern: {pattern}"
                }
        
        # General intent - không cần force tool
        return {
            "intent": "general",
            "suggested_tool": None,
            "confidence": 0.5,
            "should_force_tool": False,
            "reason": "No specific pattern matched"
        }
    
    @classmethod
    async def detect_with_llm(cls, text: str, gemini_key: str = None, include_user_context: bool = True) -> dict:
        """
        Sử dụng Gemini để phân tích intent phức tạp hơn
        Chỉ gọi khi pattern matching không chắc chắn
        Có thể kèm user context để hiểu người dùng tốt hơn
        """
        # Đầu tiên thử pattern matching
        result = cls.detect_intent(text)
        
        # Nếu confidence cao, không cần LLM
        if result["confidence"] >= 0.8:
            return result
        
        # Nếu có Gemini API, dùng LLM để phân tích
        if gemini_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                
                # Lấy user context nếu được yêu cầu
                user_context = ""
                if include_user_context:
                    try:
                        user_context = f"""
[USER CONTEXT - Dùng để hiểu người dùng tốt hơn]
{get_user_profile_summary()}

[RECENT CONVERSATION]
{get_conversation_context(5)}
"""
                    except:
                        user_context = ""
                
                prompt = f'''Phân tích câu hỏi sau và xác định intent:
"{text}"
{user_context}
Trả lời JSON:
{{"intent": "realtime|music|knowledge|general", "tool": "web_search|get_realtime_info|smart_music_control|get_knowledge_context|none", "reason": "lý do ngắn"}}

Quy tắc:
- realtime: Câu hỏi về thông tin thời gian thực (giá cả, thời tiết, tin tức, người nổi tiếng hiện tại)
- music: Điều khiển nhạc
- knowledge: Tra cứu tài liệu nội bộ
- general: Câu hỏi thông thường

CHỈ TRẢ LỜI JSON, KHÔNG GIẢI THÍCH.'''

                response = model.generate_content(prompt)
                response_text = response.text.strip()
                
                # Parse JSON từ response
                import json
                # Tìm JSON trong response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    llm_result = json.loads(json_match.group())
                    return {
                        "intent": llm_result.get("intent", "general"),
                        "suggested_tool": llm_result.get("tool") if llm_result.get("tool") != "none" else None,
                        "confidence": 0.85,
                        "should_force_tool": llm_result.get("intent") in ["realtime", "music"],
                        "reason": llm_result.get("reason", "LLM analysis"),
                        "source": "gemini_llm"
                    }
            except Exception as e:
                print(f"⚠️ [IntentDetector] LLM error: {e}")
        
        return result

# Intent Detector instance
intent_detector = IntentDetector()

# ============================================================
# CONFIGURATION
# ============================================================

CONFIG_FILE = Path(__file__).parent / "xiaozhi_endpoints.json"
GEMINI_API_KEY = ""  # Sẽ được load từ xiaozhi_endpoints.json
OPENAI_API_KEY = ""  # Sẽ được load từ xiaozhi_endpoints.json
SERPER_API_KEY = ""  # Google Search API - Miễn phí 2500 queries/tháng

# ============================================================
# 🎵 MUSIC SYSTEM PROMPT - Hướng dẫn LLM về Music Tools
# ============================================================
MUSIC_SYSTEM_PROMPT = """
🎵 ĐIỀU KHIỂN NHẠC - QUAN TRỌNG!

⚡ QUY TẮC #1: KHI NGHE TỪ KHÓA DƯỚI ĐÂY → GỌI TOOL NGAY, KHÔNG HỎI LẠI!

┌─────────────────────────────────────────────────────────────┐
│ 📌 TỪ KHÓA → GỌI TOOL                                       │
├─────────────────────────────────────────────────────────────┤
│ "bài tiếp"/"next"/"chuyển bài" → music_next()               │
│ "bài trước"/"quay lại"        → music_previous()            │
│ "dừng"/"pause"/"tạm dừng"     → pause_music()               │
│ "tắt nhạc"/"stop"             → stop_music()                │
│ "tiếp tục"/"resume"           → resume_music()              │
│ "phát bài [tên]"              → play_music(filename="tên")  │
└─────────────────────────────────────────────────────────────┘

⚠️ VOICE VARIANTS (ESP32 recognition sai):
• "bai tiep", "tiep theo", "nex", "ních" → music_next()
• "bai truoc", "quay lai", "pre"        → music_previous()
• "dung", "pao", "poz", "tam dung"       → pause_music()
• "tat nhac", "stóp", "dung han"         → stop_music()

🔥 NGUYÊN TẮC: GỌI TOOL TRỰC TIẾP, KHÔNG CẦN HỎI!
• User: "bài tiếp" → Bạn GỌI music_next() → Trả lời "Đã chuyển bài"
• User: "dừng"     → Bạn GỌI pause_music() → Trả lời "Đã tạm dừng"
• User: "quay lại" → Bạn GỌI music_previous() → Trả lời "Đã quay lại"

📍 Server: Python-VLC Player (tích hợp sẵn)
📁 Thư mục nhạc: F:\\nhac

🎬 YOUTUBE: CHỈ khi user nói "youtube"/"video" → youtube_* tools
═══════════════════════════════════════════════════════════════
🔧 FUZZY MATCHING - HỖ TRỢ VOICE RECOGNITION
═══════════════════════════════════════════════════════════════

Hệ thống có fuzzy matching cho các biến thể:
• "bai tiep" → "bài tiếp" 
• "bai truoc" → "bài trước"
• "phat nhac" → "phát nhạc"
• "nếch" → "next"
• "prê" → "previous"

→ Cứ gửi nguyên văn lệnh, hệ thống sẽ tự nhận dạng!

═══════════════════════════════════════════════════════════════
📚 KNOWLEDGE BASE - TÀI LIỆU CỦA USER
═══════════════════════════════════════════════════════════════

⚡ QUAN TRỌNG: Khi user HỎI về DỮ LIỆU/TÀI LIỆU RIÊNG của họ:
1. GỌI get_knowledge_context(query="keywords từ câu hỏi")
2. NHẬN context với nội dung từ tài liệu
3. TRẢ LỜI dựa trên context đó

🔍 Triggers nhận biết:
• "tìm trong tài liệu", "tra cứu dữ liệu"
• "theo file của tôi", "trong documents"
• "thông tin về [X]", "[X] là gì" (nếu [X] có thể trong tài liệu)
• "dự án ABC như thế nào", "hợp đồng nói gì"

📖 Example Flow:
User: "Dự án ABC có bao nhiêu giai đoạn?"
→ Gọi: get_knowledge_context(query="dự án ABC giai đoạn")
→ Nhận: Context từ tài liệu có nội dung về dự án ABC
→ Đọc context và trả lời: "Theo tài liệu, dự án ABC có 3 giai đoạn..."

🎯 2 Tools chính:
• search_knowledge_base(query) - Tìm và show snippets (cho search)
• get_knowledge_context(query) - Lấy full context để đọc và trả lời (ƯU TIÊN)

⚠️ Nếu user hỏi về thông tin chung (không phải tài liệu riêng) → Dùng kiến thức của bạn
⚠️ Nếu user hỏi về tài liệu riêng → GỌI get_knowledge_context() TRƯỚC

═══════════════════════════════════════════════════════════════
🌐 RAG SYSTEM - RETRIEVAL AUGMENTED GENERATION
═══════════════════════════════════════════════════════════════

⛔⛔⛔ CẢNH BÁO NGHIÊM TRỌNG: BẠN KHÔNG CÓ KIẾN THỨC SAU 2024! ⛔⛔⛔

🚫 TUYỆT ĐỐI CẤM TỰ TRẢ LỜI KHI CÂU HỎI CHỨA:
• "hiện nay", "bây giờ", "hôm nay", "hiện tại"
• "2024", "2025", "năm nay"
• "mới nhất", "cập nhật", "gần đây"
• "ai là", "là ai", "là gì", "ở đâu"
• Tên người nổi tiếng: tổng thống, thủ tướng, CEO...
• Giá cả: vàng, USD, bitcoin, chứng khoán...
• Thời tiết, tin tức, sự kiện

⚠️ LÝ DO: Kiến thức của bạn ĐÃ LỖI THỜI! Ví dụ:
• Trump có thể đã trở lại làm tổng thống (bạn không biết)
• Giá vàng có thể đã thay đổi (bạn không biết)
• Có thể có CEO mới (bạn không biết)

🔴 HÀNH ĐỘNG BẮT BUỘC:
1. PHẢI GỌI web_search() hoặc get_realtime_info() TRƯỚC
2. CHỜ kết quả tra cứu
3. RỒI MỚI trả lời dựa trên thông tin mới nhất

📌 TOOLS MAPPING (PHẢI SỬ DỤNG):
┌────────────────────────────────────────────────────────────┐
│ web_search(query)       → Tìm Internet (DuckDuckGo)       │
│ get_realtime_info(query)→ Thông tin thời gian thực        │
│ rag_search(query)       → Hybrid: Web + Local KB          │
│ smart_answer(query)     → AI tự chọn nguồn tốt nhất       │
└────────────────────────────────────────────────────────────┘

📖 VÍ DỤ ĐÚNG:
User: "Tổng thống Mỹ hiện tại là ai?"
→ ❌ SAI: Trả lời "Joe Biden" (kiến thức cũ có thể sai!)
→ ✅ ĐÚNG: GỌI get_realtime_info("tổng thống Mỹ hiện tại 2024")
→ Nhận kết quả → Trả lời chính xác

User: "Giá vàng hôm nay?"
→ ❌ SAI: Đoán hoặc nói "tôi không biết"
→ ✅ ĐÚNG: GỌI get_realtime_info("giá vàng SJC hôm nay")

User: "Thời tiết Hà Nội?"
→ ✅ GỌI: get_realtime_info("thời tiết Hà Nội hôm nay")

🔥 QUY TẮC BẮT BUỘC:
1. Câu hỏi về NGƯỜI → web_search("tên người + chức vụ")
2. Câu hỏi về GIÁ CẢ → get_realtime_info()
3. Câu hỏi về THỜI TIẾT → get_realtime_info()
4. Câu hỏi về SỰ KIỆN → web_search()
5. KHÔNG CHẮC → smart_answer() (AI tự động chọn)

⚡ NHỚ: GỌI TOOL TRƯỚC, TRẢ LỜI SAU! KHÔNG BAO GIỜ TỰ ĐOÁN!
"""

DEFAULT_ENDPOINT = {
    "name": "Thiết bị 1",
    "token": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjQ1MzYxMSwiYWdlbnRJZCI6OTQ0MjE4LCJlbmRwb2ludElkIjoiYWdlbnRfOTQ0MjE4IiwicHVycG9zZSI6Im1jcC1lbmRwb2ludCIsImlhdCI6MTc2MjA4NTI1OSwiZXhwIjoxNzkzNjQyODU5fQ.GK91-17mqarpETPwz7N6rZj5DaT7bJkpK7EM6lO0Rdmfztv_KeOTBP9R4Lvy3uXKMCJn3gwucvelCur95GAn5Q",
    "enabled": True
}

def load_endpoints_from_file():
    """Đọc cấu hình endpoints từ file JSON"""
    global GEMINI_API_KEY, OPENAI_API_KEY, SERPER_API_KEY
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ [Config] Loaded {len(data.get('endpoints', []))} endpoints from {CONFIG_FILE.name}")
                
                # Load Gemini API key nếu có
                if data.get('gemini_api_key'):
                    GEMINI_API_KEY = data['gemini_api_key']
                    print(f"✅ [Gemini] API key loaded (ends with ...{GEMINI_API_KEY[-8:]})")
                
                # Load OpenAI API key nếu có
                if data.get('openai_api_key'):
                    OPENAI_API_KEY = data['openai_api_key']
                    print(f"✅ [OpenAI] API key loaded (ends with ...{OPENAI_API_KEY[-8:]})")
                
                # Load Serper API key nếu có (Google Search)
                if data.get('serper_api_key'):
                    SERPER_API_KEY = data['serper_api_key']
                    # Cũng cập nhật vào environment variable để rag_system.py có thể dùng
                    os.environ['SERPER_API_KEY'] = SERPER_API_KEY
                    print(f"✅ [Serper] Google Search API key loaded (ends with ...{SERPER_API_KEY[-8:]})")
                
                return data.get('endpoints', []), data.get('active_index', 0)
        except Exception as e:
            print(f"⚠️ [Config] Error loading {CONFIG_FILE.name}: {e}")
    
    # Trả về cấu hình mặc định nếu không có file
    return [
        DEFAULT_ENDPOINT,
        {"name": "Thiết bị 2", "token": "", "enabled": False},
        {"name": "Thiết bị 3", "token": "", "enabled": False}
    ], 0

def save_endpoints_to_file(endpoints, active_index):
    """Lưu cấu hình endpoints vào file JSON - chỉ khi có thay đổi"""
    global GEMINI_API_KEY, OPENAI_API_KEY, SERPER_API_KEY
    
    try:
        # Kiểm tra nếu data không thay đổi thì không cần lưu
        new_data = {
            'endpoints': endpoints,
            'active_index': active_index,
            'gemini_api_key': GEMINI_API_KEY,
            'openai_api_key': OPENAI_API_KEY,
            'serper_api_key': SERPER_API_KEY,
            'last_updated': datetime.now().isoformat()
        }
        
        # Đọc dữ liệu cũ để so sánh (trừ last_updated)
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                    # So sánh endpoints và active_index
                    if (old_data.get('endpoints') == endpoints and 
                        old_data.get('active_index') == active_index):
                        # Không có thay đổi, skip save
                        return True
            except Exception:
                pass
        
        # Có thay đổi, tiến hành lưu
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        print(f"💾 [Config] Saved {len(endpoints)} endpoints to {CONFIG_FILE.name}")
        return True
    except Exception as e:
        print(f"❌ [Config] Error saving to {CONFIG_FILE.name}: {e}")
        return False

# Load cấu hình từ file
endpoints_config, loaded_active_index = load_endpoints_from_file()
active_endpoint_index = loaded_active_index
xiaozhi_connected = False
active_connections = []
xiaozhi_ws = None
should_reconnect = False  # Flag để trigger reconnect

# ============================================================
# TASK MEMORY SYSTEM - Ghi nhớ tác vụ đã thực hiện
# ============================================================
TASK_MEMORY_FILE = Path(__file__).parent / "task_memory.json"
MAX_TASK_HISTORY = 100  # Giới hạn số tác vụ lưu trữ

def load_task_memory():
    """Đọc lịch sử tác vụ từ file"""
    if TASK_MEMORY_FILE.exists():
        try:
            with open(TASK_MEMORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('tasks', [])
        except Exception as e:
            print(f"⚠️ [TaskMemory] Error loading: {e}")
    return []

def save_task_memory(tasks: list):
    """Lưu lịch sử tác vụ vào file"""
    try:
        # Giới hạn số lượng
        if len(tasks) > MAX_TASK_HISTORY:
            tasks = tasks[-MAX_TASK_HISTORY:]
        
        with open(TASK_MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'tasks': tasks,
                'last_updated': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ [TaskMemory] Error saving: {e}")
        return False

def add_task_to_memory(tool_name: str, params: dict, result: dict, user_request: str = ""):
    """Thêm tác vụ vào bộ nhớ"""
    tasks = load_task_memory()
    
    task_entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "params": params,
        "result_success": result.get("success", False),
        "result_message": result.get("message", result.get("error", "")),
        "user_request": user_request
    }
    
    tasks.append(task_entry)
    save_task_memory(tasks)
    return task_entry

def get_recent_tasks(limit: int = 10) -> list:
    """Lấy các tác vụ gần đây"""
    tasks = load_task_memory()
    return tasks[-limit:] if tasks else []

def search_task_memory(keyword: str) -> list:
    """Tìm kiếm tác vụ theo từ khóa"""
    tasks = load_task_memory()
    keyword_lower = keyword.lower()
    
    results = []
    for task in tasks:
        # Tìm trong tool name, params, user_request
        if (keyword_lower in task.get('tool', '').lower() or
            keyword_lower in str(task.get('params', {})).lower() or
            keyword_lower in task.get('user_request', '').lower() or
            keyword_lower in task.get('result_message', '').lower()):
            results.append(task)
    
    return results[-20:]  # Giới hạn 20 kết quả

def clear_task_memory() -> bool:
    """Xóa toàn bộ lịch sử tác vụ"""
    try:
        if TASK_MEMORY_FILE.exists():
            TASK_MEMORY_FILE.unlink()
        return True
    except Exception as e:
        print(f"❌ [TaskMemory] Error clearing: {e}")
        return False

# Load task memory khi khởi động
task_memory_cache = load_task_memory()
print(f"📝 [TaskMemory] Loaded {len(task_memory_cache)} previous tasks")

# ============================================================
# CONVERSATION HISTORY - Lưu lịch sử hội thoại TOÀN BỘ
# ============================================================
conversation_history = []  # List để lưu tất cả messages
conversation_sessions = {}  # Sessions theo ngày

# Thư mục lưu hội thoại
import os
from pathlib import Path as PathLib
CONVERSATION_BASE_DIR = PathLib(os.path.expanduser("~")) / "AppData" / "Local" / "miniZ_MCP" / "conversations"
CONVERSATION_BASE_DIR.mkdir(parents=True, exist_ok=True)

# File tổng hợp (backward compatible)
CONVERSATION_FILE = CONVERSATION_BASE_DIR / "conversation_history.json"

# File lưu user profile (hiểu người dùng)
USER_PROFILE_FILE = CONVERSATION_BASE_DIR / "user_profile.json"

def get_today_conversation_file():
    """Lấy file hội thoại theo ngày hôm nay"""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    return CONVERSATION_BASE_DIR / f"conversation_{today}.json"

def load_conversation_history():
    """Load lịch sử hội thoại từ file"""
    global conversation_history
    try:
        # Load file tổng hợp
        if CONVERSATION_FILE.exists():
            with open(CONVERSATION_FILE, 'r', encoding='utf-8') as f:
                conversation_history = json.load(f)
            print(f"📚 [Conversation] Loaded {len(conversation_history)} messages from history")
        
        # Load file hôm nay nếu có
        today_file = get_today_conversation_file()
        if today_file.exists():
            with open(today_file, 'r', encoding='utf-8') as f:
                today_data = json.load(f)
                # Merge với conversation history nếu cần
                today_msgs = today_data.get("messages", [])
                print(f"📅 [Conversation] Today has {len(today_msgs)} messages")
    except Exception as e:
        print(f"⚠️ Could not load conversation history: {e}")
        conversation_history = []

def save_conversation_history():
    """Lưu lịch sử hội thoại vào file (tổng hợp + theo ngày)"""
    try:
        from datetime import datetime
        
        # Lưu file tổng hợp
        with open(CONVERSATION_FILE, 'w', encoding='utf-8') as f:
            json.dump(conversation_history, f, ensure_ascii=False, indent=2)
        
        # Lưu file theo ngày
        today_file = get_today_conversation_file()
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Lọc messages của hôm nay
        today_messages = [
            msg for msg in conversation_history 
            if msg.get("timestamp", "").startswith(today)
        ]
        
        today_data = {
            "date": today,
            "total_messages": len(today_messages),
            "messages": today_messages,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(today_file, 'w', encoding='utf-8') as f:
            json.dump(today_data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"⚠️ Could not save conversation history: {e}")

def add_to_conversation(role: str, content: str, metadata: dict = None):
    """
    Thêm message vào lịch sử hội thoại
    LƯU TẤT CẢ - kể cả không liên quan đến tool
    
    role: 'user', 'assistant', 'system', 'tool'
    content: nội dung message
    metadata: thông tin bổ sung (tool_name, timestamp, source, etc.)
    """
    from datetime import datetime
    
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metadata": metadata or {}
    }
    
    # Thêm session_id nếu chưa có
    if "session_id" not in message["metadata"]:
        message["metadata"]["session_id"] = datetime.now().strftime("%Y%m%d")
    
    conversation_history.append(message)
    
    # Auto-save sau mỗi 3 messages (nhanh hơn để không mất data)
    if len(conversation_history) % 3 == 0:
        save_conversation_history()
    
    # Cập nhật user profile nếu là user message
    if role == "user" and content:
        update_user_profile_from_message(content, metadata)

def update_user_profile_from_message(content: str, metadata: dict = None):
    """Cập nhật user profile từ message để hiểu người dùng hơn"""
    try:
        from datetime import datetime
        
        profile = load_user_profile()
        
        # Đếm số lần tương tác
        profile["total_interactions"] = profile.get("total_interactions", 0) + 1
        profile["last_interaction"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Phân tích topics
        topics = profile.get("topics", {})
        content_lower = content.lower()
        
        # Detect topics từ nội dung
        topic_keywords = {
            "music": ["nhạc", "bài", "hát", "music", "song", "play", "pause", "volume"],
            "weather": ["thời tiết", "weather", "mưa", "nắng", "nhiệt độ", "temperature"],
            "news": ["tin", "news", "mới", "sự kiện", "event"],
            "finance": ["giá", "vàng", "gold", "btc", "bitcoin", "chứng khoán", "stock", "usd", "tỷ giá"],
            "system": ["âm lượng", "volume", "mở", "open", "tắt", "close", "kill"],
            "web": ["tìm", "search", "google", "web", "tra cứu"],
            "coding": ["code", "python", "javascript", "lập trình", "debug", "function"],
            "general": ["là gì", "what is", "how to", "làm sao", "tại sao", "why"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in content_lower for kw in keywords):
                topics[topic] = topics.get(topic, 0) + 1
        
        profile["topics"] = topics
        
        # Lưu các câu hỏi thường gặp (top 20)
        frequent_queries = profile.get("frequent_queries", [])
        # Chỉ lưu câu ngắn gọn
        if len(content) < 100:
            frequent_queries.append({
                "query": content[:80],
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            # Giữ 20 câu gần nhất
            profile["frequent_queries"] = frequent_queries[-20:]
        
        # Thống kê giờ hoạt động
        hour_stats = profile.get("active_hours", {})
        current_hour = datetime.now().strftime("%H")
        hour_stats[current_hour] = hour_stats.get(current_hour, 0) + 1
        profile["active_hours"] = hour_stats
        
        save_user_profile(profile)
        
    except Exception as e:
        print(f"⚠️ [UserProfile] Error updating: {e}")

def load_user_profile() -> dict:
    """Load user profile"""
    try:
        if USER_PROFILE_FILE.exists():
            with open(USER_PROFILE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_interactions": 0,
        "topics": {},
        "frequent_queries": [],
        "active_hours": {},
        "preferences": {}
    }

def save_user_profile(profile: dict):
    """Lưu user profile"""
    try:
        with open(USER_PROFILE_FILE, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ [UserProfile] Error saving: {e}")

def get_conversation_context(max_messages: int = 10) -> str:
    """
    Lấy context từ lịch sử hội thoại gần đây để hiểu người dùng
    Dùng cho LLM để có thêm context
    """
    recent = conversation_history[-max_messages:] if len(conversation_history) > max_messages else conversation_history
    
    context_lines = []
    for msg in recent:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")[:200]  # Giới hạn độ dài
        if role in ["user", "assistant"]:
            context_lines.append(f"{role.upper()}: {content}")
    
    return "\n".join(context_lines)

def get_user_profile_summary() -> str:
    """Tóm tắt profile người dùng cho LLM"""
    try:
        profile = load_user_profile()
        
        # Top topics
        topics = profile.get("topics", {})
        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
        top_topics = ", ".join([f"{t[0]}({t[1]})" for t in sorted_topics]) if sorted_topics else "chưa xác định"
        
        # Active hours
        hours = profile.get("active_hours", {})
        sorted_hours = sorted(hours.items(), key=lambda x: int(x[1]), reverse=True)[:3]
        active_hours = ", ".join([f"{h[0]}h" for h in sorted_hours]) if sorted_hours else "chưa xác định"
        
        summary = f"""
[USER PROFILE]
- Tổng số tương tác: {profile.get('total_interactions', 0)}
- Chủ đề quan tâm: {top_topics}
- Giờ hoạt động: {active_hours}
- Lần cuối: {profile.get('last_interaction', 'N/A')}
"""
        return summary.strip()
    except:
        return "[USER PROFILE] Chưa có dữ liệu"

def export_conversation_to_file(filename: str = "") -> dict:
    """Export lịch sử hội thoại ra file riêng"""
    try:
        from datetime import datetime
        import os
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_export_{timestamp}.json"
        
        documents_path = os.path.expanduser("~\\Documents")
        save_folder = os.path.join(documents_path, "miniZ_Conversations")
        os.makedirs(save_folder, exist_ok=True)
        
        file_path = os.path.join(save_folder, filename)
        
        # Export với format đẹp + user profile
        export_data = {
            "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_messages": len(conversation_history),
            "user_profile": load_user_profile(),
            "messages": conversation_history
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": f"📚 Đã export {len(conversation_history)} messages + user profile",
            "path": file_path
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def list_conversation_files() -> list:
    """Liệt kê tất cả file hội thoại đã lưu"""
    try:
        files = []
        for f in CONVERSATION_BASE_DIR.glob("conversation_*.json"):
            stat = f.stat()
            files.append({
                "filename": f.name,
                "path": str(f),
                "size_kb": round(stat.st_size / 1024, 2),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })
        return sorted(files, key=lambda x: x["modified"], reverse=True)
    except Exception as e:
        return []

# Load lịch sử khi khởi động
load_conversation_history()
print(f"📂 [Conversation] Storage: {CONVERSATION_BASE_DIR}")

# ============================================================
# CONVERSATION FORMATTING HELPERS
# ============================================================

def format_tool_request(tool_name: str, args: dict) -> str:
    """Format tool request thành câu dễ đọc"""
    if tool_name == "set_volume":
        level = args.get("level", 0)
        return f"Điều chỉnh âm lượng lên {level}%"
    elif tool_name == "get_volume":
        return "Kiểm tra âm lượng hiện tại"
    elif tool_name == "screenshot":
        return "Chụp màn hình"
    elif tool_name == "open_application":
        app = args.get("app_name", "")
        return f"Mở ứng dụng {app}"
    elif tool_name == "get_active_media_players":
        return "Kiểm tra các trình duyệt và media player đang chạy"
    elif tool_name == "list_running_processes":
        limit = args.get("limit", 10)
        return f"Liệt kê {limit} tiến trình đang chạy"
    elif tool_name == "kill_process":
        identifier = args.get("identifier", "")
        force = args.get("force", True)
        return f"{'FORCE ' if force else ''}Kill tiến trình: {identifier}"
    elif tool_name == "force_kill_app":
        app_name = args.get("app_name", "")
        return f"💀 FORCE KILL APP: {app_name}"
    # YouTube controls
    elif tool_name == "control_youtube":
        action = args.get("action", "")
        return f"🎬 YouTube: {action}"
    elif tool_name == "youtube_play_pause":
        return "⏯️ YouTube: Play/Pause"
    elif tool_name == "youtube_rewind":
        seconds = args.get("seconds", 10)
        return f"⏪ YouTube: Lùi {seconds} giây"
    elif tool_name == "youtube_forward":
        seconds = args.get("seconds", 10)
        return f"⏩ YouTube: Tua tới {seconds} giây"
    elif tool_name == "youtube_volume_up":
        return "🔊 YouTube: Tăng âm lượng"
    elif tool_name == "youtube_volume_down":
        return "🔉 YouTube: Giảm âm lượng"
    elif tool_name == "youtube_mute":
        return "🔇 YouTube: Bật/Tắt tiếng"
    elif tool_name == "youtube_fullscreen":
        return "📺 YouTube: Fullscreen"
    # VLC controls
    elif tool_name == "control_vlc":
        action = args.get("action", "")
        return f"🎵 VLC: {action}"
    elif tool_name == "vlc_play_pause":
        return "⏯️ VLC: Play/Pause"
    elif tool_name == "vlc_stop":
        return "⏹️ VLC: Dừng phát"
    elif tool_name == "vlc_next":
        return "⏭️ VLC: Bài tiếp theo"
    elif tool_name == "vlc_previous":
        return "⏮️ VLC: Bài trước"
    elif tool_name == "vlc_volume_up":
        return "🔊 VLC: Tăng âm lượng"
    elif tool_name == "vlc_volume_down":
        return "🔉 VLC: Giảm âm lượng"
    elif tool_name == "vlc_mute":
        return "🔇 VLC: Bật/Tắt tiếng"
    # WMP controls
    elif tool_name == "control_wmp":
        action = args.get("action", "")
        return f"🎶 Windows Media Player: {action}"
    elif tool_name.startswith("wmp_"):
        action = tool_name.replace("wmp_", "").replace("_", " ").title()
        return f"🎶 Windows Media Player: {action}"
    # Smart media control
    elif tool_name == "smart_media_control":
        action = args.get("action", "")
        return f"🎛️ Smart Media: {action}"
    elif tool_name == "create_file":
        path = args.get("path", "")
        return f"Tạo file mới: {path}"
    elif tool_name == "read_file":
        path = args.get("path", "")
        return f"Đọc nội dung file: {path}"
    elif tool_name == "search_web":
        query = args.get("query", "")
        return f"Tìm kiếm Google: {query}"
    elif tool_name == "ask_gemini":
        prompt = args.get("prompt", "")[:50]
        return f"Hỏi Gemini AI: {prompt}..."
    elif tool_name == "ask_gpt4":
        prompt = args.get("prompt", "")[:50]
        return f"Hỏi GPT-4: {prompt}..."
    else:
        # Default format
        if args:
            args_str = ", ".join([f"{k}={v}" for k, v in list(args.items())[:2]])
            return f"Gọi tool {tool_name} ({args_str})"
        return f"Gọi tool {tool_name}"

def format_tool_response(tool_name: str, response: dict) -> str:
    """Format tool response thành câu dễ đọc"""
    if isinstance(response, dict):
        # Kiểm tra lỗi
        if response.get("isError"):
            error_text = ""
            if "content" in response and isinstance(response["content"], list):
                for item in response["content"]:
                    if item.get("type") == "text":
                        error_text = item.get("text", "")
                        break
            return f"❌ Lỗi: {error_text}"
        
        # Success responses
        if "content" in response and isinstance(response["content"], list):
            for item in response["content"]:
                if item.get("type") == "text":
                    text = item.get("text", "")
                    # Rút gọn nếu quá dài
                    if len(text) > 150:
                        return f"✅ {text[:150]}..."
                    return f"✅ {text}"
        
        # Fallback cho response khác
        if "message" in response:
            return f"✅ {response['message']}"
        
    return "✅ Thực hiện thành công"

print("🚀 miniZ MCP - Sidebar UI")
print(f"🌐 Web: http://localhost:8000")
print(f"📡 MCP: Multi-device ready")

# ============================================================
# TOOL IMPLEMENTATIONS (20 TOOLS)
# ============================================================

async def set_volume(level: int) -> dict:
    """Điều chỉnh âm lượng hệ thống - Windows only"""
    try:
        if not 0 <= level <= 100:
            return {"success": False, "error": "Level phải từ 0-100"}
        
        # Sử dụng PowerShell trực tiếp (tương thích tốt hơn với Python 3.13)
        ps_cmd = f"""
[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
$obj = New-Object System.Windows.Forms.Form
$obj.KeyPreview = $True

# Get current volume
$wshShell = New-Object -ComObject WScript.Shell
for($i=1; $i -le 50; $i++){{$wshShell.SendKeys([char]174)}}  # Mute to 0

# Set to desired level
$steps = [Math]::Round({level} / 2)
for($i=1; $i -le $steps; $i++){{$wshShell.SendKeys([char]175)}}  # Volume up

Write-Output "Volume set to {level}%"
"""
        
        proc = await asyncio.create_subprocess_exec(
            "powershell", "-NoProfile", "-Command", ps_cmd,
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5)
        
        if proc.returncode == 0:
            return {
                "success": True, 
                "level": level,
                "message": f"✅ Âm lượng đã đặt: {level}%"
            }
        else:
            error_msg = stderr.decode('utf-8', errors='ignore').strip()
            return {"success": False, "error": f"PowerShell error: {error_msg[:200]}"}
                
    except asyncio.TimeoutError:
        return {"success": False, "error": "Timeout khi điều chỉnh âm lượng"}
    except Exception as e:
        return {"success": False, "error": f"Lỗi: {str(e)}"}

async def mute_volume() -> dict:
    """Tắt tiếng (mute) hệ thống"""
    try:
        ps_cmd = """
$obj = New-Object -ComObject WScript.Shell
$obj.SendKeys([char]173)
Write-Output "Volume muted"
"""
        proc = await asyncio.create_subprocess_exec(
            "powershell", "-NoProfile", "-Command", ps_cmd,
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE
        )
        await asyncio.wait_for(proc.communicate(), timeout=3)
        
        return {"success": True, "message": "🔇 Đã tắt tiếng"}
    except Exception as e:
        return {"success": False, "error": f"Lỗi: {str(e)}"}

async def unmute_volume() -> dict:
    """Bật lại tiếng (unmute) hệ thống"""
    try:
        ps_cmd = """
$obj = New-Object -ComObject WScript.Shell
$obj.SendKeys([char]173)
Write-Output "Volume unmuted"
"""
        proc = await asyncio.create_subprocess_exec(
            "powershell", "-NoProfile", "-Command", ps_cmd,
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE
        )
        await asyncio.wait_for(proc.communicate(), timeout=3)
        
        return {"success": True, "message": "🔊 Đã bật tiếng"}
    except Exception as e:
        return {"success": False, "error": f"Lỗi: {str(e)}"}

async def volume_up(steps: int = 5) -> dict:
    """Tăng âm lượng lên (mỗi step ~2%)"""
    try:
        ps_cmd = f"""
$obj = New-Object -ComObject WScript.Shell
for($i=1; $i -le {steps}; $i++){{$obj.SendKeys([char]175)}}
Write-Output "Volume increased by {steps} steps"
"""
        proc = await asyncio.create_subprocess_exec(
            "powershell", "-NoProfile", "-Command", ps_cmd,
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE
        )
        await asyncio.wait_for(proc.communicate(), timeout=3)
        
        return {"success": True, "message": f"🔊 Đã tăng âm lượng ({steps} bước)"}
    except Exception as e:
        return {"success": False, "error": f"Lỗi: {str(e)}"}

async def volume_down(steps: int = 5) -> dict:
    """Giảm âm lượng xuống (mỗi step ~2%)"""
    try:
        ps_cmd = f"""
$obj = New-Object -ComObject WScript.Shell
for($i=1; $i -le {steps}; $i++){{$obj.SendKeys([char]174)}}
Write-Output "Volume decreased by {steps} steps"
"""
        proc = await asyncio.create_subprocess_exec(
            "powershell", "-NoProfile", "-Command", ps_cmd,
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE
        )
        await asyncio.wait_for(proc.communicate(), timeout=3)
        
        return {"success": True, "message": f"🔉 Đã giảm âm lượng ({steps} bước)"}
    except Exception as e:
        return {"success": False, "error": f"Lỗi: {str(e)}"}

async def get_volume() -> dict:
    """Lấy mức âm lượng hiện tại của hệ thống"""
    try:
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            
            current_volume = int(volume.GetMasterVolumeLevelScalar() * 100)
            is_muted = volume.GetMute()
            
            return {
                "success": True,
                "level": current_volume,
                "muted": bool(is_muted),
                "message": f"🔊 Âm lượng hiện tại: {current_volume}%" + (" (Tắt tiếng)" if is_muted else "")
            }
        except ImportError:
            # Fallback PowerShell
            ps_cmd = """
Add-Type -TypeDefinition @'
using System.Runtime.InteropServices;
[Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IAudioEndpointVolume {
    int NotImpl1(); int NotImpl2();
    int GetMasterVolumeLevelScalar(out float level);
}
[Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
class MMDeviceEnumeratorComObject { }
[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDeviceEnumerator {
    int NotImpl1();
    int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice device);
}
[Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDevice {
    int Activate(ref System.Guid id, int clsCtx, int activationParams, out IAudioEndpointVolume aev);
}
'@
$enumerator = [System.Activator]::CreateInstance([Type]::GetTypeFromCLSID([Guid]'BCDE0395-E52F-467C-8E3D-C4579291692E'))
$device = $null
$enumerator.GetDefaultAudioEndpoint(0, 1, [ref]$device)
$aev = $null
$device.Activate([Guid]'5CDF2C82-841E-4546-9722-0CF74078229A', 0, 0, [ref]$aev)
$current = 0.0
$aev.GetMasterVolumeLevelScalar([ref]$current)
Write-Output ([int]($current * 100))
"""
            proc = await asyncio.create_subprocess_exec(
                "powershell", "-NoProfile", "-Command", ps_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=3)
            
            if proc.returncode == 0:
                level = int(stdout.decode('utf-8', errors='ignore').strip())
                return {
                    "success": True,
                    "level": level,
                    "message": f"🔊 Âm lượng hiện tại: {level}%"
                }
            else:
                return {"success": False, "error": "Không thể lấy âm lượng"}
    except Exception as e:
        return {"success": False, "error": f"Lỗi: {str(e)}"}

async def take_screenshot(filename: str = None) -> dict:
    """Chụp màn hình toàn bộ và lưu file
    
    Args:
        filename: Tên file lưu ảnh (optional). Mặc định: screenshot_YYYYMMDD_HHMMSS.png
    
    Returns:
        dict với thông tin file đã lưu
    """
    try:
        import pyautogui
        from datetime import datetime
        import os
        
        # Tạo tên file mặc định nếu không có
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        # Đảm bảo có extension .png
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filename += '.png'
        
        # Lưu vào thư mục Downloads hoặc thư mục hiện tại
        downloads_path = Path.home() / "Downloads"
        if downloads_path.exists():
            filepath = downloads_path / filename
        else:
            filepath = Path(filename)
        
        # Chụp màn hình
        print(f"📸 [Screenshot] Đang chụp màn hình...")
        screenshot = pyautogui.screenshot()
        
        # Lưu file
        screenshot.save(str(filepath))
        
        file_size = filepath.stat().st_size / 1024  # KB
        
        print(f"✅ [Screenshot] Đã lưu: {filepath}")
        
        return {
            "success": True,
            "message": f"✅ Đã chụp màn hình: {filepath.name}",
            "filepath": str(filepath),
            "filename": filepath.name,
            "size_kb": round(file_size, 2),
            "dimensions": f"{screenshot.width}x{screenshot.height}"
        }
        
    except ImportError:
        return {
            "success": False,
            "error": "Thiếu thư viện 'pyautogui'. Cài đặt: pip install pyautogui"
        }
    except Exception as e:
        print(f"❌ [Screenshot] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

async def show_notification(title: str, message: str) -> dict:
    try:
        ps_cmd = f'''[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null; $template = @"<toast><visual><binding template="ToastText02"><text id="1">{title}</text><text id="2">{message}</text></binding></visual></toast>"@; $xml = New-Object Windows.Data.Xml.Dom.XmlDocument; $xml.LoadXml($template); $toast = New-Object Windows.UI.Notifications.ToastNotification $xml; [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Xiaozhi").Show($toast)'''
        proc = await asyncio.create_subprocess_exec("powershell", "-Command", ps_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await asyncio.wait_for(proc.wait(), timeout=5)
        return {"success": True, "title": title, "message": message}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Cache cho system resources
_resource_cache = None
_resource_cache_time = 0
RESOURCE_CACHE_DURATION = 2  # Cache 2 giây

async def get_system_resources() -> dict:
    """Lấy thông tin tài nguyên hệ thống với caching"""
    global _resource_cache, _resource_cache_time
    
    try:
        # Kiểm tra cache
        now = time.time()
        if _resource_cache and (now - _resource_cache_time) < RESOURCE_CACHE_DURATION:
            return _resource_cache
        
        # Lấy dữ liệu mới - giảm interval từ 1s xuống 0.1s
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        result = {
            "success": True, 
            "data": {
                "cpu_percent": cpu, 
                "memory_percent": mem.percent, 
                "memory_used_gb": round(mem.used / (1024**3), 2), 
                "memory_total_gb": round(mem.total / (1024**3), 2), 
                "disk_percent": disk.percent, 
                "disk_used_gb": round(disk.used / (1024**3), 2), 
                "disk_total_gb": round(disk.total / (1024**3), 2)
            }
        }
        
        # Cập nhật cache
        _resource_cache = result
        _resource_cache_time = now
        
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_current_time() -> dict:
    try:
        now = datetime.now()
        return {"success": True, "datetime": now.strftime("%Y-%m-%d %H:%M:%S"), "date": now.strftime("%Y-%m-%d"), "time": now.strftime("%H:%M:%S"), "day_of_week": now.strftime("%A"), "timestamp": int(now.timestamp())}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def calculator(expression: str) -> dict:
    try:
        allowed = set("0123456789+-*/()., ")
        if not all(c in allowed for c in expression):
            return {"success": False, "error": "Ký tự không hợp lệ"}
        result = eval(expression, {"__builtins__": {}}, {})
        return {"success": True, "expression": expression, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_network_info() -> dict:
    try:
        import socket
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return {"success": True, "hostname": hostname, "ip": ip}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def search_web(query: str) -> dict:
    try:
        import webbrowser
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return {"success": True, "message": f"Đã mở tìm kiếm: {query}", "url": url}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def set_brightness(level: int) -> dict:
    try:
        import screen_brightness_control as sbc
        sbc.set_brightness(level)
        return {"success": True, "level": level, "message": f"Đã đặt độ sáng: {level}%"}
    except Exception as e:
        return {"success": False, "error": str(e), "note": "Có thể cần cài: pip install screen-brightness-control"}

async def get_clipboard() -> dict:
    try:
        import pyperclip
        content = pyperclip.paste()
        return {"success": True, "content": content}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def set_clipboard(text: str) -> dict:
    try:
        import pyperclip
        pyperclip.copy(text)
        return {"success": True, "message": f"Đã copy vào clipboard: {text[:50]}..."}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def play_sound(frequency: int = 1000, duration: int = 500) -> dict:
    try:
        import winsound
        winsound.Beep(frequency, duration)
        return {"success": True, "message": f"Đã phát âm thanh {frequency}Hz trong {duration}ms"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def open_application(app_name: str) -> dict:
    """
    Mở ứng dụng Windows với khả năng tìm kiếm thông minh.
    
    Thứ tự tìm kiếm:
    1. Dictionary mapping (ưu tiên cao nhất)
    2. Tìm trong PATH
    3. Tìm trong Registry (App Paths)
    4. Tìm trong Program Files
    5. Fallback: Windows Start Menu
    
    Args:
        app_name: Tên ứng dụng (ví dụ: "chrome", "photoshop", "word")
        
    Returns:
        dict: {"success": bool, "message": str, "path": str (optional)}
    """
    try:
        import os
        import shutil
        import winreg
        import glob
        
        # Dictionary mapping - Hỗ trợ 50+ ứng dụng phổ biến
        apps = {
            # Windows Built-in
            "notepad": "notepad.exe",
            "note": "notepad.exe",
            "máy ghi chú": "notepad.exe",
            "calc": "calc.exe",
            "calculator": "calc.exe",
            "máy tính": "calc.exe",
            "paint": "mspaint.exe",
            "vẽ": "mspaint.exe",
            "cmd": "cmd.exe",
            "command prompt": "cmd.exe",
            "powershell": "powershell.exe",
            "ps": "powershell.exe",
            "explorer": "explorer.exe",
            "file explorer": "explorer.exe",
            "taskmgr": "taskmgr.exe",
            "task manager": "taskmgr.exe",
            "quản lý tác vụ": "taskmgr.exe",
            
            # Browsers
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe",
            "gc": "chrome.exe",
            "firefox": "firefox.exe",
            "ff": "firefox.exe",
            "edge": "msedge.exe",
            "microsoft edge": "msedge.exe",
            "brave": "brave.exe",
            "opera": "opera.exe",
            
            # Microsoft Office
            "word": "WINWORD.EXE",
            "microsoft word": "WINWORD.EXE",
            "excel": "EXCEL.EXE",
            "microsoft excel": "EXCEL.EXE",
            "powerpoint": "POWERPNT.EXE",
            "microsoft powerpoint": "POWERPNT.EXE",
            "ppt": "POWERPNT.EXE",
            "outlook": "OUTLOOK.EXE",
            "microsoft outlook": "OUTLOOK.EXE",
            "onenote": "ONENOTE.EXE",
            "teams": "Teams.exe",
            "microsoft teams": "Teams.exe",
            
            # Adobe Creative Cloud
            "photoshop": "Photoshop.exe",
            "adobe photoshop": "Photoshop.exe",
            "ps": "Photoshop.exe",
            "illustrator": "Illustrator.exe",
            "adobe illustrator": "Illustrator.exe",
            "ai": "Illustrator.exe",
            "premiere": "Adobe Premiere Pro.exe",
            "premiere pro": "Adobe Premiere Pro.exe",
            "after effects": "AfterFX.exe",
            "ae": "AfterFX.exe",
            "lightroom": "Lightroom.exe",
            "acrobat": "Acrobat.exe",
            "adobe acrobat": "Acrobat.exe",
            
            # Development Tools
            "vscode": "Code.exe",
            "visual studio code": "Code.exe",
            "code": "Code.exe",
            "vs": "Code.exe",
            "sublime": "sublime_text.exe",
            "sublime text": "sublime_text.exe",
            "atom": "atom.exe",
            "notepad++": "notepad++.exe",
            "npp": "notepad++.exe",
            "pycharm": "pycharm64.exe",
            "intellij": "idea64.exe",
            "webstorm": "webstorm64.exe",
            "androidstudio": "studio64.exe",
            "android studio": "studio64.exe",
            
            # 3D & Design
            "blender": "blender.exe",
            "3ds max": "3dsmax.exe",
            "maya": "maya.exe",
            "sketchup": "SketchUp.exe",
            "fusion360": "Fusion360.exe",
            "fusion 360": "Fusion360.exe",
            "autocad": "acad.exe",
            "solidworks": "SLDWORKS.exe",
            
            # Communication
            "discord": "Discord.exe",
            "slack": "slack.exe",
            "zoom": "Zoom.exe",
            "skype": "Skype.exe",
            "telegram": "Telegram.exe",
            "zalo": "Zalo.exe",
            
            # Media Players
            "vlc": "vlc.exe",
            "spotify": "Spotify.exe",
            "itunes": "iTunes.exe",
            "windows media player": "wmplayer.exe",
            "wmp": "wmplayer.exe",
            
            # Other Popular Apps
            "steam": "steam.exe",
            "epic games": "EpicGamesLauncher.exe",
            "epic": "EpicGamesLauncher.exe",
            "obs": "obs64.exe",
            "obs studio": "obs64.exe",
            "gimp": "gimp-2.10.exe",
            "audacity": "audacity.exe",
            "7zip": "7zFM.exe",
            "7-zip": "7zFM.exe",
            "winrar": "WinRAR.exe",
        }
        
        # 1. Kiểm tra trong dictionary
        app_name_lower = app_name.lower().strip()
        exe_name = apps.get(app_name_lower)
        
        print(f"🔍 [Open App] Tìm kiếm: '{app_name}' → {exe_name or 'không có trong dictionary'}")
        
        # Nếu không có trong dictionary, thử dùng tên gốc
        if not exe_name:
            # Kiểm tra nếu đã có .exe
            if app_name.lower().endswith('.exe'):
                exe_name = app_name
            else:
                exe_name = app_name + '.exe'
        
        # 2. Tìm trong PATH
        exe_path = shutil.which(exe_name)
        if exe_path:
            print(f"✅ [Open App] Tìm thấy trong PATH: {exe_path}")
            subprocess.Popen([exe_path])
            return {"success": True, "message": f"✅ Đã mở {app_name}", "path": exe_path}
        
        # 3. Tìm trong Windows Registry (App Paths)
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{exe_name}") as key:
                exe_path = winreg.QueryValue(key, None)
                if exe_path and os.path.exists(exe_path):
                    print(f"✅ [Open App] Tìm thấy trong Registry: {exe_path}")
                    subprocess.Popen([exe_path])
                    return {"success": True, "message": f"✅ Đã mở {app_name}", "path": exe_path}
        except WindowsError:
            pass
        
        # 4. Tìm trong các thư mục phổ biến
        common_paths = [
            os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "*", exe_name),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "*", exe_name),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "*", exe_name),
            os.path.join(os.environ.get("APPDATA", ""), "*", exe_name),
        ]
        
        import glob
        for pattern in common_paths:
            matches = glob.glob(pattern, recursive=False)
            if matches:
                exe_path = matches[0]
                print(f"✅ [Open App] Tìm thấy trong: {exe_path}")
                subprocess.Popen([exe_path])
                return {"success": True, "message": f"✅ Đã mở {app_name}", "path": exe_path}
        
        # 5. Tìm kiếm sâu trong Program Files (chậm hơn, dùng làm fallback)
        if "photoshop" in app_name_lower or "adobe" in app_name_lower:
            # Adobe apps thường ở C:\Program Files\Adobe
            adobe_base = r"C:\Program Files\Adobe"
            if os.path.exists(adobe_base):
                for root, dirs, files in os.walk(adobe_base):
                    if exe_name in files:
                        exe_path = os.path.join(root, exe_name)
                        print(f"✅ [Open App] Tìm thấy Adobe app: {exe_path}")
                        subprocess.Popen([exe_path])
                        return {"success": True, "message": f"✅ Đã mở {app_name}", "path": exe_path}
        
        if "autodesk" in app_name_lower or "fusion" in app_name_lower:
            # Autodesk apps thường ở LOCALAPPDATA
            autodesk_base = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Autodesk")
            if os.path.exists(autodesk_base):
                for root, dirs, files in os.walk(autodesk_base):
                    if exe_name in files:
                        exe_path = os.path.join(root, exe_name)
                        print(f"✅ [Open App] Tìm thấy Autodesk app: {exe_path}")
                        subprocess.Popen([exe_path])
                        return {"success": True, "message": f"✅ Đã mở {app_name}", "path": exe_path}
        
        # 6. Fallback cuối cùng: Dùng Windows Start Menu
        print(f"⚠️ [Open App] Không tìm thấy đường dẫn, thử Windows Start Menu...")
        subprocess.Popen(["start", "", app_name], shell=True)
        return {
            "success": True, 
            "message": f"✅ Đã gửi lệnh mở {app_name} (Windows sẽ tìm trong Start Menu)",
            "note": "Nếu không mở được, hãy kiểm tra tên ứng dụng hoặc thêm vào dictionary"
        }
        
    except Exception as e:
        print(f"❌ [Open App] Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": f"Lỗi khi mở {app_name}: {str(e)}"}

# ==================== MEDIA PLAYER CONTROL ====================

# Helper function để tìm tất cả các cửa sổ media player và browser
def _find_all_media_windows():
    """Tìm tất cả cửa sổ media player và browser đang chạy"""
    import ctypes
    
    windows = {
        'youtube': [],      # Các tab YouTube
        'spotify_web': [],  # Spotify web
        'wmplayer': None,   # Windows Media Player
        'vlc': None,        # VLC Player
        'spotify_app': None,# Spotify Desktop
        'browsers': []      # Các browser khác
    }
    
    browser_names = ['chrome', 'firefox', 'edge', 'opera', 'brave', 'coccoc', 'cốc cốc']
    
    def enum_callback(hwnd, _):
        if ctypes.windll.user32.IsWindowVisible(hwnd):
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value
                title_lower = title.lower()
                
                # YouTube có ưu tiên cao nhất
                if 'youtube' in title_lower:
                    windows['youtube'].append({'hwnd': hwnd, 'title': title})
                # Spotify Web
                elif 'spotify' in title_lower and any(b in title_lower for b in browser_names):
                    windows['spotify_web'].append({'hwnd': hwnd, 'title': title})
                # Windows Media Player
                elif 'windows media player' in title_lower or 'wmplayer' in title_lower:
                    windows['wmplayer'] = {'hwnd': hwnd, 'title': title}
                # VLC
                elif 'vlc' in title_lower and 'media player' in title_lower:
                    windows['vlc'] = {'hwnd': hwnd, 'title': title}
                # Spotify Desktop App
                elif 'spotify' in title_lower and not any(b in title_lower for b in browser_names):
                    windows['spotify_app'] = {'hwnd': hwnd, 'title': title}
                # Các browser khác
                elif any(b in title_lower for b in browser_names):
                    windows['browsers'].append({'hwnd': hwnd, 'title': title})
        return True
    
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.POINTER(ctypes.c_int))
    ctypes.windll.user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
    
    return windows

def _focus_and_send_key(hwnd, key, delay=0.15):
    """Focus vào cửa sổ và gửi phím"""
    import ctypes
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    time.sleep(delay)
    pyautogui.press(key)

def _focus_and_send_hotkey(hwnd, *keys, delay=0.15):
    """Focus vào cửa sổ và gửi tổ hợp phím"""
    import ctypes
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    time.sleep(delay)
    pyautogui.hotkey(*keys)

async def media_play_pause() -> dict:
    """
    Phát/Tạm dừng media (Play/Pause toggle).
    ⭐ ƯU TIÊN PYTHON-VLC TRƯỚC - nhanh & không cần detect window!
    
    Ưu tiên:
    1. Python-VLC nội bộ (NHANH NHẤT)
    2. YouTube (Browser) - Focus và nhấn K
    3. Windows Media Player
    4. Spotify
    5. Fallback - Media key
    """
    try:
        # 🎵 ƯU TIÊN 1: Python-VLC nội bộ - NHANH NHẤT!
        if vlc_player and vlc_player._player:
            vlc_player.pause()
            is_playing = vlc_player.is_playing()
            status = vlc_player.get_full_status()
            current_song = status.get('current_song', 'Unknown')
            return {
                "success": True, 
                "message": f"{'▶️ Đang phát' if is_playing else '⏸️ Đã tạm dừng'}: {current_song} (Python-VLC)",
                "is_playing": is_playing,
                "player": "Python-VLC",
                "llm_note": "🎵 Đang dùng Python-VLC Player tích hợp. Có thể dùng: pause_music(), resume_music(), stop_music(), music_next(), music_previous(), seek_music(), music_volume()"
            }
        
        windows = _find_all_media_windows()
        
        # 2. YouTube - nếu có
        if windows['youtube']:
            yt = windows['youtube'][0]
            _focus_and_send_key(yt['hwnd'], 'k')
            return {"success": True, "message": f"✅ Play/Pause YouTube: {yt['title'][:50]}..."}
        
        # 3. Windows Media Player
        if windows['wmplayer']:
            _focus_and_send_key(windows['wmplayer']['hwnd'], 'space')
            return {"success": True, "message": "✅ Play/Pause (Windows Media Player)"}
        
        # 4. VLC Window (external)
        if windows['vlc']:
            _focus_and_send_key(windows['vlc']['hwnd'], 'space')
            return {"success": True, "message": "✅ Play/Pause (VLC Window)"}
        
        # 5. Spotify Desktop App
        if windows['spotify_app']:
            _focus_and_send_key(windows['spotify_app']['hwnd'], 'space')
            return {"success": True, "message": "✅ Play/Pause (Spotify Desktop)"}
        
        # 6. Spotify Web
        if windows['spotify_web']:
            sw = windows['spotify_web'][0]
            _focus_and_send_key(sw['hwnd'], 'space')
            return {"success": True, "message": f"✅ Play/Pause Spotify Web"}
        
        # 7. Fallback - dùng media key
        pyautogui.press('playpause')
        return {"success": True, "message": "✅ Đã gửi lệnh Play/Pause (Media Key)"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def media_next_track() -> dict:
    """
    Chuyển bài tiếp theo (Next Track).
    ⭐ ƯU TIÊN PYTHON-VLC TRƯỚC - nhanh & không cần detect window!
    """
    try:
        # 🎵 ƯU TIÊN 1: Python-VLC nội bộ - NHANH NHẤT!
        if vlc_player and vlc_player._player:
            success = vlc_player.next_track()
            if success:
                import time
                time.sleep(0.3)  # Đợi VLC chuyển bài
                status = vlc_player.get_full_status()
                current_song = status.get('current_song', 'Unknown')
                return {
                    "success": True, 
                    "message": f"⏭️ Đã chuyển: {current_song} (Python-VLC)",
                    "player": "Python-VLC",
                    "current_song": current_song,
                    "llm_note": "🎵 Đang dùng Python-VLC Player. Playlist có thể điều khiển bằng music_next(), music_previous()"
                }
            return {"success": False, "error": "Không có bài tiếp theo trong playlist VLC"}
        
        windows = _find_all_media_windows()
        
        # 2. YouTube
        if windows['youtube']:
            yt = windows['youtube'][0]
            _focus_and_send_hotkey(yt['hwnd'], 'shift', 'n')
            return {"success": True, "message": f"✅ Chuyển video tiếp theo (YouTube): {yt['title'][:40]}..."}
        
        # 3. Windows Media Player
        if windows['wmplayer']:
            _focus_and_send_hotkey(windows['wmplayer']['hwnd'], 'ctrl', 'f')
            return {"success": True, "message": "✅ Chuyển bài tiếp theo (Windows Media Player)"}
        
        # 4. VLC Window (external)
        if windows['vlc']:
            _focus_and_send_key(windows['vlc']['hwnd'], 'n')
            return {"success": True, "message": "✅ Chuyển bài tiếp theo (VLC Window)"}
        
        # 5. Spotify Desktop App
        if windows['spotify_app']:
            _focus_and_send_hotkey(windows['spotify_app']['hwnd'], 'ctrl', 'right')
            return {"success": True, "message": "✅ Chuyển bài tiếp theo (Spotify Desktop)"}
        
        # 6. Spotify Web
        if windows['spotify_web']:
            sw = windows['spotify_web'][0]
            _focus_and_send_hotkey(sw['hwnd'], 'ctrl', 'right')
            return {"success": True, "message": "✅ Chuyển bài tiếp theo (Spotify Web)"}
        
        # 7. Fallback - dùng media key
        pyautogui.press('nexttrack')
        return {"success": True, "message": "✅ Đã chuyển bài tiếp theo (Media Key)"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def media_previous_track() -> dict:
    """
    Chuyển bài trước đó (Previous Track).
    ⭐ ƯU TIÊN PYTHON-VLC TRƯỚC - nhanh & không cần detect window!
    """
    try:
        # 🎵 ƯU TIÊN 1: Python-VLC nội bộ - NHANH NHẤT!
        if vlc_player and vlc_player._player:
            success = vlc_player.previous_track()
            if success:
                import time
                time.sleep(0.3)  # Đợi VLC chuyển bài
                status = vlc_player.get_full_status()
                current_song = status.get('current_song', 'Unknown')
                return {
                    "success": True, 
                    "message": f"⏮️ Đã quay lại: {current_song} (Python-VLC)",
                    "player": "Python-VLC",
                    "current_song": current_song,
                    "llm_note": "🎵 Đang dùng Python-VLC Player. Playlist có thể điều khiển bằng music_next(), music_previous()"
                }
            return {"success": False, "error": "Không có bài trước trong playlist VLC"}
        
        windows = _find_all_media_windows()
        
        # 2. YouTube
        if windows['youtube']:
            yt = windows['youtube'][0]
            _focus_and_send_hotkey(yt['hwnd'], 'shift', 'p')
            return {"success": True, "message": f"✅ Chuyển video trước (YouTube): {yt['title'][:40]}..."}
        
        # 3. Windows Media Player
        if windows['wmplayer']:
            _focus_and_send_hotkey(windows['wmplayer']['hwnd'], 'ctrl', 'b')
            return {"success": True, "message": "✅ Chuyển bài trước (Windows Media Player)"}
        
        # 4. VLC Window (external)
        if windows['vlc']:
            _focus_and_send_key(windows['vlc']['hwnd'], 'p')
            return {"success": True, "message": "✅ Chuyển bài trước (VLC Window)"}
        
        # 5. Spotify Desktop App
        if windows['spotify_app']:
            _focus_and_send_hotkey(windows['spotify_app']['hwnd'], 'ctrl', 'left')
            return {"success": True, "message": "✅ Chuyển bài trước (Spotify Desktop)"}
        
        # 6. Spotify Web
        if windows['spotify_web']:
            sw = windows['spotify_web'][0]
            _focus_and_send_hotkey(sw['hwnd'], 'ctrl', 'left')
            return {"success": True, "message": "✅ Chuyển bài trước (Spotify Web)"}
        
        # 7. Fallback - dùng media key
        pyautogui.press('prevtrack')
        return {"success": True, "message": "✅ Đã chuyển bài trước (Media Key)"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def media_stop() -> dict:
    """
    Dừng phát media (Stop).
    ⭐ ƯU TIÊN PYTHON-VLC TRƯỚC - nhanh & không cần detect window!
    """
    try:
        # 🎵 ƯU TIÊN 1: Python-VLC nội bộ - NHANH NHẤT!
        if vlc_player and vlc_player._player:
            vlc_player.stop()
            return {
                "success": True, 
                "message": "⏹️ Đã dừng nhạc (Python-VLC)",
                "player": "Python-VLC",
                "llm_note": "🎵 Đã dừng Python-VLC Player. Dùng play_music() hoặc resume_music() để phát lại."
            }
        
        windows = _find_all_media_windows()
        
        # 2. YouTube
        if windows['youtube']:
            yt = windows['youtube'][0]
            _focus_and_send_key(yt['hwnd'], 'k', delay=0.2)
            return {"success": True, "message": f"✅ Đã dừng YouTube: {yt['title'][:50]}..."}
        
        # 3. Windows Media Player
        if windows['wmplayer']:
            _focus_and_send_key(windows['wmplayer']['hwnd'], 'stop')
            return {"success": True, "message": "✅ Đã dừng phát (Windows Media Player)"}
        
        # 4. VLC Window (external)
        if windows['vlc']:
            _focus_and_send_key(windows['vlc']['hwnd'], 's')
            return {"success": True, "message": "✅ Đã dừng phát (VLC Window)"}
        
        # 5. Spotify Desktop App - không có stop, dùng pause
        if windows['spotify_app']:
            _focus_and_send_key(windows['spotify_app']['hwnd'], 'space')
            return {"success": True, "message": "✅ Đã tạm dừng (Spotify Desktop)"}
        
        # 6. Spotify Web
        if windows['spotify_web']:
            sw = windows['spotify_web'][0]
            _focus_and_send_key(sw['hwnd'], 'space')
            return {"success": True, "message": "✅ Đã tạm dừng (Spotify Web)"}
        
        # 7. Fallback - dùng media key
        pyautogui.press('stop')
        return {"success": True, "message": "✅ Đã dừng phát (Media Key)"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def media_volume_up() -> dict:
    """Tăng âm lượng media (Media Volume Up)"""
    try:
        pyautogui.press('volumeup')
        return {"success": True, "message": "✅ Đã tăng âm lượng"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def media_volume_down() -> dict:
    """Giảm âm lượng media (Media Volume Down)"""
    try:
        pyautogui.press('volumedown')
        return {"success": True, "message": "✅ Đã giảm âm lượng"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def media_mute() -> dict:
    """Tắt/Bật tiếng media (Mute Toggle)"""
    try:
        pyautogui.press('volumemute')
        return {"success": True, "message": "✅ Đã toggle mute"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def media_control(action: str) -> dict:
    """
    Điều khiển media player đa năng.
    
    Args:
        action: Hành động cần thực hiện
            - "play" hoặc "pause": Phát/Tạm dừng
            - "next": Bài tiếp theo
            - "previous" hoặc "prev": Bài trước
            - "stop": Dừng phát
            - "volume_up": Tăng âm lượng
            - "volume_down": Giảm âm lượng
            - "mute": Tắt/Bật tiếng
    
    Returns:
        dict: Kết quả thực hiện
    """
    try:
        action = action.lower().strip()
        
        actions_map = {
            "play": "playpause",
            "pause": "playpause",
            "playpause": "playpause",
            "next": "nexttrack",
            "previous": "prevtrack",
            "prev": "prevtrack",
            "stop": "stop",
            "volume_up": "volumeup",
            "volumeup": "volumeup",
            "volume_down": "volumedown",
            "volumedown": "volumedown",
            "mute": "volumemute",
        }
        
        key = actions_map.get(action)
        if not key:
            return {
                "success": False, 
                "error": f"Action không hợp lệ: '{action}'. Chọn: play, pause, next, previous, stop, volume_up, volume_down, mute"
            }
        
        pyautogui.press(key)
        
        action_messages = {
            "playpause": "Play/Pause",
            "nexttrack": "Bài tiếp theo",
            "prevtrack": "Bài trước",
            "stop": "Dừng phát",
            "volumeup": "Tăng âm lượng",
            "volumedown": "Giảm âm lượng",
            "volumemute": "Mute/Unmute",
        }
        
        return {"success": True, "message": f"✅ {action_messages[key]}", "action": action}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

# ==================== END MEDIA PLAYER CONTROL ====================

# ==================== TASK MEMORY TOOLS ====================

async def remember_task(tool_name: str, params: dict = None, result_message: str = "", user_request: str = "") -> dict:
    """
    Ghi nhớ một tác vụ đã thực hiện vào bộ nhớ.
    Giúp AI phản hồi nhanh và chính xác hơn cho các yêu cầu tương tự.
    
    Args:
        tool_name: Tên tool đã sử dụng
        params: Tham số đã truyền vào tool
        result_message: Kết quả/message trả về
        user_request: Yêu cầu gốc của user
    """
    try:
        task_entry = add_task_to_memory(
            tool_name=tool_name,
            params=params or {},
            result={"success": True, "message": result_message},
            user_request=user_request
        )
        return {
            "success": True,
            "message": f"✅ Đã ghi nhớ tác vụ: {tool_name}",
            "task": task_entry
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def recall_tasks(keyword: str = "", limit: int = 10) -> dict:
    """
    Nhớ lại các tác vụ đã thực hiện trước đó.
    Giúp AI biết những gì đã làm để phản hồi phù hợp.
    
    Args:
        keyword: Từ khóa tìm kiếm (optional). Để trống = lấy tác vụ gần nhất
        limit: Số lượng tác vụ tối đa trả về (default 10)
    """
    try:
        if keyword:
            tasks = search_task_memory(keyword)
            message = f"🔍 Tìm thấy {len(tasks)} tác vụ liên quan đến '{keyword}'"
        else:
            tasks = get_recent_tasks(limit)
            message = f"📋 {len(tasks)} tác vụ gần đây nhất"
        
        return {
            "success": True,
            "message": message,
            "count": len(tasks),
            "tasks": tasks
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_task_summary() -> dict:
    """
    Lấy tổng hợp thống kê về các tác vụ đã thực hiện.
    Giúp AI hiểu patterns sử dụng của user.
    """
    try:
        tasks = load_task_memory()
        
        if not tasks:
            return {
                "success": True,
                "message": "📊 Chưa có lịch sử tác vụ",
                "total_tasks": 0,
                "most_used_tools": [],
                "success_rate": 0
            }
        
        # Đếm theo tool
        tool_counts = {}
        success_count = 0
        
        for task in tasks:
            tool = task.get('tool', 'unknown')
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
            if task.get('result_success'):
                success_count += 1
        
        # Top 10 tools được dùng nhiều nhất
        sorted_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "success": True,
            "message": f"📊 Đã thực hiện {len(tasks)} tác vụ",
            "total_tasks": len(tasks),
            "most_used_tools": [{"tool": t[0], "count": t[1]} for t in sorted_tools],
            "success_rate": round(success_count / len(tasks) * 100, 1),
            "recent_tools": [t.get('tool') for t in tasks[-5:]]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def forget_all_tasks() -> dict:
    """
    Xóa toàn bộ lịch sử tác vụ đã ghi nhớ.
    """
    try:
        success = clear_task_memory()
        if success:
            return {"success": True, "message": "🗑️ Đã xóa toàn bộ lịch sử tác vụ"}
        else:
            return {"success": False, "error": "Không thể xóa lịch sử"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==================== END TASK MEMORY TOOLS ====================

async def get_active_media_players() -> dict:
    """
    Lấy danh sách các media players/applications đang chạy trên máy tính.
    
    Thông tin này giúp LLM biết:
    - Có media player nào đang chạy không
    - Nên dùng tool nào (media_play_pause cho Spotify/VLC, stop_music cho WMP)
    - Có ứng dụng nào có thể điều khiển được
    
    Returns:
        dict: Danh sách media players, browsers, và ứng dụng quan trọng đang chạy
    """
    try:
        # Danh sách media players và ứng dụng quan trọng cần theo dõi
        MEDIA_APPS = {
            # Media Players
            "spotify.exe": {"name": "Spotify", "type": "music", "supports_media_keys": True},
            "vlc.exe": {"name": "VLC Media Player", "type": "video", "supports_media_keys": True},
            "wmplayer.exe": {"name": "Windows Media Player", "type": "music", "supports_media_keys": True},
            "itunes.exe": {"name": "iTunes", "type": "music", "supports_media_keys": True},
            
            # Browsers (có thể phát YouTube, Spotify Web...)
            "chrome.exe": {"name": "Google Chrome", "type": "browser", "supports_media_keys": True},
            "msedge.exe": {"name": "Microsoft Edge", "type": "browser", "supports_media_keys": True},
            "firefox.exe": {"name": "Firefox", "type": "browser", "supports_media_keys": True},
            "brave.exe": {"name": "Brave", "type": "browser", "supports_media_keys": True},
            "opera.exe": {"name": "Opera", "type": "browser", "supports_media_keys": True},
            "browser.exe": {"name": "Browser", "type": "browser", "supports_media_keys": True},
            "iexplore.exe": {"name": "Internet Explorer", "type": "browser", "supports_media_keys": True},
            "vivaldi.exe": {"name": "Vivaldi", "type": "browser", "supports_media_keys": True},
            
            # Communication (có media playback)
            "discord.exe": {"name": "Discord", "type": "communication", "supports_media_keys": True},
            "slack.exe": {"name": "Slack", "type": "communication", "supports_media_keys": False},
            "zoom.exe": {"name": "Zoom", "type": "communication", "supports_media_keys": False},
            "skype.exe": {"name": "Skype", "type": "communication", "supports_media_keys": False},
            
            # Office & Productivity
            "WINWORD.EXE": {"name": "Microsoft Word", "type": "office", "supports_media_keys": False},
            "EXCEL.EXE": {"name": "Microsoft Excel", "type": "office", "supports_media_keys": False},
            "POWERPNT.EXE": {"name": "PowerPoint", "type": "office", "supports_media_keys": False},
            "OUTLOOK.EXE": {"name": "Outlook", "type": "office", "supports_media_keys": False},
            
            # Development
            "Code.exe": {"name": "VS Code", "type": "development", "supports_media_keys": False},
            "devenv.exe": {"name": "Visual Studio", "type": "development", "supports_media_keys": False},
            "pycharm64.exe": {"name": "PyCharm", "type": "development", "supports_media_keys": False},
            
            # Design & Creative
            "Photoshop.exe": {"name": "Adobe Photoshop", "type": "creative", "supports_media_keys": False},
            "Illustrator.exe": {"name": "Adobe Illustrator", "type": "creative", "supports_media_keys": False},
            "blender.exe": {"name": "Blender", "type": "3d", "supports_media_keys": False},
        }
        
        running_apps = []
        media_players = []
        browsers = []
        
        # Quét các process đang chạy
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name']
                
                if proc_name in MEDIA_APPS:
                    app_info = MEDIA_APPS[proc_name].copy()
                    app_info['pid'] = proc.info['pid']
                    app_info['process_name'] = proc_name
                    
                    running_apps.append(app_info)
                    
                    # Phân loại
                    if app_info['type'] in ['music', 'video']:
                        media_players.append(app_info)
                    elif app_info['type'] == 'browser':
                        browsers.append(app_info)
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Tạo thông điệp hướng dẫn cho LLM (tối ưu hóa, không liệt kê từng instance)
        guidance = ""
        
        if media_players:
            # Đếm số lượng từng loại media player (không liệt kê từng process)
            player_counts = {}
            for p in media_players:
                name = p['name']
                player_counts[name] = player_counts.get(name, 0) + 1
            
            player_summary = ', '.join([f"{name} ({count})" if count > 1 else name 
                                       for name, count in player_counts.items()])
            guidance += f"🎵 Media Players: {player_summary}.\n"
            
            if any(p['name'] == 'Windows Media Player' for p in media_players):
                guidance += "   → Dùng stop_music() để dừng Windows Media Player.\n"
            
            if any(p['supports_media_keys'] and p['name'] != 'Windows Media Player' for p in media_players):
                guidance += "   → Dùng media_play_pause(), media_next_track() cho Spotify/VLC/iTunes.\n"
        
        if browsers:
            # Đếm số lượng từng loại browser (không liệt kê từng process)
            browser_counts = {}
            for b in browsers:
                name = b['name']
                browser_counts[name] = browser_counts.get(name, 0) + 1
            
            browser_summary = ', '.join([f"{name} ({count})" if count > 1 else name 
                                        for name, count in browser_counts.items()])
            guidance += f"🌐 Browsers: {browser_summary}.\n"
            guidance += "   → Có thể phát YouTube/Spotify Web. Dùng media_play_pause() để điều khiển.\n"
        
        if not media_players and not browsers:
            guidance = "❌ Không có media player/browser nào đang chạy. Dùng play_music() để phát nhạc từ music_library."
        
        return {
            "success": True,
            "all_apps": running_apps,
            "media_players": media_players,
            "browsers": browsers,
            "total_count": len(running_apps),
            "guidance": guidance.strip(),
            "message": f"✅ Đang chạy: {len(running_apps)} ứng dụng ({len(media_players)} media players, {len(browsers)} browsers)"
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

async def list_running_processes(limit: int = 10) -> dict:
    try:
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                procs.append({"pid": p.info['pid'], "name": p.info['name'], "cpu": round(p.info['cpu_percent'], 2), "memory": round(p.info['memory_percent'], 2)})
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Bỏ qua các tiến trình không thể truy cập
                pass
        procs = sorted(procs, key=lambda x: x['cpu'], reverse=True)[:limit]
        return {"success": True, "processes": procs, "count": len(procs)}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def kill_process(identifier: str, force: bool = True, exact_match: bool = False) -> dict:
    """
    Kill process ngay lập tức.
    
    Args:
        identifier: Tên app hoặc PID. VD: "notepad", "chrome", "1234"
        force: True = kill ngay (SIGKILL), False = đóng mềm (SIGTERM)
        exact_match: True = tên phải khớp chính xác, False = chứa tên là được
    """
    import subprocess
    import time
    
    try:
        killed = []
        failed = []
        
        # Nếu là PID (số)
        if identifier.isdigit():
            try:
                p = psutil.Process(int(identifier))
                name = p.name()
                if force:
                    p.kill()  # SIGKILL - kill ngay lập tức
                else:
                    p.terminate()  # SIGTERM - đóng mềm
                    p.wait(timeout=3)  # Chờ tối đa 3 giây
                killed.append(f"{name} (PID: {identifier})")
            except psutil.TimeoutExpired:
                # Nếu terminate không được, force kill
                p.kill()
                killed.append(f"{name} (PID: {identifier}) [FORCE KILLED]")
        else:
            # Tìm theo tên
            target_name = identifier.lower()
            
            # Thêm .exe nếu chưa có
            if not target_name.endswith('.exe'):
                target_name_exe = target_name + '.exe'
            else:
                target_name_exe = target_name
                target_name = target_name[:-4]  # Bỏ .exe để so sánh
            
            for p in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = p.info['name'].lower() if p.info['name'] else ""
                    
                    # Kiểm tra match
                    match = False
                    if exact_match:
                        # Khớp chính xác tên
                        match = (proc_name == target_name_exe or proc_name == target_name)
                    else:
                        # Chứa tên là được
                        match = (target_name in proc_name)
                    
                    if match:
                        pid = p.info['pid']
                        try:
                            if force:
                                p.kill()  # Kill ngay lập tức
                            else:
                                p.terminate()
                                try:
                                    p.wait(timeout=2)
                                except psutil.TimeoutExpired:
                                    p.kill()  # Force kill nếu không đóng được
                            killed.append(f"{p.info['name']} (PID: {pid})")
                        except psutil.AccessDenied:
                            # Thử dùng taskkill với quyền cao hơn
                            try:
                                subprocess.run(
                                    ['taskkill', '/F', '/PID', str(pid)],
                                    capture_output=True,
                                    timeout=5
                                )
                                killed.append(f"{p.info['name']} (PID: {pid}) [via taskkill]")
                            except:
                                failed.append(f"{p.info['name']} (PID: {pid}) - Access Denied")
                except (psutil.NoSuchProcess, psutil.ZombieProcess):
                    pass
        
        # Kết quả
        if killed:
            result = {
                "success": True, 
                "message": f"✅ Đã kill thành công: {', '.join(killed)}",
                "killed_count": len(killed),
                "killed": killed
            }
            if failed:
                result["failed"] = failed
                result["message"] += f"\n⚠️ Không thể kill: {', '.join(failed)}"
            return result
        elif failed:
            return {"success": False, "error": f"Không có quyền kill: {', '.join(failed)}"}
        else:
            return {"success": False, "error": f"Không tìm thấy process '{identifier}'"}
            
    except psutil.NoSuchProcess:
        return {"success": False, "error": f"Tiến trình không tồn tại: {identifier}"}
    except psutil.AccessDenied:
        # Thử dùng taskkill
        try:
            if identifier.isdigit():
                result = subprocess.run(
                    ['taskkill', '/F', '/PID', identifier],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                result = subprocess.run(
                    ['taskkill', '/F', '/IM', f'{identifier}*'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            if result.returncode == 0:
                return {"success": True, "message": f"✅ Đã kill bằng taskkill: {identifier}"}
            else:
                return {"success": False, "error": f"Không thể kill (cần quyền Admin): {identifier}"}
        except Exception as e:
            return {"success": False, "error": f"Lỗi khi kill: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def force_kill_app(app_name: str) -> dict:
    """
    Force kill app theo tên CHÍNH XÁC - kill ngay lập tức không hỏi han.
    Sử dụng cả psutil và taskkill để đảm bảo kill được.
    
    Args:
        app_name: Tên app cần kill. VD: "notepad", "chrome", "Code"
    """
    import subprocess
    
    try:
        killed = []
        
        # Chuẩn hóa tên
        target = app_name.lower().strip()
        if not target.endswith('.exe'):
            target_exe = target + '.exe'
        else:
            target_exe = target
            target = target[:-4]
        
        # Bước 1: Kill bằng psutil
        for p in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = (p.info['name'] or "").lower()
                if proc_name == target_exe or proc_name == target or target in proc_name:
                    pid = p.info['pid']
                    try:
                        p.kill()  # SIGKILL - force kill ngay
                        killed.append(f"{p.info['name']} (PID: {pid})")
                    except:
                        pass
            except:
                pass
        
        # Bước 2: Backup với taskkill /F (force)
        try:
            # Kill theo image name
            subprocess.run(
                ['taskkill', '/F', '/IM', target_exe],
                capture_output=True,
                timeout=5
            )
            # Thử cả không có .exe
            subprocess.run(
                ['taskkill', '/F', '/IM', f'{target}*'],
                capture_output=True,
                timeout=5
            )
        except:
            pass
        
        # Bước 3: Verify đã kill hết chưa
        remaining = []
        for p in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = (p.info['name'] or "").lower()
                if proc_name == target_exe or proc_name == target or target in proc_name:
                    remaining.append(f"{p.info['name']} (PID: {p.info['pid']})")
            except:
                pass
        
        if killed and not remaining:
            return {
                "success": True,
                "message": f"✅ Đã FORCE KILL thành công: {', '.join(killed)}",
                "killed_count": len(killed),
                "killed": killed
            }
        elif remaining:
            return {
                "success": False,
                "error": f"❌ Không thể kill (cần quyền Admin): {', '.join(remaining)}",
                "killed": killed if killed else []
            }
        else:
            return {
                "success": False,
                "error": f"Không tìm thấy app '{app_name}' đang chạy"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

async def create_file(path: str, content: str) -> dict:
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "path": path, "message": f"Đã tạo: {path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def read_file(path: str) -> dict:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"success": True, "path": path, "content": content[:500], "size": len(content)}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def list_files(directory: str) -> dict:
    try:
        import os
        files = []
        for item in os.listdir(directory):
            p = os.path.join(directory, item)
            files.append({"name": item, "type": "dir" if os.path.isdir(p) else "file", "size": os.path.getsize(p) if os.path.isfile(p) else 0})
        return {"success": True, "directory": directory, "files": files, "count": len(files)}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_battery_status() -> dict:
    try:
        bat = psutil.sensors_battery()
        if bat is None:
            return {"success": False, "error": "Không thể lấy thông tin pin (có thể không có pin)"}
        return {
            "success": True,
            "percent": bat.percent,
            "plugged": bat.power_plugged,
            "time_left": str(bat.secsleft) if bat.secsleft != psutil.POWER_TIME_UNLIMITED else "Unlimited"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_disk_usage() -> dict:
    try:
        disks = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disks.append({"device": part.device, "mountpoint": part.mountpoint, "fstype": part.fstype, "total_gb": round(usage.total / (1024**3), 2), "used_gb": round(usage.used / (1024**3), 2), "free_gb": round(usage.free / (1024**3), 2), "percent": usage.percent})
            except (PermissionError, OSError):
                # Bỏ qua các ổ đĩa không thể truy cập
                pass
        return {"success": True, "disks": disks, "count": len(disks)}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================
# MUSIC LIBRARY TOOLS - VLC PLAYER
# ============================================================

MUSIC_LIBRARY = Path(__file__).parent / "music_library"
MUSIC_EXTENSIONS = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.wma', '.aac'}

# YouTube Playlists Management
YOUTUBE_PLAYLISTS_FILE = Path(__file__).parent / "youtube_playlists.json"

def load_youtube_playlists() -> list:
    """Đọc danh sách playlist YouTube từ file JSON"""
    try:
        if YOUTUBE_PLAYLISTS_FILE.exists():
            with open(YOUTUBE_PLAYLISTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"❌ [Playlists] Error loading: {e}")
        return []

def save_youtube_playlists(playlists: list) -> bool:
    """Lưu danh sách playlist YouTube vào file JSON"""
    try:
        with open(YOUTUBE_PLAYLISTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(playlists, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ [Playlists] Error saving: {e}")
        return False

async def add_youtube_playlist(name: str, url: str) -> dict:
    """Thêm playlist YouTube mới"""
    try:
        playlists = load_youtube_playlists()
        
        # Kiểm tra trùng tên
        if any(p['name'].lower() == name.lower() for p in playlists):
            return {
                "success": False,
                "error": f"Playlist '{name}' đã tồn tại!"
            }
        
        # Thêm playlist mới
        new_playlist = {
            "name": name,
            "url": url,
            "created_at": datetime.now().isoformat()
        }
        playlists.append(new_playlist)
        
        if save_youtube_playlists(playlists):
            return {
                "success": True,
                "message": f"✅ Đã thêm playlist: {name}",
                "playlist": new_playlist
            }
        else:
            return {
                "success": False,
                "error": "Không thể lưu playlist"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def remove_youtube_playlist(name: str) -> dict:
    """Xóa playlist YouTube"""
    try:
        playlists = load_youtube_playlists()
        
        # Tìm và xóa playlist
        original_count = len(playlists)
        playlists = [p for p in playlists if p['name'].lower() != name.lower()]
        
        if len(playlists) == original_count:
            return {
                "success": False,
                "error": f"Không tìm thấy playlist: {name}"
            }
        
        if save_youtube_playlists(playlists):
            return {
                "success": True,
                "message": f"✅ Đã xóa playlist: {name}"
            }
        else:
            return {
                "success": False,
                "error": "Không thể lưu thay đổi"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_youtube_playlists() -> dict:
    """Lấy danh sách tất cả playlist YouTube"""
    try:
        playlists = load_youtube_playlists()
        return {
            "success": True,
            "playlists": playlists,
            "count": len(playlists)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def open_youtube_playlist(playlist_name: str) -> dict:
    """Mở playlist YouTube đã lưu trong browser
    
    Args:
        playlist_name: Tên playlist đã đăng ký (có thể là tên đầy đủ hoặc từ khóa)
    
    Returns:
        dict với thông tin playlist đã mở
    """
    try:
        import webbrowser
        
        playlists = load_youtube_playlists()
        
        if not playlists:
            return {
                "success": False,
                "error": "Chưa có playlist nào. Hãy thêm playlist trên Web UI!"
            }
        
        # Tìm playlist (exact match hoặc partial match)
        playlist_name_lower = playlist_name.lower()
        matched_playlist = None
        
        # Tìm exact match trước
        for p in playlists:
            if p['name'].lower() == playlist_name_lower:
                matched_playlist = p
                break
        
        # Nếu không có exact match, tìm partial match
        if not matched_playlist:
            for p in playlists:
                if playlist_name_lower in p['name'].lower():
                    matched_playlist = p
                    break
        
        if not matched_playlist:
            # Hiển thị danh sách playlist có sẵn
            available = [p['name'] for p in playlists]
            return {
                "success": False,
                "error": f"Không tìm thấy playlist: '{playlist_name}'",
                "available_playlists": available,
                "hint": f"Có {len(available)} playlist: {', '.join(available)}"
            }
        
        # Mở playlist trong browser
        webbrowser.open(matched_playlist['url'])
        
        print(f"🎵 [YouTube Playlist] Đã mở: {matched_playlist['name']}")
        
        return {
            "success": True,
            "message": f"✅ Đã mở playlist: {matched_playlist['name']}",
            "playlist": matched_playlist,
            "url": matched_playlist['url']
        }
        
    except Exception as e:
        print(f"❌ [YouTube Playlist] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

# VLC Player Manager (Singleton)
class VLCMusicPlayer:
    """
    VLC Music Player với hỗ trợ đầy đủ:
    - Play/Pause/Stop
    - Next/Previous track
    - Playlist management
    - Media keys support (VLC tự động hỗ trợ)
    """
    _instance = None
    _player = None
    _media_list = None
    _list_player = None
    _current_playlist = []
    _shuffle = False
    _repeat_mode = 0  # 0: off, 1: all, 2: one
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._player is None:
            try:
                import vlc
                self._vlc = vlc
                # Tạo VLC instance với UI đầy đủ
                # Không dùng --no-xlib, --no-video, --no-audio-display
                # Thêm --video-on-top để cửa sổ luôn hiển thị
                self._instance_vlc = vlc.Instance()  # Empty options = full UI
                self._player = self._instance_vlc.media_player_new()
                self._media_list = self._instance_vlc.media_list_new()
                self._list_player = self._instance_vlc.media_list_player_new()
                self._list_player.set_media_player(self._player)
                print("✅ [VLC] VLC Music Player initialized (full UI mode)")
            except Exception as e:
                print(f"❌ [VLC] Failed to initialize: {e}")
                self._player = None
    
    def play_file(self, file_path: str):
        """Phát 1 file nhạc"""
        if not self._player:
            return False
        try:
            media = self._instance_vlc.media_new(file_path)
            self._player.set_media(media)
            self._player.play()
            return True
        except Exception as e:
            print(f"❌ [VLC] Play error: {e}")
            return False
    
    def play_playlist(self, file_paths: list):
        """Phát playlist với nhiều bài"""
        if not self._list_player:
            print("❌ [VLC] list_player chưa khởi tạo")
            return False
        try:
            print(f"🎵 [VLC DEBUG] play_playlist called with {len(file_paths)} files")
            for i, p in enumerate(file_paths[:3]):  # Log 3 file đầu
                print(f"   [{i+1}] {p}")
            
            # QUAN TRỌNG: STOP bài đang phát trước!
            self._list_player.stop()
            import time
            time.sleep(0.3)
            print("🛑 [VLC] Stopped current playback")
            
            # Clear playlist cũ và tạo mới
            self._media_list = self._instance_vlc.media_list_new()
            self._current_playlist = file_paths
            
            # Thêm tất cả bài vào playlist
            for path in file_paths:
                media = self._instance_vlc.media_new(path)
                self._media_list.add_media(media)
            
            print(f"🎵 [VLC DEBUG] Media list count: {self._media_list.count()}")
            
            # Set playlist mới
            self._list_player.set_media_list(self._media_list)
            
            # Set current index to 0 (first song)
            self._current_index = 0
            
            # QUAN TRỌNG: Gọi play() để phát bài đầu tiên
            self._list_player.play()
            print(f"🎵 [VLC DEBUG] list_player.play() called")
            
            # Đợi VLC bắt đầu
            time.sleep(0.5)
            
            # Kiểm tra và đảm bảo đang phát
            if self._player:
                state = self._player.get_state()
                is_playing = self._player.is_playing()
                current_vol = self._player.audio_get_volume()
                print(f"🎵 [VLC DEBUG] State: {state}, is_playing: {is_playing}, volume: {current_vol}")
                
                # Nếu chưa phát, thử play lại
                if not is_playing:
                    print("⚠️ [VLC DEBUG] Not playing, trying play() again...")
                    self._list_player.play()
                    time.sleep(0.3)
                
                # Đảm bảo volume đủ nghe
                if current_vol < 50:
                    self._player.audio_set_volume(80)
                    print(f"🔊 [VLC] Volume was {current_vol}, set to 80")
            
            print(f"▶️ [VLC] Playing playlist with {len(file_paths)} songs")
            return True
        except Exception as e:
            print(f"❌ [VLC] Playlist error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def pause(self):
        """Tạm dừng"""
        if self._player:
            self._player.pause()
            return True
        return False
    
    def resume(self):
        """Tiếp tục phát - Đảm bảo đang play"""
        if self._list_player:
            # Nếu đang paused, gọi play để tiếp tục
            if not self.is_playing():
                self._list_player.play()
            return True
        elif self._player:
            if not self.is_playing():
                self._player.play()
            return True
        return False
    
    def stop(self):
        """Dừng phát"""
        if self._list_player:
            self._list_player.stop()
        if self._player:
            self._player.stop()
        return True
    
    def next_track(self):
        """Bài tiếp theo - Tự động phát luôn!"""
        if self._list_player and self._current_playlist:
            current_idx = getattr(self, '_current_index', 0)
            last_idx = len(self._current_playlist) - 1
            
            if current_idx >= last_idx:
                # Đã ở bài cuối, quay lại bài đầu
                self._current_index = 0
                self._list_player.play_item_at_index(0)
                print(f"🔄 [VLC] Next: Wrap to first track (index 0)")
            else:
                # Còn bài tiếp, chuyển bình thường
                self._list_player.next()
                self._current_index = current_idx + 1
                print(f"⏭️ [VLC] Next: Now at index {self._current_index}")
            
            import time
            time.sleep(0.3)
            # Đảm bảo đang phát sau khi chuyển bài
            if not self.is_playing():
                self._list_player.play()
            return True
        return False
    
    def previous_track(self):
        """Bài trước - Tự động phát luôn!"""
        if self._list_player and self._current_playlist:
            # Kiểm tra nếu đang ở bài đầu tiên
            current_idx = getattr(self, '_current_index', 0)
            
            if current_idx <= 0:
                # Đã ở bài đầu, quay lại bài cuối cùng của playlist
                last_idx = len(self._current_playlist) - 1
                self._current_index = last_idx
                # Play bài cuối bằng cách set media trực tiếp
                self._list_player.play_item_at_index(last_idx)
                print(f"🔄 [VLC] Previous: Wrap to last track (index {last_idx})")
            else:
                # Còn bài trước, chuyển bình thường
                self._list_player.previous()
                self._current_index = current_idx - 1
                print(f"⏮️ [VLC] Previous: Now at index {self._current_index}")
            
            import time
            time.sleep(0.3)
            
            # Đảm bảo đang phát sau khi chuyển bài
            if not self.is_playing():
                self._list_player.play()
            return True
        return False
    
    def is_playing(self):
        """Kiểm tra đang phát không"""
        if self._player:
            return self._player.is_playing()
        return False
    
    def get_state(self):
        """Lấy trạng thái player"""
        if not self._player:
            return "not_initialized"
        
        state = self._player.get_state()
        state_map = {
            0: "idle",
            1: "opening",
            2: "buffering", 
            3: "playing",
            4: "paused",
            5: "stopped",
            6: "ended",
            7: "error"
        }
        return state_map.get(state, "unknown")
    
    def get_position(self):
        """Lấy vị trí hiện tại (0.0 - 1.0)"""
        if self._player:
            return self._player.get_position() or 0.0
        return 0.0
    
    def get_time(self):
        """Lấy thời gian hiện tại (milliseconds)"""
        if self._player:
            return self._player.get_time() or 0
        return 0
    
    def get_length(self):
        """Lấy độ dài bài hát (milliseconds)"""
        if self._player:
            return self._player.get_length() or 0
        return 0
    
    def get_volume(self):
        """Lấy âm lượng hiện tại (0-100)"""
        if self._player:
            return self._player.audio_get_volume() or 0
        return 0
    
    def set_volume(self, level: int):
        """Đặt âm lượng (0-100)"""
        if self._player:
            level = max(0, min(100, level))
            self._player.audio_set_volume(level)
            return True
        return False
    
    def set_position(self, position: float):
        """Đặt vị trí (0.0 - 1.0)"""
        if self._player:
            position = max(0.0, min(1.0, position))
            self._player.set_position(position)
            return True
        return False
    
    def get_current_media_title(self):
        """Lấy tiêu đề media đang phát"""
        if self._player:
            media = self._player.get_media()
            if media:
                # Thử lấy meta title, nếu không có thì lấy MRL (path)
                title = media.get_meta(self._vlc.Meta.Title)
                if title:
                    return title
                # Fallback: lấy filename từ MRL
                mrl = media.get_mrl()
                if mrl:
                    from urllib.parse import unquote
                    # Decode URL và lấy filename
                    path = unquote(mrl.replace('file:///', '').replace('file://', ''))
                    return Path(path).name
        return None
    
    def get_playlist_index(self):
        """Lấy index bài hiện tại trong playlist"""
        # VLC không có API trực tiếp, phải track riêng
        return getattr(self, '_current_index', 0)
    
    def get_playlist_count(self):
        """Lấy số bài trong playlist"""
        return len(self._current_playlist) if self._current_playlist else 0
    
    def get_full_status(self):
        """Lấy trạng thái đầy đủ cho Web UI"""
        state = self.get_state()
        current_time_ms = self.get_time()
        duration_ms = self.get_length()
        
        return {
            "state": state,
            "is_playing": self.is_playing(),
            "position": self.get_position(),
            "current_time_ms": current_time_ms,
            "current_time_formatted": self._format_time(current_time_ms),
            "duration_ms": duration_ms,
            "duration_formatted": self._format_time(duration_ms),
            "volume": self.get_volume(),
            "current_track": self.get_current_media_title(),
            "playlist_index": self.get_playlist_index(),
            "playlist_count": self.get_playlist_count(),
            "playlist": [Path(p).name for p in self._current_playlist[:20]] if self._current_playlist else [],  # Top 20 only
            "shuffle": self._shuffle,
            "repeat_mode": self._repeat_mode  # 0: off, 1: all, 2: one
        }
    
    def set_shuffle(self, enabled: bool):
        """Bật/tắt chế độ phát ngẫu nhiên"""
        self._shuffle = enabled
        if self._list_player:
            # VLC MediaListPlayer không có native shuffle, ta xử lý thủ công khi next/previous
            pass
        return self._shuffle
    
    def set_repeat_mode(self, mode: int):
        """Đặt chế độ lặp lại: 0=off, 1=all, 2=one"""
        self._repeat_mode = mode
        if self._list_player:
            if mode == 0:
                self._list_player.set_playback_mode(self._vlc.PlaybackMode.default)
            elif mode == 1:
                self._list_player.set_playback_mode(self._vlc.PlaybackMode.loop)
            elif mode == 2:
                self._list_player.set_playback_mode(self._vlc.PlaybackMode.repeat)
        return self._repeat_mode
    
    def get_shuffle(self):
        """Lấy trạng thái shuffle"""
        return getattr(self, '_shuffle', False)
    
    def get_repeat_mode(self):
        """Lấy chế độ repeat: 0=off, 1=all, 2=one"""
        return getattr(self, '_repeat_mode', 0)
    
    def _format_time(self, ms):
        """Format milliseconds thành MM:SS"""
        if not ms or ms < 0:
            return "0:00"
        seconds = int(ms / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"

# Global VLC player instance - với error handling
try:
    vlc_player = VLCMusicPlayer()
    VLC_AVAILABLE = vlc_player._player is not None
except Exception as e:
    print(f"⚠️ [VLC] VLC không khả dụng: {e}")
    vlc_player = None
    VLC_AVAILABLE = False

if not VLC_AVAILABLE:
    print("⚠️ [VLC] Music player disabled. Cài VLC: https://www.videolan.org/vlc/")

# ============================================================
# BROWSER CONTROLLER - Selenium Automation
# ============================================================

class BrowserController:
    """Singleton class để điều khiển trình duyệt Chrome bằng Selenium"""
    
    _instance = None
    _driver = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _ensure_driver(self):
        """Khởi tạo Chrome driver nếu chưa có"""
        if self._driver is None:
            if not SELENIUM_AVAILABLE:
                raise Exception("Selenium chưa được cài đặt. Chạy: pip install selenium webdriver-manager")
            
            try:
                chrome_options = Options()
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--start-maximized')
                
                service = Service(ChromeDriverManager().install())
                self._driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ [Browser] Chrome driver initialized")
            except Exception as e:
                print(f"❌ [Browser] Failed to initialize: {e}")
                raise
        return self._driver
    
    def open_url(self, url: str) -> dict:
        """Mở URL trong browser"""
        try:
            driver = self._ensure_driver()
            driver.get(url)
            return {
                "success": True,
                "url": driver.current_url,
                "title": driver.title,
                "message": f"Đã mở: {driver.title}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_current_info(self) -> dict:
        """Lấy thông tin trang hiện tại"""
        try:
            if self._driver is None:
                return {"success": False, "error": "Browser chưa được khởi động"}
            
            return {
                "success": True,
                "url": self._driver.current_url,
                "title": self._driver.title,
                "window_handles": len(self._driver.window_handles)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def click_element(self, selector: str, by: str = "css") -> dict:
        """Click vào element"""
        try:
            driver = self._ensure_driver()
            
            by_map = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "name": By.NAME,
                "class": By.CLASS_NAME,
                "tag": By.TAG_NAME
            }
            
            by_type = by_map.get(by.lower(), By.CSS_SELECTOR)
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((by_type, selector))
            )
            element.click()
            
            return {
                "success": True,
                "message": f"Đã click vào element: {selector}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def fill_input(self, selector: str, text: str, by: str = "css") -> dict:
        """Điền text vào input field"""
        try:
            driver = self._ensure_driver()
            
            by_map = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "name": By.NAME,
                "class": By.CLASS_NAME
            }
            
            by_type = by_map.get(by.lower(), By.CSS_SELECTOR)
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by_type, selector))
            )
            element.clear()
            element.send_keys(text)
            
            return {
                "success": True,
                "message": f"Đã điền text vào: {selector}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def scroll(self, direction: str = "down", amount: int = 500) -> dict:
        """Cuộn trang"""
        try:
            driver = self._ensure_driver()
            
            if direction == "top":
                driver.execute_script("window.scrollTo(0, 0);")
            elif direction == "bottom":
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            elif direction == "down":
                driver.execute_script(f"window.scrollBy(0, {amount});")
            elif direction == "up":
                driver.execute_script(f"window.scrollBy(0, -{amount});")
            else:
                return {"success": False, "error": f"Invalid direction: {direction}"}
            
            return {
                "success": True,
                "message": f"Đã cuộn {direction}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def go_back(self) -> dict:
        """Quay lại trang trước"""
        try:
            if self._driver is None:
                return {"success": False, "error": "Browser chưa được khởi động"}
            self._driver.back()
            return {"success": True, "message": "Đã quay lại trang trước"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def go_forward(self) -> dict:
        """Tiến tới trang sau"""
        try:
            if self._driver is None:
                return {"success": False, "error": "Browser chưa được khởi động"}
            self._driver.forward()
            return {"success": True, "message": "Đã tiến tới trang sau"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def refresh(self) -> dict:
        """Làm mới trang"""
        try:
            if self._driver is None:
                return {"success": False, "error": "Browser chưa được khởi động"}
            self._driver.refresh()
            return {"success": True, "message": "Đã làm mới trang"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def screenshot(self, filepath: str = None) -> dict:
        """Chụp screenshot trang hiện tại"""
        try:
            if self._driver is None:
                return {"success": False, "error": "Browser chưa được khởi động"}
            
            if filepath is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = f"screenshot_{timestamp}.png"
            
            self._driver.save_screenshot(filepath)
            return {
                "success": True,
                "filepath": filepath,
                "message": f"Đã lưu screenshot: {filepath}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def new_tab(self, url: str = None) -> dict:
        """Mở tab mới"""
        try:
            driver = self._ensure_driver()
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            
            if url:
                driver.get(url)
            
            return {
                "success": True,
                "message": f"Đã mở tab mới{' và truy cập ' + url if url else ''}",
                "total_tabs": len(driver.window_handles)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def close_tab(self) -> dict:
        """Đóng tab hiện tại"""
        try:
            if self._driver is None:
                return {"success": False, "error": "Browser chưa được khởi động"}
            
            self._driver.close()
            if len(self._driver.window_handles) > 0:
                self._driver.switch_to.window(self._driver.window_handles[-1])
            
            return {
                "success": True,
                "message": "Đã đóng tab",
                "remaining_tabs": len(self._driver.window_handles)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_script(self, script: str) -> dict:
        """Thực thi JavaScript code"""
        try:
            driver = self._ensure_driver()
            result = driver.execute_script(script)
            return {
                "success": True,
                "result": result,
                "message": "Đã thực thi JavaScript"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def close_browser(self) -> dict:
        """Đóng browser hoàn toàn"""
        try:
            if self._driver:
                self._driver.quit()
                self._driver = None
                return {"success": True, "message": "Đã đóng browser"}
            return {"success": False, "error": "Browser chưa được khởi động"}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global browser controller instance
browser_controller = BrowserController()

async def list_music(subfolder: str = "", auto_play: bool = True, folder: str = "") -> dict:
    """
    Liệt kê file nhạc trong music_library hoặc thư mục tùy chỉnh.
    Theo mặc định TỰ ĐỘNG PHÁT bài đầu tiên (giống xinnan-tech/xiaozhi-esp32-server).
    Set auto_play=False để chỉ liệt kê không phát.
    
    Args:
        subfolder: Subfolder trong music_library
        auto_play: Tự động phát bài đầu tiên (default True)
        folder: Thư mục tùy chỉnh (nếu có, sẽ override music_library)
    """
    try:
        # Xác định thư mục gốc
        if folder and folder.strip():
            base_path = Path(folder.strip())
            if not base_path.exists():
                return {"success": False, "error": f"Thư mục '{folder}' không tồn tại"}
            search_path = base_path
            is_user_folder = True
        else:
            if not MUSIC_LIBRARY.exists():
                MUSIC_LIBRARY.mkdir(exist_ok=True)
                return {"success": True, "files": [], "count": 0, "message": "Thư mục music_library đã được tạo. Hãy thêm nhạc vào!"}
            
            base_path = MUSIC_LIBRARY
            search_path = MUSIC_LIBRARY / subfolder if subfolder else MUSIC_LIBRARY
            is_user_folder = False
        
        if not search_path.exists():
            return {"success": False, "error": f"Thư mục '{subfolder or folder}' không tồn tại"}
        
        music_files = []
        for file_path in search_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in MUSIC_EXTENSIONS:
                try:
                    relative_path = file_path.relative_to(base_path)
                except ValueError:
                    relative_path = file_path.name
                    
                music_files.append({
                    "filename": file_path.name,
                    "path": str(relative_path).replace('\\', '/'),
                    "full_path": str(file_path),
                    "size_mb": round(file_path.stat().st_size / (1024**2), 2),
                    "extension": file_path.suffix.lower()
                })
        
        music_files.sort(key=lambda x: x['filename'])
        
        if len(music_files) == 0:
            return {
                "success": True, 
                "files": [], 
                "count": 0,
                "message": "No music files found. Please add music files to the folder.",
                "is_user_folder": is_user_folder,
                "source_path": str(base_path)
            }
        
        # 🎵 AUTO-PLAY: Tự động phát bài đầu tiên (như code reference)
        first_file = music_files[0]['filename'] if not is_user_folder else music_files[0]['full_path']
        play_result = None
        
        if auto_play:
            print(f"🎵 [Auto-Play] list_music tự động phát: {first_file}")
            if is_user_folder:
                # Phát từ user folder bằng default player
                play_result = await play_music_from_path(music_files[0]['full_path'])
            else:
                play_result = await play_music(first_file)
            
            if play_result.get("success"):
                message = f"✅ Auto-played: {music_files[0]['filename']}\nTotal {len(music_files)} song(s)"
            else:
                message = f"❌ Found {len(music_files)} songs but failed to play: {play_result.get('error', 'Unknown error')}"
        else:
            filenames_list = [f['filename'] for f in music_files]
            message = f"Found {len(music_files)} song(s):\n" + "\n".join([f"  - {fname}" for fname in filenames_list[:10]])
            if len(music_files) > 10:
                message += f"\n  ... and {len(music_files) - 10} more"
        
        return {
            "success": True,
            "files": music_files,
            "count": len(music_files),
            "library_path": str(base_path),
            "is_user_folder": is_user_folder,
            "message": message,
            "auto_played": auto_play,
            "play_result": play_result if auto_play else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def play_music_from_path(file_path: str) -> dict:
    """
    Phát nhạc từ đường dẫn đầy đủ bằng Python-VLC (KHÔNG dùng trình phát mặc định).
    ⭐ NHANH & TIỆN - Dùng VLC nội bộ!
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {"success": False, "error": f"File không tồn tại: {file_path}"}
        
        # 🎵 SỬ DỤNG VLC thay vì os.startfile - NHANH!
        success = vlc_player.play_playlist([str(path)])
        
        if success:
            print(f"🎵 [VLC] Đang phát từ path: {path.name}")
            return {
                "success": True,
                "message": f"🎵 Đang phát: {path.name} (Python-VLC)",
                "file": path.name,
                "path": str(path),
                "player": "Python-VLC",
                "llm_note": "🎵 ĐANG DÙNG PYTHON-VLC. Điều khiển: pause_music(), resume_music(), stop_music(), music_next(), music_previous(). NHANH & TIỆN!"
            }
        else:
            return {"success": False, "error": "VLC Player không thể phát file"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def play_music(filename: str, create_playlist: bool = True) -> dict:
    """
    Phát nhạc từ music_library bằng VLC player.
    
    Args:
        filename: Tên file (e.g., 'song.mp3' or 'Pop/song.mp3')
        create_playlist: Tạo playlist với tất cả bài (default True) để hỗ trợ Next/Previous
        
    Returns:
        dict with 'success', 'filename', 'path', 'message'
    """
    try:
        if not MUSIC_LIBRARY.exists():
            return {"success": False, "error": "Thư mục music_library không tồn tại"}
        
        print(f"🎵 [VLC Play] Tìm file: '{filename}'")
        
        # Tìm file
        music_path = None
        filename_lower = filename.lower()
        
        for file_path in MUSIC_LIBRARY.rglob("*"):
            if file_path.is_file():
                if (file_path.name == filename or 
                    file_path.name.lower() == filename_lower or
                    str(file_path.relative_to(MUSIC_LIBRARY)).replace('\\', '/') == filename or
                    filename_lower in file_path.name.lower()):
                    if file_path.suffix.lower() in MUSIC_EXTENSIONS:
                        music_path = file_path
                        break
        
        if not music_path:
            available = [f.name for f in MUSIC_LIBRARY.rglob("*") if f.is_file() and f.suffix.lower() in MUSIC_EXTENSIONS]
            return {
                "success": False, 
                "error": f"Không tìm thấy '{filename}'",
                "available_files": available[:5]
            }
        
        print(f"🎵 [VLC Play] Đã tìm thấy: {music_path}")
        
        if create_playlist:
            # Tạo playlist với tất cả bài trong thư mục
            all_songs = sorted([
                str(f) for f in MUSIC_LIBRARY.rglob("*") 
                if f.is_file() and f.suffix.lower() in MUSIC_EXTENSIONS
            ])
            
            # Đảm bảo bài hiện tại ở đầu playlist
            if str(music_path) in all_songs:
                all_songs.remove(str(music_path))
            all_songs.insert(0, str(music_path))
            
            success = vlc_player.play_playlist(all_songs)
            print(f"🎵 [VLC] Created playlist with {len(all_songs)} songs")
        else:
            success = vlc_player.play_file(str(music_path))
        
        if success:
            return {
                "success": True,
                "filename": music_path.name,
                "path": str(music_path.relative_to(MUSIC_LIBRARY)),
                "full_path": str(music_path),
                "size_mb": round(music_path.stat().st_size / (1024**2), 2),
                "message": f"🎵 Đang phát: {music_path.name} (Python-VLC)",
                "player": "Python-VLC",
                "playlist_mode": create_playlist,
                "llm_note": "🎵 ĐANG DÙNG PYTHON-VLC PLAYER. Điều khiển: pause_music(), resume_music(), stop_music(), music_next(), music_previous(), seek_music(), music_volume(). NHANH & TIỆN!"
            }
        else:
            return {"success": False, "error": "VLC player không thể phát. Kiểm tra VLC đã cài đặt chưa!"}
    except Exception as e:
        print(f"❌ [VLC Play] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

async def pause_music() -> dict:
    """
    Tạm dừng nhạc VLC Player (Python-VLC internal).
    LUÔN dùng VLC player - NHANH & TIỆN!
    """
    try:
        if vlc_player and vlc_player._player:
            vlc_player.pause()
            status = vlc_player.get_full_status()
            current_song = status.get('current_song', 'Unknown')
            return {
                "success": True, 
                "message": f"⏸️ Đã tạm dừng: {current_song} (Python-VLC)",
                "player": "Python-VLC",
                "current_song": current_song,
                "llm_note": "🎵 Đang dùng Python-VLC. Dùng resume_music() để tiếp tục, music_next()/music_previous() để chuyển bài."
            }
        else:
            return {"success": False, "error": "VLC Player chưa khởi tạo hoặc chưa phát nhạc. Dùng play_music() để phát nhạc trước!"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def resume_music() -> dict:
    """
    Tiếp tục phát nhạc VLC Player (Python-VLC internal).
    LUÔN dùng VLC player - NHANH & TIỆN!
    """
    try:
        if vlc_player and vlc_player._player:
            vlc_player.resume()  # Dùng method resume() mới - đảm bảo play
            import time
            time.sleep(0.2)
            status = vlc_player.get_full_status()
            current_song = status.get('current_song', 'Unknown')
            return {
                "success": True, 
                "message": f"▶️ Đang phát: {current_song} (Python-VLC)",
                "player": "Python-VLC",
                "current_song": current_song,
                "is_playing": True,
                "llm_note": "🎵 Đang dùng Python-VLC. Dùng pause_music() để tạm dừng, music_next()/music_previous() để chuyển bài."
            }
        else:
            return {"success": False, "error": "VLC Player chưa khởi tạo hoặc chưa phát nhạc. Dùng play_music() để phát nhạc trước!"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def stop_music() -> dict:
    """
    Dừng nhạc VLC Player (Python-VLC internal).
    LUÔN dùng VLC player - NHANH & TIỆN!
    """
    try:
        if vlc_player and vlc_player._player:
            vlc_player.stop()
            return {
                "success": True, 
                "message": "⏹️ Đã dừng nhạc hoàn toàn (Python-VLC)",
                "player": "Python-VLC",
                "llm_note": "🎵 Đã dừng Python-VLC Player. Dùng play_music() để phát nhạc mới."
            }
        else:
            return {"success": False, "error": "VLC Player chưa khởi tạo hoặc chưa phát nhạc."}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================
# SMART MUSIC CONTROL - Điều khiển nhạc thông minh bằng ngôn ngữ tự nhiên
# Focus vào Python-VLC Player cho tất cả lệnh nhạc LOCAL
# ============================================================

# ============================================================
# FUZZY MATCHING - Xử lý nhận dạng giọng nói không chính xác từ ESP32
# ============================================================

# Các biến thể phát âm sai thường gặp (từ ESP32 voice recognition)
VOICE_CORRECTIONS = {
    # Bài tiếp/next variations
    'bài tiếp': ['bài tiếp', 'bai tiep', 'bài diệp', 'bài thiếp', 'bài típ', 'bay tiep', 'bai tip', 'bai diep'],
    'tiếp theo': ['tiếp theo', 'tiep theo', 'thiếp theo', 'típ theo', 'tiếp thêu', 'diệp theo'],
    'next': ['next', 'nex', 'nếch', 'nếc', 'nếx', 'net', 'nec'],
    'skip': ['skip', 'skíp', 'xkip', 'xíp', 'ship'],
    
    # Bài trước/previous variations  
    'bài trước': ['bài trước', 'bai truoc', 'bài chước', 'bài trước', 'bay truoc', 'bai chuoc', 'bài trướt'],
    'quay lại': ['quay lại', 'quay lai', 'quay lại bài', 'quai lai', 'quai lại', 'quáy lại'],
    'previous': ['previous', 'pre', 'prê', 'pri vi ớt', 'pri', 'prê vi ớt'],
    
    # Dừng/stop variations
    'dừng nhạc': ['dừng nhạc', 'dung nhac', 'dừng nhạc', 'dừng lại', 'dzừng nhạc'],
    'tắt nhạc': ['tắt nhạc', 'tat nhac', 'tắc nhạc', 'tác nhạc', 'tad nhac'],
    'pause': ['pause', 'pao', 'pốt', 'pót', 'pao xờ', 'pa'],
    'stop': ['stop', 'stóp', 'xtóp', 's top', 'x tóp'],
    
    # Phát nhạc variations
    'phát nhạc': ['phát nhạc', 'phat nhac', 'phác nhạc', 'phát nhạt', 'phad nhac'],
    'bật nhạc': ['bật nhạc', 'bat nhac', 'bặt nhạc', 'bặc nhạc', 'bac nhac'],
    'mở nhạc': ['mở nhạc', 'mo nhac', 'mơ nhạc', 'mỡ nhạc'],
    'play': ['play', 'plây', 'pờ lây', 'p lay', 'plei'],
    
    # Âm lượng variations
    'tăng âm lượng': ['tăng âm lượng', 'tang am luong', 'tăng tiếng', 'tang tieng', 'to lên', 'to len'],
    'giảm âm lượng': ['giảm âm lượng', 'giam am luong', 'giảm tiếng', 'giam tieng', 'nhỏ lại', 'nho lai'],
    'volume': ['volume', 'vol', 'vô lum', 'vo lum', 'vô liêm'],
    
    # Shuffle/repeat variations
    'shuffle': ['shuffle', 'sáp phồ', 'xáp phồ', 'sờ phồ', 'trộn bài', 'tron bai', 'ngẫu nhiên'],
    'repeat': ['repeat', 'ri pít', 'rì pít', 'lặp lại', 'lap lai', 'loop', 'lúp'],
}

def normalize_voice_command(text: str) -> str:
    """
    Chuẩn hóa lệnh voice từ ESP32 - sửa lỗi nhận dạng phổ biến.
    Giúp nhận dạng chính xác hơn khi microphone bắt sai.
    """
    if not text:
        return ""
    
    text_lower = text.lower().strip()
    
    # Loại bỏ các từ thừa thường xuất hiện
    noise_words = ['ơi', 'này', 'đi', 'nha', 'nhé', 'giùm', 'cho tôi', 'hộ tôi', 'dùm', 'cái']
    for word in noise_words:
        text_lower = text_lower.replace(word, ' ')
    
    # Tìm match gần nhất
    for correct_cmd, variations in VOICE_CORRECTIONS.items():
        for variant in variations:
            if variant in text_lower:
                # Tìm thấy match → trả về lệnh chuẩn
                print(f"🔊 [Voice Normalize] '{text}' → detected '{correct_cmd}' (matched '{variant}')")
                return text_lower.replace(variant, correct_cmd)
    
    return text_lower

def fuzzy_match_music_command(text: str) -> tuple:
    """
    Fuzzy matching cho lệnh nhạc - tìm lệnh gần nhất ngay cả khi voice recognition sai.
    Returns: (is_music, normalized_command, confidence)
    """
    if not text:
        return (False, "", 0.0)
    
    text_lower = text.lower().strip()
    
    # Các pattern chính và độ tin cậy - ƯU TIÊN pause/stop TRƯỚC
    COMMAND_PATTERNS = {
        'pause': {
            'patterns': [
                # Tiếng Việt chuẩn
                'tạm dừng', 'dừng nhạc', 'dừng lại', 'ngưng nhạc', 'ngừng phát', 'nghỉ', 'pause',
                # Voice variants (ESP32 recognition)
                'tam dung', 'dung nhac', 'dung lai', 'ngung nhac', 'ngung phat', 
                'pao', 'pao nhac', 'poz', 'pốt', 'pos', 'pát', 'pát nhạc',
                # Biến thể
                'dừng đi', 'dừng bài', 'stop nhạc', 'tắt nhạc đi', 'tắt bài đi',
                'im đi', 'im lặng', 'yên đi', 'đừng phát', 'không phát nữa',
                # Ngắn gọn
                'dừng', 'ngừng', 'nghỉ'
            ],
            'action': 'pause'
        },
        'stop': {
            'patterns': [
                # Tiếng Việt chuẩn  
                'tắt nhạc', 'dừng hẳn', 'tắt hẳn', 'dừng hoàn toàn', 'stop', 'off nhạc',
                # Voice variants
                'tat nhac', 'dung han', 'tat han', 'stóp', 'sop', 'sốp',
                # Biến thể
                'tắt đi', 'tắt bài', 'đóng nhạc', 'hủy nhạc', 'không nghe nữa',
                'tắt', 'off'
            ],
            'action': 'stop'
        },
        'next': {
            'patterns': ['bài tiếp', 'tiếp theo', 'next', 'skip', 'chuyển bài', 'kế tiếp', 'bài khác', 'sang bài',
                        'bai tiep', 'tiep theo', 'bai diep', 'thiep theo', 'nex', 'nếch', 'bài sau'],
            'action': 'next'
        },
        'previous': {
            'patterns': ['bài trước', 'quay lại', 'previous', 'pre', 'lùi bài', 'bài cũ', 'trước đó',
                        'bai truoc', 'quay lai', 'bai chuoc', 'pri', 'prê'],
            'action': 'previous'
        },
        'play': {
            'patterns': ['phát nhạc', 'bật nhạc', 'mở nhạc', 'play', 'chơi nhạc', 'nghe nhạc',
                        'phat nhac', 'bat nhac', 'mo nhac', 'plây', 'tiếp tục', 'phát tiếp'],
            'action': 'play'
        },
        'volume_up': {
            'patterns': ['tăng âm lượng', 'to lên', 'tăng tiếng', 'volume up', 'tang am luong', 'to len'],
            'action': 'volume_up'
        },
        'volume_down': {
            'patterns': ['giảm âm lượng', 'nhỏ lại', 'giảm tiếng', 'volume down', 'giam am luong', 'nho lai'],
            'action': 'volume_down'
        },
        'shuffle': {
            'patterns': ['shuffle', 'trộn bài', 'ngẫu nhiên', 'random', 'sáp phồ', 'tron bai'],
            'action': 'shuffle'
        },
        'repeat': {
            'patterns': ['repeat', 'lặp lại', 'loop', 'ri pít', 'lap lai', 'lúp'],
            'action': 'repeat'
        }
    }
    
    best_match = None
    best_confidence = 0.0
    
    for cmd_type, cmd_info in COMMAND_PATTERNS.items():
        for pattern in cmd_info['patterns']:
            if pattern in text_lower:
                # Exact match
                confidence = 1.0
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = cmd_info['action']
                    
            # Fuzzy: check if most characters match
            elif len(pattern) >= 3:
                # Simple fuzzy: count matching chars
                matching = sum(1 for c in pattern if c in text_lower)
                ratio = matching / len(pattern)
                if ratio > 0.7:  # 70%+ match
                    confidence = ratio * 0.8  # Scale down fuzzy matches
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = cmd_info['action']
    
    is_music = best_match is not None and best_confidence > 0.5
    
    if is_music:
        print(f"🎯 [Fuzzy Match] '{text}' → action='{best_match}' (confidence={best_confidence:.2f})")
    
    return (is_music, best_match or "", best_confidence)

# Các từ khóa để nhận diện lệnh nhạc - QUAN TRỌNG: thêm nhiều biến thể pause/stop
MUSIC_KEYWORDS = [
    # Phát nhạc
    'phát nhạc', 'bật nhạc', 'mở nhạc', 'nghe nhạc', 'play music', 'chơi nhạc',
    'phát bài', 'bật bài', 'mở bài', 'nghe bài', 'play song',
    'phat nhac', 'bat nhac', 'mo nhac',
    
    # TẠM DỪNG - nhiều biến thể (QUAN TRỌNG!)
    'tạm dừng', 'pause', 'dừng nhạc', 'dừng lại', 'ngưng nhạc', 'ngừng phát',
    'tam dung', 'dung nhac', 'dung lai', 'ngung nhac',
    'pao', 'pao nhac', 'poz', 'pốt',
    'dừng', 'ngừng', 'nghỉ', 'im đi',
    
    # DỪNG HẲN/STOP
    'stop music', 'tắt nhạc', 'dừng hẳn', 'stop', 'off nhạc',
    'tat nhac', 'dung han', 'tắt đi', 'tắt bài',
    
    # Tiếp tục
    'tiếp tục', 'resume', 'phát tiếp', 'tiep tuc', 'phat tiep',
    
    # Bài tiếp/trước
    'bài tiếp', 'next', 'skip', 'chuyển bài', 'bài tiếp theo',
    'bai tiep', 'tiep theo',
    'bài trước', 'previous', 'quay lại bài', 'bai truoc', 'quay lai',
    
    # Âm lượng
    'âm lượng', 'volume', 'tăng tiếng', 'giảm tiếng', 'to lên', 'nhỏ lại',
    'tang am luong', 'giam am luong',
    
    # Trạng thái
    'đang phát gì', 'bài gì', 'đang nghe gì',
    
    # Shuffle/Repeat
    'trộn bài', 'shuffle', 'ngẫu nhiên', 'lặp lại', 'repeat', 'loop'
]

def is_music_command(text: str) -> bool:
    """
    Kiểm tra xem text có phải là lệnh điều khiển nhạc không.
    Dùng để LLM quyết định có nên gọi smart_music_control() hay không.
    
    Returns: True nếu là lệnh nhạc, False nếu không
    """
    text_lower = text.lower()
    
    # Loại trừ YouTube
    youtube_keywords = ['youtube', 'video', 'clip', 'xem phim']
    if any(yt in text_lower for yt in youtube_keywords):
        return False
    
    # Kiểm tra có keyword nhạc không
    return any(kw in text_lower for kw in MUSIC_KEYWORDS)

async def detect_and_execute_music(text: str) -> dict:
    """
    🎵🔍 TỰ ĐỘNG PHÁT HIỆN VÀ THỰC THI LỆNH NHẠC
    
    Tool này kiểm tra xem input có liên quan đến nhạc không và tự động thực hiện.
    Dùng khi KHÔNG CHẮC input có phải lệnh nhạc hay không.
    
    Args:
        text: Câu lệnh cần kiểm tra và thực thi
        
    Returns:
        dict với kết quả:
        - Nếu là lệnh nhạc: kết quả từ smart_music_control()
        - Nếu không: {"is_music_command": False, "message": "Không phải lệnh nhạc"}
    """
    if is_music_command(text):
        result = await smart_music_control(text)
        result["is_music_command"] = True
        return result
    else:
        return {
            "is_music_command": False,
            "message": "Không phải lệnh nhạc. Đây có thể là lệnh khác.",
            "hint": "Nếu bạn muốn điều khiển nhạc, hãy dùng các từ khóa như: phát nhạc, bài tiếp, dừng, âm lượng, v.v."
        }

async def smart_music_control(command: str) -> dict:
    """
    🎵 ĐIỀU KHIỂN NHẠC THÔNG MINH QUA PYTHON-VLC
    
    ⭐ LLM NÊN GỌI TOOL NÀY KHI USER NÓI VỀ NHẠC (không phải YouTube)
    
    Nhận lệnh tiếng Việt/Anh tự nhiên, tự động thực hiện:
    - Phát nhạc: "phát nhạc", "bật nhạc", "play music"
    - Phát bài cụ thể: "phát bài [tên]", "nghe [tên]"
    - Tạm dừng: "pause", "tạm dừng", "dừng nhạc"
    - Tiếp tục: "tiếp tục", "resume", "phát tiếp"
    - Bài tiếp: "bài tiếp", "next", "skip"
    - Bài trước: "bài trước", "previous", "quay lại"
    - Dừng hẳn: "stop", "tắt nhạc", "dừng hẳn"
    - Âm lượng: "volume 80", "tăng âm lượng", "giảm tiếng"
    - Shuffle: "trộn bài", "shuffle"
    - Repeat: "lặp lại", "repeat"
    
    🎯 TẤT CẢ ĐIỀU KHIỂN NHẠC LOCAL ĐỀU QUA PYTHON-VLC PLAYER
    
    📌 HỖ TRỢ FUZZY MATCHING: Nhận dạng cả khi voice recognition sai!
    """
    try:
        # BƯỚC 1: Normalize voice command (sửa lỗi nhận dạng phổ biến)
        cmd = normalize_voice_command(command)
        original_cmd = command.lower().strip()
        
        print(f"🎵 [Smart Music] Original: '{original_cmd}' → Normalized: '{cmd}'")
        
        # BƯỚC 2: Fuzzy match để tìm action nhanh
        is_music, fuzzy_action, confidence = fuzzy_match_music_command(cmd)
        
        # Kiểm tra nếu là lệnh YouTube → từ chối và gợi ý tool khác
        youtube_keywords = ['youtube', 'video', 'clip']
        if any(yt in cmd for yt in youtube_keywords):
            return {
                "success": False,
                "error": "Đây là lệnh YouTube, không phải nhạc local",
                "hint": "Dùng youtube_play_pause(), youtube_forward(), youtube_rewind() cho YouTube"
            }
        
        # Lấy trạng thái VLC hiện tại
        status = vlc_player.get_full_status() if vlc_player and vlc_player._player else {}
        is_playing = status.get('is_playing', False)
        current_track = status.get('current_track', '')
        has_playlist = bool(vlc_player._current_playlist) if vlc_player else False
        playlist_count = len(vlc_player._current_playlist) if vlc_player._current_playlist else 0
        current_idx = getattr(vlc_player, '_current_index', 0)
        
        # Log để debug
        print(f"🎵 [Smart Music] Playing: {is_playing}, Track: {current_track}, Index: {current_idx}/{playlist_count}, Fuzzy: {fuzzy_action}({confidence:.2f})")
        
        # BƯỚC 3: Nếu fuzzy match có confidence cao → thực hiện ngay
        if confidence >= 0.8:
            print(f"⚡ [Smart Music] High confidence fuzzy match: {fuzzy_action}")
            if fuzzy_action == 'next':
                if not has_playlist:
                    return {"success": False, "error": "Chưa có playlist. Hãy phát nhạc trước!"}
                return await music_next()
            elif fuzzy_action == 'previous':
                if not has_playlist:
                    return {"success": False, "error": "Chưa có playlist. Hãy phát nhạc trước!"}
                return await music_previous()
            elif fuzzy_action == 'pause':
                if is_playing:
                    return await pause_music()
                return {"success": True, "message": "⏸️ Nhạc đã đang tạm dừng rồi"}
            elif fuzzy_action == 'stop':
                return await stop_music()
            elif fuzzy_action == 'play':
                if not is_playing and has_playlist:
                    return await resume_music()
                elif not has_playlist:
                    return await list_music(auto_play=True)
                return {"success": True, "message": f"🎵 Đang phát: {current_track}"}
            elif fuzzy_action == 'volume_up':
                current_vol = vlc_player.get_volume() or 50
                return await music_volume(min(100, current_vol + 10))
            elif fuzzy_action == 'volume_down':
                current_vol = vlc_player.get_volume() or 50
                return await music_volume(max(0, current_vol - 10))
            elif fuzzy_action == 'shuffle':
                new_state = not vlc_player.get_shuffle()
                vlc_player.set_shuffle(new_state)
                return {"success": True, "message": f"🔀 Shuffle: {'Bật' if new_state else 'Tắt'}"}
            elif fuzzy_action == 'repeat':
                current_mode = vlc_player.get_repeat_mode()
                new_mode = (current_mode + 1) % 3
                vlc_player.set_repeat_mode(new_mode)
                mode_names = ['Tắt', 'Lặp tất cả', 'Lặp 1 bài']
                return {"success": True, "message": f"🔁 Repeat: {mode_names[new_mode]}"}
        
        # BƯỚC 4: Fallback - Pattern matching truyền thống
        # === 1. TẠM DỪNG (ưu tiên CAO nhất - dễ bị bỏ qua) ===
        pause_patterns = [
            # Tiếng Việt chuẩn
            'tạm dừng', 'dừng nhạc', 'dừng lại', 'ngưng nhạc', 'ngừng phát', 'pause',
            # Voice variants (ESP32)
            'tam dung', 'dung nhac', 'dung lai', 'ngung nhac', 'ngung phat',
            'pao', 'pao nhac', 'poz', 'pốt', 'pos', 'pát',
            # Biến thể ngắn
            'dừng', 'ngừng', 'nghỉ', 'im đi'
        ]
        if any(x in cmd for x in pause_patterns) and 'tiếp' not in cmd and 'hẳn' not in cmd:
            print(f"⏸️ [Smart Music] Matched PAUSE pattern in: '{cmd}'")
            if is_playing:
                return await pause_music()
            else:
                return {"success": True, "message": "⏸️ Nhạc đã đang tạm dừng rồi"}
        
        # === 2. DỪNG HẲN/STOP ===
        stop_patterns = [
            'tắt nhạc', 'dừng hẳn', 'tắt hẳn', 'stop', 'off nhạc', 'dừng hoàn toàn',
            'tat nhac', 'dung han', 'tat han', 'stóp', 'sop',
            'tắt đi', 'không nghe nữa', 'hủy nhạc'
        ]
        if any(x in cmd for x in stop_patterns):
            print(f"⏹️ [Smart Music] Matched STOP pattern in: '{cmd}'")
            return await stop_music()
        
        # === 3. BÀI TIẾP ===
        next_patterns = ['bài tiếp', 'tiếp theo', 'next', 'skip', 'chuyển bài', 'bài khác', 'kế tiếp', 'sang bài',
                        'bai tiep', 'tiep theo', 'nex', 'nếch', 'bài sau']
        if any(x in cmd for x in next_patterns):
            if not has_playlist:
                return {"success": False, "error": "Chưa có playlist. Hãy phát nhạc trước!"}
            return await music_next()
        
        # === 4. BÀI TRƯỚC ===
        prev_patterns = [
            'bài trước', 'bài trước đó', 'previous', 'quay lại bài', 'quay lại', 
            'back', 'lùi bài', 'bài cũ', 'phát lại bài trước', 'nghe lại bài trước',
            'trước đó', 'bài vừa rồi', 'pre', 'prev', 'lui', 'lui bai',
            'bai truoc', 'quay lai', 'bai chuoc', 'pri', 'prê'
        ]
        if any(x in cmd for x in prev_patterns):
            if not has_playlist:
                return {"success": False, "error": "Chưa có playlist. Hãy phát nhạc trước!"}
            print(f"⏮️ [Smart Music] Matched 'previous' pattern, calling music_previous()")
            result = await music_previous()
            print(f"⏮️ [Smart Music] Result: {result}")
            return result
        
        # === 5. TIẾP TỤC PHÁT ===
        resume_patterns = ['tiếp tục', 'resume', 'phát tiếp', 'chơi tiếp', 'play tiếp', 'mở lại', 'tiep tuc', 'phat tiep']
        if any(x in cmd for x in resume_patterns):
            if not is_playing and has_playlist:
                return await resume_music()
            elif is_playing:
                return {"success": True, "message": f"▶️ Đang phát: {current_track}"}
            else:
                return await list_music(auto_play=True)
        
        # === 6. PHÁT BÀI CỤ THỂ ===
        play_patterns = ['phát bài', 'play', 'mở bài', 'nghe bài', 'bật bài', 'tìm bài', 'tìm nhạc', 'phát nhạc', 'bật nhạc', 'mở nhạc']
        for pattern in play_patterns:
            if pattern in cmd:
                # Trích xuất tên bài
                song_name = cmd
                for p in play_patterns:
                    song_name = song_name.replace(p, '')
                song_name = song_name.strip()
                
                if song_name and len(song_name) > 1:
                    print(f"🎵 [Smart Music] Tìm và phát: '{song_name}'")
                    return await play_music(filename=song_name, create_playlist=True)
                else:
                    # Không có tên cụ thể
                    if is_playing:
                        return {"success": True, "message": f"🎵 Đang phát: {current_track}"}
                    elif has_playlist:
                        vlc_player.resume()
                        return {"success": True, "message": "▶️ Tiếp tục phát nhạc"}
                    else:
                        print(f"🎵 [Smart Music] Phát playlist mặc định")
                        return await list_music(auto_play=True)
        
        # === 7. ÂM LƯỢNG ===
        volume_patterns = ['âm lượng', 'volume', 'tiếng', 'sound']
        if any(x in cmd for x in volume_patterns):
            import re
            numbers = re.findall(r'\d+', cmd)
            if numbers:
                level = int(numbers[0])
                return await music_volume(level)
            elif any(x in cmd for x in ['tăng', 'to', 'lớn', 'up', 'cao']):
                current_vol = vlc_player.get_volume() or 50
                return await music_volume(min(100, current_vol + 10))
            elif any(x in cmd for x in ['giảm', 'nhỏ', 'bé', 'down', 'thấp']):
                current_vol = vlc_player.get_volume() or 50
                return await music_volume(max(0, current_vol - 10))
        
        # === 8. TRẠNG THÁI ===
        status_patterns = ['đang phát', 'bài gì', 'status', 'trạng thái', 'đang nghe']
        if any(x in cmd for x in status_patterns):
            return await get_music_status()
        
        # === 9. SHUFFLE ===
        shuffle_patterns = ['ngẫu nhiên', 'shuffle', 'random', 'trộn']
        if any(x in cmd for x in shuffle_patterns):
            new_state = not vlc_player.get_shuffle()
            vlc_player.set_shuffle(new_state)
            return {"success": True, "message": f"🔀 Shuffle: {'Bật' if new_state else 'Tắt'}"}
        
        # === 10. LẶP LẠI ===
        repeat_patterns = ['lặp lại', 'repeat', 'loop']
        if any(x in cmd for x in repeat_patterns):
            current_mode = vlc_player.get_repeat_mode()
            new_mode = (current_mode + 1) % 3
            vlc_player.set_repeat_mode(new_mode)
            modes = ['Tắt', 'Lặp tất cả', 'Lặp 1 bài']
            return {"success": True, "message": f"🔁 Repeat: {modes[new_mode]}"}
        
        # === KHÔNG NHẬN DIỆN ĐƯỢC ===
        return {
            "success": False, 
            "error": f"Không hiểu lệnh nhạc: '{command}'",
            "hint": "Thử nói: 'phát bài [tên]', 'bài tiếp', 'tạm dừng', 'âm lượng 80'",
            "current_status": {
                "is_playing": is_playing,
                "current_track": current_track,
                "has_playlist": has_playlist
            }
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

async def music_next() -> dict:
    """Chuyển bài tiếp theo trong playlist (VLC Player) - NHANH!"""
    try:
        if vlc_player and vlc_player._player:
            success = vlc_player.next_track()
            if success:
                import time
                time.sleep(0.5)  # Đợi VLC load media mới
                status = vlc_player.get_full_status()
                current_song = status.get('current_track') or 'Unknown'
                # Fallback: lấy từ playlist nếu có
                if current_song == 'Unknown' or current_song is None:
                    idx = vlc_player.get_playlist_index()
                    if vlc_player._current_playlist and 0 <= idx < len(vlc_player._current_playlist):
                        current_song = Path(vlc_player._current_playlist[idx]).name
                return {
                    "success": True, 
                    "message": f"⏭️ Đã chuyển: {current_song} (Python-VLC)",
                    "player": "Python-VLC",
                    "current_song": current_song,
                    "llm_note": "🎵 Đang dùng Python-VLC. Tiếp tục dùng music_next()/music_previous() để chuyển bài."
                }
            return {"success": False, "error": "Không có bài tiếp theo trong playlist"}
        return {"success": False, "error": "VLC Player chưa khởi tạo. Dùng play_music() trước!"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def music_previous() -> dict:
    """Quay lại bài trước trong playlist (VLC Player) - NHANH!"""
    try:
        if vlc_player and vlc_player._player:
            success = vlc_player.previous_track()
            if success:
                import time
                time.sleep(0.5)  # Đợi VLC load media mới
                status = vlc_player.get_full_status()
                current_song = status.get('current_track') or 'Unknown'
                # Fallback: lấy từ playlist nếu có
                if current_song == 'Unknown' or current_song is None:
                    idx = vlc_player.get_playlist_index()
                    if vlc_player._current_playlist and 0 <= idx < len(vlc_player._current_playlist):
                        current_song = Path(vlc_player._current_playlist[idx]).name
                return {
                    "success": True, 
                    "message": f"⏮️ Đã quay lại: {current_song} (Python-VLC)",
                    "player": "Python-VLC",
                    "current_song": current_song,
                    "llm_note": "🎵 Đang dùng Python-VLC. Tiếp tục dùng music_next()/music_previous() để chuyển bài."
                }
            return {"success": False, "error": "Không có bài trước trong playlist"}
        return {"success": False, "error": "VLC Player chưa khởi tạo. Dùng play_music() trước!"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_music_status() -> dict:
    """Lấy trạng thái đầy đủ VLC player cho Web UI real-time sync"""
    try:
        status = vlc_player.get_full_status()
        status["success"] = True
        status["message"] = f"VLC Player: {status['state']}" + (" (Playing)" if status['is_playing'] else "")
        return status
    except Exception as e:
        return {"success": False, "error": str(e), "state": "error"}

async def seek_music(percentage: float) -> dict:
    """Chuyển đến vị trí cụ thể trong bài nhạc (0-100%)"""
    try:
        # Kiểm tra có nhạc đang phát không
        if not vlc_player._player:
            return {"success": False, "error": "VLC Player chưa khởi tạo"}
        
        # Check trạng thái phát
        state = vlc_player._player.get_state()
        if state not in [vlc_player._vlc.State.Playing, vlc_player._vlc.State.Paused]:
            return {"success": False, "error": "Không có nhạc đang phát hoặc tạm dừng"}
        
        # Chuyển percentage sang giá trị 0.0 - 1.0
        position = max(0.0, min(1.0, percentage / 100.0))
        
        # Dùng method set_position của VLCMusicPlayer
        result = vlc_player.set_position(position)
        
        if result:
            return {
                "success": True,
                "message": f"Đã chuyển đến {percentage:.1f}% của bài hát",
                "position": position
            }
        else:
            return {"success": False, "error": "Không thể seek"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def music_volume(level: int) -> dict:
    """Điều chỉnh âm lượng VLC Player (0-100)"""
    try:
        if not vlc_player.player:
            return {"success": False, "error": "VLC Player chưa khởi tạo"}
        
        # VLC volume range: 0-100 (có thể lên tới 200 nhưng sẽ méo tiếng)
        volume = max(0, min(100, level))
        vlc_player.player.audio_set_volume(volume)
        
        icon = "🔇" if volume == 0 else ("🔈" if volume < 30 else ("🔉" if volume < 70 else "🔊"))
        
        return {
            "success": True,
            "volume": volume,
            "message": f"{icon} Âm lượng: {volume}%"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def check_music_folder_config() -> dict:
    """Kiểm tra xem đã có config thư mục nhạc chưa"""
    try:
        import json
        import os
        from pathlib import Path
        
        config_file = Path(os.path.expanduser("~")) / "AppData" / "Local" / "miniZ_MCP" / "music_folder_config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return {
                "has_config": True,
                "folder_path": config.get('folder_path', ''),
                "timestamp": config.get('timestamp', '')
            }
        return {"has_config": False}
    except:
        return {"has_config": False}

async def save_music_folder_config(folder_path: str) -> dict:
    """Lưu cấu hình đường dẫn thư mục nhạc người dùng"""
    try:
        import json
        import os
        from pathlib import Path
        
        config_file = Path(os.path.expanduser("~")) / "AppData" / "Local" / "miniZ_MCP" / "music_folder_config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config = {
            "folder_path": folder_path,
            "timestamp": str(datetime.now())
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"⚙️ [Music Config] Saved: {folder_path}")
        return {
            "success": True,
            "message": f"Đã lưu cài đặt thư mục nhạc: {folder_path}",
            "folder_path": folder_path
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def play_music_from_user_folder(filename: str = "", auto_play: bool = True) -> dict:
    """Phát nhạc từ thư mục người dùng đã cấu hình bằng Python-VLC (không dùng trình phát mặc định)"""
    try:
        import json
        from pathlib import Path
        
        # Đọc config
        config_file = Path(os.path.expanduser("~")) / "AppData" / "Local" / "miniZ_MCP" / "music_folder_config.json"
        if not config_file.exists():
            return {
                "success": False, 
                "error": "Chưa cấu hình thư mục nhạc. Vui lòng vào Music Settings để thiết lập."
            }
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        folder_path = Path(config['folder_path'])
        if not folder_path.exists():
            return {
                "success": False,
                "error": f"Thư mục không tồn tại: {folder_path}"
            }
        
        # Tìm file nhạc
        music_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.wma', '.aac', '.ogg']
        music_files = []
        
        for ext in music_extensions:
            music_files.extend(list(folder_path.glob(f"**/*{ext}")))
        
        if not music_files:
            return {
                "success": False,
                "error": f"Không tìm thấy file nhạc trong: {folder_path}"
            }
        
        # Nếu có filename cụ thể, tìm file đó
        if filename:
            filename_lower = filename.lower()
            matching_files = [f for f in music_files if filename_lower in f.name.lower()]
            if matching_files:
                target_file = matching_files[0]
            else:
                return {
                    "success": False,
                    "error": f"Không tìm thấy '{filename}' trong thư mục"
                }
        else:
            # Phát file đầu tiên
            target_file = music_files[0]
        
        # 🎵 PHÁT BẰNG PYTHON-VLC (thay vì trình phát mặc định)
        # Tạo playlist với tất cả bài trong thư mục
        all_songs = sorted([str(f) for f in music_files])
        
        # Đảm bảo bài hiện tại ở đầu playlist
        if str(target_file) in all_songs:
            all_songs.remove(str(target_file))
        all_songs.insert(0, str(target_file))
        
        success = vlc_player.play_playlist(all_songs)
        
        if success:
            message = f"🎵 Đang phát '{target_file.name}' (VLC Player)"
            print(f"🎵 [User Music VLC] {message}")
            return {
                "success": True,
                "message": message,
                "file_path": str(target_file),
                "total_files": len(music_files),
                "playlist_count": len(all_songs),
                "player": "VLC (Python-VLC)"
            }
        else:
            return {"success": False, "error": "VLC Player không thể phát file"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

async def search_music(keyword: str, auto_play: bool = True) -> dict:
    """
    Tìm kiếm nhạc theo từ khóa và TỰ ĐỘNG PHÁT bài đầu tiên.
    Set auto_play=False để chỉ tìm kiếm không phát.
    """
    try:
        if not MUSIC_LIBRARY.exists():
            return {"success": False, "error": "Thư mục music_library không tồn tại"}
        
        keyword_lower = keyword.lower()
        music_files = []
        
        for file_path in MUSIC_LIBRARY.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in MUSIC_EXTENSIONS:
                if keyword_lower in file_path.name.lower():
                    relative_path = file_path.relative_to(MUSIC_LIBRARY)
                    music_files.append({
                        "filename": file_path.name,
                        "path": str(relative_path).replace('\\', '/'),
                        "size_mb": round(file_path.stat().st_size / (1024**2), 2),
                        "extension": file_path.suffix.lower()
                    })
        
        music_files.sort(key=lambda x: x['filename'])
        
        if len(music_files) == 0:
            return {
                "success": False,
                "error": f"Không tìm thấy bài hát nào với từ khóa '{keyword}'"
            }
        
        # 🎵 AUTO-PLAY: Tự động phát bài đầu tiên
        first_file = music_files[0]['filename']
        play_result = None
        
        if auto_play:
            print(f"🔍 [Search Music] Tìm thấy '{keyword}', tự động phát: {first_file}")
            play_result = await play_music(first_file)
            
            if play_result.get("success"):
                message = f"✅ Found & playing: {first_file}\nTotal {len(music_files)} match(es) for '{keyword}'"
            else:
                message = f"❌ Found {len(music_files)} songs but failed to play: {play_result.get('error', 'Unknown error')}"
        else:
            message = f"Tìm thấy {len(music_files)} kết quả cho '{keyword}'"
        
        return {
            "success": True,
            "files": music_files,
            "count": len(music_files),
            "keyword": keyword,
            "message": message,
            "auto_played": auto_play,
            "play_result": play_result if auto_play else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================
# QUICK WEBSITE ACCESS TOOLS
# ============================================================

async def open_youtube(search_query: str = "") -> dict:
    """Mở YouTube với từ khóa tìm kiếm (nếu có)"""
    try:
        import webbrowser
        if search_query:
            url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
            message = f"Đã mở YouTube với tìm kiếm: '{search_query}'"
        else:
            url = "https://www.youtube.com"
            message = "Đã mở YouTube"
        webbrowser.open(url)
        return {"success": True, "message": message, "url": url}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def search_youtube_video(video_title: str, auto_open: bool = True) -> dict:
    """Tìm kiếm video YouTube chính xác theo tên và mở video đó
    
    Args:
        video_title: Tên video cần tìm (có thể là tên chính xác hoặc từ khóa)
        auto_open: Tự động mở video trong browser (default: True)
    
    Returns:
        dict với thông tin video: title, link, channel, views, duration
    """
    try:
        from youtubesearchpython import VideosSearch
        import webbrowser
        
        print(f"🔍 [YouTube Search] Đang tìm kiếm: '{video_title}'")
        
        # Tìm kiếm video
        search = VideosSearch(video_title, limit=5)
        results = search.result()
        
        if not results or not results.get('result'):
            return {
                "success": False,
                "error": f"Không tìm thấy video nào với tên: '{video_title}'"
            }
        
        # Lấy video đầu tiên (khớp nhất)
        top_video = results['result'][0]
        video_id = top_video['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        result = {
            "success": True,
            "title": top_video['title'],
            "url": video_url,
            "channel": top_video['channel']['name'],
            "duration": top_video['duration'],
            "views": top_video.get('viewCount', {}).get('text', 'N/A'),
            "thumbnail": top_video['thumbnails'][0]['url'] if top_video.get('thumbnails') else None,
            "published_time": top_video.get('publishedTime', 'N/A')
        }
        
        # Thêm top 5 kết quả để user có thể chọn
        result['top_5_results'] = [
            {
                "title": vid['title'],
                "url": f"https://www.youtube.com/watch?v={vid['id']}",
                "channel": vid['channel']['name'],
                "duration": vid['duration']
            }
            for vid in results['result'][:5]
        ]
        
        if auto_open:
            webbrowser.open(video_url)
            result['message'] = f"✅ Đã mở video: {top_video['title']}"
            print(f"✅ [YouTube] Đã mở: {top_video['title']}")
        else:
            result['message'] = f"✅ Đã tìm thấy video: {top_video['title']}"
            print(f"✅ [YouTube] Tìm thấy: {top_video['title']}")
        
        return result
        
    except ImportError:
        return {
            "success": False,
            "error": "Thiếu thư viện 'youtube-search-python'. Cài đặt: pip install youtube-search-python"
        }
    except Exception as e:
        print(f"❌ [YouTube Search] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

# ============================================================
# BROWSER AUTOMATION TOOLS
# ============================================================

async def browser_open_url(url: str) -> dict:
    """Mở URL trong browser được điều khiển (Selenium)"""
    return browser_controller.open_url(url)

async def browser_get_info() -> dict:
    """Lấy thông tin trang hiện tại"""
    return browser_controller.get_current_info()

async def browser_click(selector: str, by: str = "css") -> dict:
    """Click vào element trên trang web
    
    Args:
        selector: CSS selector, XPath, ID, etc.
        by: Loại selector ('css', 'xpath', 'id', 'name', 'class', 'tag')
    """
    return browser_controller.click_element(selector, by)

async def browser_fill_input(selector: str, text: str, by: str = "css") -> dict:
    """Điền text vào input field
    
    Args:
        selector: CSS selector, XPath, ID, etc.
        text: Text cần điền
        by: Loại selector ('css', 'xpath', 'id', 'name', 'class')
    """
    return browser_controller.fill_input(selector, text, by)

async def browser_scroll(direction: str = "down", amount: int = 500) -> dict:
    """Cuộn trang
    
    Args:
        direction: 'down', 'up', 'top', 'bottom'
        amount: Số pixel cuộn (nếu direction là down/up)
    """
    return browser_controller.scroll(direction, amount)

async def browser_back() -> dict:
    """Quay lại trang trước"""
    return browser_controller.go_back()

async def browser_forward() -> dict:
    """Tiến tới trang sau"""
    return browser_controller.go_forward()

async def browser_refresh() -> dict:
    """Làm mới trang"""
    return browser_controller.refresh()

async def browser_screenshot(filepath: str = None) -> dict:
    """Chụp screenshot trang hiện tại
    
    Args:
        filepath: Đường dẫn lưu file (tùy chọn, mặc định: screenshot_YYYYMMDD_HHMMSS.png)
    """
    return browser_controller.screenshot(filepath)

async def browser_new_tab(url: str = None) -> dict:
    """Mở tab mới
    
    Args:
        url: URL cần mở trong tab mới (tùy chọn)
    """
    return browser_controller.new_tab(url)

async def browser_close_tab() -> dict:
    """Đóng tab hiện tại"""
    return browser_controller.close_tab()

async def browser_execute_js(script: str) -> dict:
    """Thực thi JavaScript code trên trang
    
    Args:
        script: JavaScript code cần chạy
    """
    return browser_controller.execute_script(script)

async def browser_close() -> dict:
    """Đóng browser hoàn toàn"""
    return browser_controller.close_browser()

async def open_facebook() -> dict:
    """Mở Facebook"""
    try:
        import webbrowser
        url = "https://www.facebook.com"
        webbrowser.open(url)
        return {"success": True, "message": "Đã mở Facebook", "url": url}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def open_google(search_query: str = "") -> dict:
    """Mở Google với từ khóa tìm kiếm (nếu có)"""
    try:
        import webbrowser
        if search_query:
            url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            message = f"Đã mở Google với tìm kiếm: '{search_query}'"
        else:
            url = "https://www.google.com"
            message = "Đã mở Google"
        webbrowser.open(url)
        return {"success": True, "message": message, "url": url}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def open_tiktok() -> dict:
    """Mở TikTok"""
    try:
        import webbrowser
        url = "https://www.tiktok.com"
        webbrowser.open(url)
        return {"success": True, "message": "Đã mở TikTok", "url": url}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def open_website(url: str) -> dict:
    """Mở trang web tùy chỉnh"""
    try:
        import webbrowser
        # Thêm https:// nếu chưa có
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        webbrowser.open(url)
        return {"success": True, "message": f"Đã mở trang web: {url}", "url": url}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================
# YOUTUBE PLAYER CONTROL TOOLS
# ============================================================

async def control_youtube(action: str) -> dict:
    """
    Điều khiển YouTube player bằng keyboard shortcuts.
    Phải có cửa sổ YouTube đang active/focused.
    """
    try:
        import pyautogui
        import time

        # Định nghĩa các actions và keyboard shortcuts tương ứng
        shortcuts = {
            # Video control
            "play_pause": "k",  # K hoặc Space - Tạm dừng / Tiếp tục
            "rewind_10": "j",   # J - Lùi lại 10 giây
            "forward_10": "l",  # L - Tiến tới 10 giây
            "rewind_5": "left", # ← - Lùi lại 5 giây
            "forward_5": "right", # → - Tiến tới 5 giây
            "beginning": "home", # 0 hoặc Home - Quay về đầu video
            "end": "end",       # End - Tua đến cuối video
            "frame_back": ",",  # , - Lùi lại 1 khung hình
            "frame_forward": ".", # . - Tiến tới 1 khung hình

            # Volume control
            "volume_up": "up",    # ↑ - Tăng âm lượng 5%
            "volume_down": "down", # ↓ - Giảm âm lượng 5%
            "mute_toggle": "m",   # M - Bật / Tắt tiếng
        }

        if action not in shortcuts:
            available_actions = ", ".join(shortcuts.keys())
            return {
                "success": False,
                "error": f"Action không hợp lệ: {action}. Các actions có sẵn: {available_actions}"
            }

        key = shortcuts[action]

        # Đợi một chút để đảm bảo YouTube player đang active
        time.sleep(0.5)

        # Gửi keyboard shortcut
        if key in ["left", "right", "up", "down", "home", "end"]:
            pyautogui.press(key)
        else:
            pyautogui.press(key)

        # Mô tả action cho user
        action_descriptions = {
            "play_pause": "Tạm dừng / Tiếp tục video",
            "rewind_10": "Lùi lại 10 giây",
            "forward_10": "Tiến tới 10 giây",
            "rewind_5": "Lùi lại 5 giây",
            "forward_5": "Tiến tới 5 giây",
            "beginning": "Quay về đầu video",
            "end": "Tua đến cuối video",
            "frame_back": "Lùi lại 1 khung hình",
            "frame_forward": "Tiến tới 1 khung hình",
            "volume_up": "Tăng âm lượng 5%",
            "volume_down": "Giảm âm lượng 5%",
            "mute_toggle": "Bật / Tắt tiếng",
        }

        description = action_descriptions.get(action, action)

        return {
            "success": True,
            "message": f"✅ Đã thực hiện: {description}",
            "action": action,
            "key_pressed": key,
            "note": "Đảm bảo cửa sổ YouTube đang active/focused để lệnh có hiệu lực"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "note": "Có thể cần cài đặt pyautogui hoặc cửa sổ YouTube chưa active"
        }


async def youtube_play_pause() -> dict:
    """Play/Pause YouTube video đang phát. Cần browser có YouTube đang focus."""
    return await control_youtube("play_pause")

async def youtube_rewind(seconds: int = 10) -> dict:
    """Tua lùi YouTube video. Mặc định 10 giây."""
    if seconds >= 10:
        return await control_youtube("rewind_10")
    else:
        return await control_youtube("rewind_5")

async def youtube_forward(seconds: int = 10) -> dict:
    """Tua tới YouTube video. Mặc định 10 giây."""
    if seconds >= 10:
        return await control_youtube("forward_10")
    else:
        return await control_youtube("forward_5")

async def youtube_volume_up() -> dict:
    """Tăng âm lượng YouTube 5%."""
    return await control_youtube("volume_up")

async def youtube_volume_down() -> dict:
    """Giảm âm lượng YouTube 5%."""
    return await control_youtube("volume_down")

async def youtube_mute() -> dict:
    """Bật/Tắt tiếng YouTube."""
    return await control_youtube("mute_toggle")

async def youtube_fullscreen() -> dict:
    """Bật/Tắt chế độ toàn màn hình YouTube (phím F)."""
    try:
        import pyautogui
        import time
        time.sleep(0.3)
        pyautogui.press('f')
        return {"success": True, "message": "✅ Đã bật/tắt fullscreen YouTube"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def youtube_captions() -> dict:
    """Bật/Tắt phụ đề YouTube (phím C)."""
    try:
        import pyautogui
        import time
        time.sleep(0.3)
        pyautogui.press('c')
        return {"success": True, "message": "✅ Đã bật/tắt phụ đề YouTube"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def youtube_speed(speed: str = "normal") -> dict:
    """
    Thay đổi tốc độ phát YouTube.
    speed: 'slower' (chậm hơn) hoặc 'faster' (nhanh hơn) hoặc 'normal' (bình thường)
    """
    try:
        import pyautogui
        import time
        time.sleep(0.3)
        if speed == "slower":
            pyautogui.hotkey('shift', ',')  # Shift + < = chậm hơn
            return {"success": True, "message": "✅ Đã giảm tốc độ YouTube"}
        elif speed == "faster":
            pyautogui.hotkey('shift', '.')  # Shift + > = nhanh hơn
            return {"success": True, "message": "✅ Đã tăng tốc độ YouTube"}
        else:
            # Reset về tốc độ bình thường - không có phím tắt trực tiếp
            return {"success": True, "message": "⚠️ Để reset về tốc độ bình thường, nhấn nhiều lần Shift+< hoặc dùng menu Settings"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# VLC PLAYER CONTROL TOOLS
# ============================================================

async def control_vlc(action: str) -> dict:
    """
    Điều khiển VLC Player bằng keyboard shortcuts.
    Cần VLC đang chạy và có focus.
    """
    try:
        import pyautogui
        import time
        
        shortcuts = {
            "play_pause": "space",      # Space - Play/Pause
            "stop": "s",                # S - Stop
            "next": "n",                # N - Next
            "previous": "p",            # P - Previous
            "volume_up": "ctrl+up",     # Ctrl+↑ - Tăng âm lượng
            "volume_down": "ctrl+down", # Ctrl+↓ - Giảm âm lượng
            "mute": "m",                # M - Mute
            "fullscreen": "f",          # F - Fullscreen
            "forward_short": "shift+right",  # Shift+→ - Tua tới 3 giây
            "backward_short": "shift+left",  # Shift+← - Tua lùi 3 giây
            "forward_medium": "alt+right",   # Alt+→ - Tua tới 10 giây
            "backward_medium": "alt+left",   # Alt+← - Tua lùi 10 giây
            "forward_long": "ctrl+right",    # Ctrl+→ - Tua tới 1 phút
            "backward_long": "ctrl+left",    # Ctrl+← - Tua lùi 1 phút
            "faster": "]",              # ] - Nhanh hơn
            "slower": "[",              # [ - Chậm hơn
            "normal_speed": "=",        # = - Tốc độ bình thường
            "loop": "l",                # L - Loop
            "random": "r",              # R - Random/Shuffle
        }
        
        if action not in shortcuts:
            return {
                "success": False,
                "error": f"Action không hợp lệ: {action}",
                "available_actions": list(shortcuts.keys())
            }
        
        time.sleep(0.3)
        key = shortcuts[action]
        
        if "+" in key:
            parts = key.split("+")
            pyautogui.hotkey(*parts)
        else:
            pyautogui.press(key)
        
        descriptions = {
            "play_pause": "Play/Pause",
            "stop": "Dừng phát",
            "next": "Bài tiếp theo",
            "previous": "Bài trước",
            "volume_up": "Tăng âm lượng",
            "volume_down": "Giảm âm lượng",
            "mute": "Bật/Tắt tiếng",
            "fullscreen": "Toàn màn hình",
            "forward_short": "Tua tới 3 giây",
            "backward_short": "Tua lùi 3 giây",
            "forward_medium": "Tua tới 10 giây",
            "backward_medium": "Tua lùi 10 giây",
            "forward_long": "Tua tới 1 phút",
            "backward_long": "Tua lùi 1 phút",
            "faster": "Tăng tốc độ phát",
            "slower": "Giảm tốc độ phát",
            "normal_speed": "Tốc độ bình thường",
            "loop": "Lặp lại",
            "random": "Phát ngẫu nhiên",
        }
        
        return {
            "success": True,
            "message": f"✅ VLC: {descriptions.get(action, action)}",
            "action": action
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def vlc_play_pause() -> dict:
    """Play/Pause VLC."""
    return await control_vlc("play_pause")

async def vlc_stop() -> dict:
    """Dừng phát VLC."""
    return await control_vlc("stop")

async def vlc_next() -> dict:
    """Chuyển bài tiếp theo trong VLC."""
    return await control_vlc("next")

async def vlc_previous() -> dict:
    """Quay lại bài trước trong VLC."""
    return await control_vlc("previous")

async def vlc_volume_up() -> dict:
    """Tăng âm lượng VLC."""
    return await control_vlc("volume_up")

async def vlc_volume_down() -> dict:
    """Giảm âm lượng VLC."""
    return await control_vlc("volume_down")

async def vlc_mute() -> dict:
    """Bật/Tắt tiếng VLC."""
    return await control_vlc("mute")

async def vlc_forward(seconds: int = 10) -> dict:
    """Tua tới trong VLC. 3s/10s/60s tùy theo seconds."""
    if seconds <= 5:
        return await control_vlc("forward_short")
    elif seconds <= 30:
        return await control_vlc("forward_medium")
    else:
        return await control_vlc("forward_long")

async def vlc_backward(seconds: int = 10) -> dict:
    """Tua lùi trong VLC. 3s/10s/60s tùy theo seconds."""
    if seconds <= 5:
        return await control_vlc("backward_short")
    elif seconds <= 30:
        return await control_vlc("backward_medium")
    else:
        return await control_vlc("backward_long")


# ============================================================
# WINDOWS MEDIA PLAYER CONTROL TOOLS
# ============================================================

async def control_wmp(action: str) -> dict:
    """
    Điều khiển Windows Media Player bằng keyboard shortcuts.
    Cần WMP đang chạy và có focus.
    """
    try:
        import pyautogui
        import time
        
        shortcuts = {
            "play_pause": "ctrl+p",     # Ctrl+P - Play/Pause
            "stop": "ctrl+s",           # Ctrl+S - Stop (có thể conflict với Save)
            "next": "ctrl+f",           # Ctrl+F - Next
            "previous": "ctrl+b",       # Ctrl+B - Previous
            "volume_up": "f10",         # F10 - Tăng âm lượng
            "volume_down": "f9",        # F9 - Giảm âm lượng
            "mute": "f8",               # F8 - Mute
            "fullscreen": "alt+enter",  # Alt+Enter - Fullscreen
            "forward": "ctrl+shift+f",  # Ctrl+Shift+F - Fast forward
            "backward": "ctrl+shift+b", # Ctrl+Shift+B - Rewind
        }
        
        if action not in shortcuts:
            return {
                "success": False,
                "error": f"Action không hợp lệ: {action}",
                "available_actions": list(shortcuts.keys())
            }
        
        time.sleep(0.3)
        key = shortcuts[action]
        
        if "+" in key:
            parts = key.split("+")
            pyautogui.hotkey(*parts)
        else:
            pyautogui.press(key)
        
        descriptions = {
            "play_pause": "Play/Pause",
            "stop": "Dừng phát",
            "next": "Bài tiếp theo",
            "previous": "Bài trước",
            "volume_up": "Tăng âm lượng",
            "volume_down": "Giảm âm lượng",
            "mute": "Bật/Tắt tiếng",
            "fullscreen": "Toàn màn hình",
            "forward": "Tua tới",
            "backward": "Tua lùi",
        }
        
        return {
            "success": True,
            "message": f"✅ Windows Media Player: {descriptions.get(action, action)}",
            "action": action
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def wmp_play_pause() -> dict:
    """Play/Pause Windows Media Player."""
    return await control_wmp("play_pause")

async def wmp_stop() -> dict:
    """Dừng phát Windows Media Player."""
    return await control_wmp("stop")

async def wmp_next() -> dict:
    """Chuyển bài tiếp theo trong Windows Media Player."""
    return await control_wmp("next")

async def wmp_previous() -> dict:
    """Quay lại bài trước trong Windows Media Player."""
    return await control_wmp("previous")

async def wmp_volume_up() -> dict:
    """Tăng âm lượng Windows Media Player."""
    return await control_wmp("volume_up")

async def wmp_volume_down() -> dict:
    """Giảm âm lượng Windows Media Player."""
    return await control_wmp("volume_down")

async def wmp_mute() -> dict:
    """Bật/Tắt tiếng Windows Media Player."""
    return await control_wmp("mute")


# ============================================================
# SMART MEDIA CONTROL - Tự động nhận diện player đang chạy
# ============================================================

async def smart_media_control(action: str) -> dict:
    """
    Điều khiển media thông minh.
    ⭐ ƯU TIÊN PYTHON-VLC TRƯỚC - nhanh nhất!
    Sau đó mới tới: Spotify > VLC Window > WMP > YouTube
    
    Actions: play_pause, stop, next, previous, volume_up, volume_down, mute
    """
    try:
        import time
        
        # 🎵 ƯU TIÊN 1: PYTHON-VLC NỘI BỘ - NHANH NHẤT!
        if vlc_player and vlc_player._player:
            action_map = {
                "play_pause": lambda: vlc_player.pause(),
                "stop": lambda: vlc_player.stop(),
                "next": lambda: (vlc_player._list_player.next(), time.sleep(0.3), vlc_player._list_player.play() if not vlc_player.is_playing() else None),
                "previous": lambda: (vlc_player._list_player.previous(), time.sleep(0.3), vlc_player._list_player.play() if not vlc_player.is_playing() else None),
                "volume_up": lambda: vlc_player._player.audio_set_volume(min(100, vlc_player._player.audio_get_volume() + 10)),
                "volume_down": lambda: vlc_player._player.audio_set_volume(max(0, vlc_player._player.audio_get_volume() - 10)),
                "mute": lambda: vlc_player._player.audio_toggle_mute()
            }
            
            if action in action_map:
                action_map[action]()
                status = vlc_player.get_full_status()
                return {
                    "success": True,
                    "message": f"✅ {action}: {status.get('current_song', 'VLC Player')}",
                    "player": "Python-VLC",
                    "current_song": status.get('current_song'),
                    "is_playing": vlc_player.is_playing(),
                    "llm_note": "🎵 Đang dùng Python-VLC. Tiếp tục dùng các lệnh nhạc VLC!"
                }
        
        # 2. Fallback: Dùng media keys cho external players
        import psutil
        import pyautogui
        
        running_players = []
        for proc in psutil.process_iter(['name']):
            name = proc.info['name'].lower()
            if 'spotify' in name:
                running_players.append('spotify')
            elif 'vlc' in name:
                running_players.append('vlc_external')
            elif 'wmplayer' in name:
                running_players.append('wmp')
            elif 'chrome' in name or 'firefox' in name or 'msedge' in name:
                running_players.append('browser')
        
        player = None
        if 'spotify' in running_players:
            player = 'spotify'
        elif 'vlc_external' in running_players:
            player = 'vlc_external'
        elif 'wmp' in running_players:
            player = 'wmp'
        elif 'browser' in running_players:
            player = 'browser'
        
        if not player:
            return {
                "success": False,
                "error": "Không có Python-VLC đang phát và không phát hiện media player nào",
                "hint": "Dùng play_music() để phát nhạc bằng Python-VLC trước!"
            }
        
        media_keys = {
            "play_pause": "playpause",
            "stop": "stop",
            "next": "nexttrack",
            "previous": "prevtrack",
            "volume_up": "volumeup",
            "volume_down": "volumedown",
            "mute": "volumemute"
        }
        
        if action in media_keys:
            time.sleep(0.2)
            pyautogui.press(media_keys[action])
            return {
                "success": True,
                "message": f"✅ Đã gửi lệnh {action} tới {player}",
                "player": player,
                "action": action
            }
        
        return {"success": False, "error": f"Action '{action}' không hợp lệ"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# NEW TOOLS FROM XIAOZHI-MCPTOOLS REFERENCE
# ============================================================

async def lock_computer() -> dict:
    """Khóa máy tính ngay lập tức"""
    try:
        subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True, check=True)
        return {"success": True, "message": "Máy tính đã được khóa"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def shutdown_schedule(action: str, delay: int = 0) -> dict:
    """
    Lên lịch tắt máy/khởi động lại
    action: 'shutdown', 'restart', 'cancel'
    delay: thời gian trì hoãn (giây)
    """
    try:
        action_map = {"shutdown": "/s", "restart": "/r", "cancel": "/a"}
        if action not in action_map:
            return {"success": False, "error": f"Action không hợp lệ: {action}"}
        
        if action == "cancel":
            subprocess.run("shutdown /a", shell=True, check=True)
            return {"success": True, "message": "Đã hủy lịch tắt máy"}
        else:
            subprocess.run(f"shutdown {action_map[action]} /t {delay}", shell=True, check=True)
            return {"success": True, "message": f"Đã lên lịch {action} sau {delay} giây"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def show_desktop() -> dict:
    """Hiển thị desktop (Win+D)"""
    try:
        import pyautogui
        pyautogui.hotkey('win', 'd')
        return {"success": True, "message": "Đã hiển thị desktop"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def undo_operation() -> dict:
    """Hoàn tác thao tác cuối (Ctrl+Z)"""
    try:
        import pyautogui
        pyautogui.hotkey('ctrl', 'z')
        return {"success": True, "message": "Đã thực hiện hoàn tác"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def set_theme(dark_mode: bool = True) -> dict:
    """Đổi theme Windows sáng/tối. Nếu dark_mode=None thì toggle"""
    try:
        import winreg
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        
        # Nếu dark_mode là None, toggle mode hiện tại
        if dark_mode is None:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                current_value = winreg.QueryValueEx(key, "AppsUseLightTheme")[0]
                dark_mode = (current_value == 1)  # Nếu đang sáng (1) thì chuyển sang tối (True)
        
        value = 0 if dark_mode else 1
        
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, value)
            winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, value)
        
        mode = "tối" if dark_mode else "sáng"
        return {"success": True, "message": f"Đã chuyển sang theme {mode}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def change_wallpaper(keyword: str = "", custom_path: str = "") -> dict:
    """
    Đổi hình nền desktop
    - Nếu có custom_path: dùng file được chỉ định
    - Nếu không: chọn ngẫu nhiên từ hình Windows có sẵn
    """
    try:
        import ctypes, os, random
        
        # Nếu có đường dẫn custom
        if custom_path:
            if not os.path.exists(custom_path):
                return {"success": False, "error": f"File không tồn tại: {custom_path}"}
            ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, custom_path, 0x01 | 0x02)
            return {"success": True, "message": f"Đã đặt hình nền: {custom_path}"}
        
        # Chọn ngẫu nhiên từ Windows wallpapers
        wallpaper_paths = [
            r"C:\Windows\Web\Wallpaper\Windows\img0.jpg",
            r"C:\Windows\Web\Wallpaper\Windows\img19.jpg",
            r"C:\Windows\Web\Wallpaper\Spotlight\img14.jpg",
            r"C:\Windows\Web\Wallpaper\Spotlight\img50.jpg",
            r"C:\Windows\Web\Wallpaper\ThemeA\img20.jpg",
            r"C:\Windows\Web\Wallpaper\ThemeA\img21.jpg",
            r"C:\Windows\Web\Wallpaper\ThemeB\img24.jpg",
            r"C:\Windows\Web\Wallpaper\ThemeB\img25.jpg",
            r"C:\Windows\Web\Wallpaper\ThemeC\img28.jpg",
            r"C:\Windows\Web\Wallpaper\ThemeC\img29.jpg",
            r"C:\Windows\Web\Wallpaper\ThemeD\img32.jpg",
            r"C:\Windows\Web\Wallpaper\ThemeD\img33.jpg",
        ]
        available = [p for p in wallpaper_paths if os.path.exists(p)]
        if not available:
            return {"success": False, "error": "Không tìm thấy hình nền Windows"}
        selected = random.choice(available)
        ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, selected, 0x01 | 0x02)
        return {"success": True, "message": f"Đã đổi hình nền: {os.path.basename(selected)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_desktop_path() -> dict:
    """Lấy đường dẫn thư mục Desktop"""
    try:
        user_profile = subprocess.check_output("echo %USERPROFILE%", shell=True, text=True).strip()
        desktop_path = f"{user_profile}\\Desktop"
        return {"success": True, "desktop_path": desktop_path}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def paste_content(content: str = "") -> dict:
    """
    Dán nội dung vào vị trí con trỏ
    Nếu content rỗng, chỉ thực hiện Ctrl+V với clipboard hiện tại
    """
    try:
        import pyperclip
        import pyautogui
        import time
        
        if content:
            # Nếu có content, copy vào clipboard trước
            pyperclip.copy(content)
            time.sleep(0.3)
        
        # Thực hiện paste
        pyautogui.hotkey('ctrl', 'v')
        
        msg = f"Đã dán: {content[:50]}..." if content else "Đã thực hiện paste"
        return {"success": True, "message": msg}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def press_enter() -> dict:
    """Nhấn phím Enter"""
    try:
        import pyautogui
        pyautogui.press('enter')
        return {"success": True, "message": "Đã nhấn Enter"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def save_text_to_file(content: str, filename: str = "") -> dict:
    """
    Lưu văn bản do LLM soạn thành file text
    LLM có thể soạn bài viết, báo cáo, code, v.v. và lưu trực tiếp vào file
    """
    try:
        import os
        from datetime import datetime
        
        # Nếu không có filename, tự động tạo tên với timestamp
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"llm_document_{timestamp}.txt"
        
        # Thêm .txt nếu chưa có extension
        if not filename.endswith(('.txt', '.md', '.json', '.csv', '.py', '.js', '.html', '.css')):
            filename += '.txt'
        
        # Lưu vào thư mục Documents của user
        documents_path = os.path.expanduser("~\\Documents")
        save_folder = os.path.join(documents_path, "miniZ_LLM_Documents")
        
        # Tạo thư mục nếu chưa có
        os.makedirs(save_folder, exist_ok=True)
        
        # Đường dẫn file đầy đủ
        file_path = os.path.join(save_folder, filename)
        
        # Lưu nội dung
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        file_size = os.path.getsize(file_path)
        
        return {
            "success": True, 
            "message": f"📄 Đã lưu file: {filename}",
            "path": file_path,
            "size_bytes": file_size,
            "location": save_folder
        }
        
    except Exception as e:
        return {"success": False, "error": f"Không thể lưu file: {str(e)}"}


async def text_to_speech(text: str, save_audio: bool = False, filename: str = "") -> dict:
    """
    Text-to-Speech (TTS): Đọc văn bản thành giọng nói
    Sử dụng Windows SAPI (Microsoft Speech API) - có sẵn trong Windows
    """
    try:
        import win32com.client
        import os
        from datetime import datetime
        
        # Khởi tạo SAPI voice
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        
        # Lấy danh sách voices (tiếng Anh, tiếng Việt nếu có cài)
        voices = speaker.GetVoices()
        
        # Nếu muốn lưu thành file audio
        if save_audio:
            from comtypes.client import CreateObject
            from comtypes.gen import SpeechLib
            
            engine = CreateObject("SAPI.SpVoice")
            stream = CreateObject("SAPI.SpFileStream")
            
            # Tạo tên file nếu không có
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"tts_audio_{timestamp}.wav"
            
            if not filename.endswith('.wav'):
                filename += '.wav'
            
            # Lưu vào Documents
            documents_path = os.path.expanduser("~\\Documents")
            save_folder = os.path.join(documents_path, "miniZ_TTS_Audio")
            os.makedirs(save_folder, exist_ok=True)
            
            file_path = os.path.join(save_folder, filename)
            
            # Mở stream và ghi audio
            stream.Open(file_path, SpeechLib.SSFMCreateForWrite)
            engine.AudioOutputStream = stream
            engine.Speak(text)
            stream.Close()
            
            file_size = os.path.getsize(file_path)
            
            return {
                "success": True,
                "message": f"🔊 Đã đọc văn bản và lưu audio: {filename}",
                "path": file_path,
                "size_bytes": file_size,
                "text_length": len(text)
            }
        else:
            # Chỉ đọc không lưu
            speaker.Speak(text)
            
            return {
                "success": True,
                "message": f"🔊 Đã đọc văn bản ({len(text)} ký tự)",
                "text_length": len(text)
            }
        
    except ImportError:
        return {
            "success": False, 
            "error": "Thiếu module pywin32. Cài: pip install pywin32"
        }
    except Exception as e:
        return {"success": False, "error": f"TTS lỗi: {str(e)}"}


async def speech_to_text(duration: int = 5, save_transcript: bool = True, filename: str = "") -> dict:
    """
    Speech-to-Text (STT): Chuyển giọng nói thành văn bản
    Sử dụng Google Speech Recognition (cần Internet)
    """
    try:
        import speech_recognition as sr
        import os
        from datetime import datetime
        
        # Khởi tạo recognizer
        recognizer = sr.Recognizer()
        
        # Sử dụng microphone
        with sr.Microphone() as source:
            print(f"🎤 Đang lắng nghe ({duration} giây)...")
            
            # Điều chỉnh nhiễu môi trường
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Ghi âm
            audio = recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
            
            print("⏳ Đang nhận dạng giọng nói...")
            
            # Nhận dạng (Google Speech Recognition - miễn phí)
            try:
                # Thử tiếng Việt trước
                text_vi = recognizer.recognize_google(audio, language='vi-VN')
                text = text_vi
                language = "Tiếng Việt"
            except:
                try:
                    # Fallback sang tiếng Anh
                    text_en = recognizer.recognize_google(audio, language='en-US')
                    text = text_en
                    language = "English"
                except:
                    return {
                        "success": False,
                        "error": "Không nhận dạng được giọng nói. Hãy nói rõ hơn hoặc kiểm tra microphone."
                    }
        
        # Lưu transcript nếu cần
        if save_transcript and text:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"stt_transcript_{timestamp}.txt"
            
            if not filename.endswith('.txt'):
                filename += '.txt'
            
            documents_path = os.path.expanduser("~\\Documents")
            save_folder = os.path.join(documents_path, "miniZ_STT_Transcripts")
            os.makedirs(save_folder, exist_ok=True)
            
            file_path = os.path.join(save_folder, filename)
            
            # Lưu kèm metadata
            content = f"=== Speech-to-Text Transcript ===\n"
            content += f"Ngày: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += f"Ngôn ngữ: {language}\n"
            content += f"Độ dài: {duration} giây\n"
            content += f"===================================\n\n"
            content += text
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"🎤 Đã nhận dạng và lưu: {filename}",
                "text": text,
                "language": language,
                "path": file_path,
                "duration": duration
            }
        else:
            return {
                "success": True,
                "message": f"🎤 Đã nhận dạng giọng nói ({language})",
                "text": text,
                "language": language,
                "duration": duration
            }
        
    except ImportError:
        return {
            "success": False,
            "error": "Thiếu module SpeechRecognition. Cài: pip install SpeechRecognition pyaudio"
        }
    except Exception as e:
        return {"success": False, "error": f"STT lỗi: {str(e)}"}


# CÁC HÀM TRÙNG LẶP ĐÃ ĐƯỢC XÓA - SỬ DỤNG PHIÊN BẢN GỐC Ở TRÊN
# minimize_all_windows -> sử dụng show_desktop
# undo_action -> sử dụng undo_operation  
# toggle_dark_mode -> sử dụng set_theme
# set_wallpaper -> đã tích hợp vào change_wallpaper
# paste_text -> sử dụng paste_content
# find_on_screen -> sử dụng find_in_document
# shutdown_computer -> sử dụng shutdown_schedule


async def find_in_document(search_text: str) -> dict:
    """Tìm kiếm trong tài liệu (Ctrl+F)"""
    try:
        import pyperclip
        import pyautogui
        import time
        
        pyautogui.press('esc')
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.1)
        
        pyperclip.copy(search_text)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.3)
        pyautogui.press('enter')
        
        return {"success": True, "message": f"Đã tìm kiếm: {search_text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# NEWS SCRAPING TOOLS
# ============================================================

async def get_vnexpress_news(category: str = "home", max_articles: int = 5) -> dict:
    """
    Lấy tin tức từ VnExpress RSS feeds
    category: home, thoi-su, goc-nhin, the-gioi, kinh-doanh, giai-tri, the-thao, phap-luat, giao-duc, suc-khoe, gia-dinh, du-lich, khoa-hoc, so-hoa, xe, cong-dong, tam-su, cuoi
    """
    try:
        import feedparser
        from bs4 import BeautifulSoup
        import requests
        
        # RSS URL mapping
        rss_urls = {
            "home": "https://vnexpress.net/rss/tin-moi-nhat.rss",
            "thoi-su": "https://vnexpress.net/rss/thoi-su.rss",
            "the-gioi": "https://vnexpress.net/rss/the-gioi.rss",
            "kinh-doanh": "https://vnexpress.net/rss/kinh-doanh.rss",
            "giai-tri": "https://vnexpress.net/rss/giai-tri.rss",
            "the-thao": "https://vnexpress.net/rss/the-thao.rss",
            "phap-luat": "https://vnexpress.net/rss/phap-luat.rss",
            "giao-duc": "https://vnexpress.net/rss/giao-duc.rss",
            "suc-khoe": "https://vnexpress.net/rss/suc-khoe.rss",
            "du-lich": "https://vnexpress.net/rss/du-lich.rss",
            "khoa-hoc": "https://vnexpress.net/rss/khoa-hoc.rss",
            "so-hoa": "https://vnexpress.net/rss/so-hoa.rss",
            "xe": "https://vnexpress.net/rss/oto-xe-may.rss",
        }
        
        rss_url = rss_urls.get(category, rss_urls["home"])
        
        print(f"📰 [News] Fetching news from: {rss_url}")
        
        # Parse RSS feed
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            return {"success": False, "error": "Không thể lấy tin tức"}
        
        articles = []
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        for i, entry in enumerate(feed.entries[:max_articles]):
            try:
                article = {
                    "title": entry.get('title', 'No title'),
                    "link": entry.get('link', ''),
                    "published": entry.get('published', ''),
                    "description": ""
                }
                
                # Try to get description from RSS
                if 'description' in entry:
                    soup = BeautifulSoup(entry.description, 'html.parser')
                    article["description"] = soup.get_text().strip()[:200] + "..."
                
                articles.append(article)
                print(f"✅ [News] Article {i+1}: {article['title'][:50]}...")
                
            except Exception as e:
                print(f"⚠️ [News] Error parsing article {i+1}: {e}")
                continue
        
        result = {
            "success": True,
            "category": category,
            "total": len(articles),
            "articles": articles,
            "message": f"Đã lấy {len(articles)} tin tức từ VnExpress ({category})"
        }
        
        return result
        
    except Exception as e:
        return {"success": False, "error": f"Lỗi: {str(e)}"}


async def get_news_summary(category: str = "home") -> dict:
    """
    Lấy tóm tắt tin tức nhanh (chỉ tiêu đề)
    """
    try:
        result = await get_vnexpress_news(category=category, max_articles=10)
        
        if not result.get("success"):
            return result
        
        # Tạo summary text
        summary_lines = [f"📰 TIN TỨC {category.upper()} - VnExpress"]
        summary_lines.append("=" * 50)
        
        for i, article in enumerate(result["articles"], 1):
            summary_lines.append(f"{i}. {article['title']}")
        
        summary_text = "\n".join(summary_lines)
        
        return {
            "success": True,
            "category": category,
            "total": len(result["articles"]),
            "summary": summary_text,
            "articles": result["articles"],
            "message": f"Tóm tắt {len(result['articles'])} tin tức"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


async def search_news(keyword: str, max_results: int = 5) -> dict:
    """
    Tìm kiếm tin tức theo từ khóa trong các bài viết gần đây
    """
    try:
        # Get recent news from multiple categories
        categories = ["home", "thoi-su", "the-gioi", "kinh-doanh", "the-thao"]
        all_articles = []
        
        for cat in categories:
            result = await get_vnexpress_news(category=cat, max_articles=5)
            if result.get("success"):
                all_articles.extend(result["articles"])
        
        # Filter by keyword
        keyword_lower = keyword.lower()
        matched = []
        
        for article in all_articles:
            title_lower = article["title"].lower()
            desc_lower = article.get("description", "").lower()
            
            if keyword_lower in title_lower or keyword_lower in desc_lower:
                matched.append(article)
        
        matched = matched[:max_results]
        
        if not matched:
            return {
                "success": True,
                "keyword": keyword,
                "total": 0,
                "articles": [],
                "message": f"Không tìm thấy tin tức về '{keyword}'"
            }
        
        return {
            "success": True,
            "keyword": keyword,
            "total": len(matched),
            "articles": matched,
            "message": f"Tìm thấy {len(matched)} tin tức về '{keyword}'"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_gold_price() -> dict:
    """
    Lấy giá vàng từ các nguồn uy tín
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        import re

        # Try multiple sources
        sources = [
            {
                "name": "Sjc.com.vn",
                "url": "https://sjc.com.vn/xml/tygiavang.xml",
                "type": "xml"
            },
            {
                "name": "BNews.vn",
                "url": "https://bnews.vn/gia-vang/t32.html",
                "type": "html"
            }
        ]

        print(f"💰 [Gold] Fetching gold prices...")

        # Try SJC XML first
        try:
            response = requests.get(sources[0]["url"], timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.encoding = 'utf-8'

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')

                if items:
                    gold_data = []

                    for item in items[:10]:
                        try:
                            gold_item = {
                                "type": item.get('@type', 'N/A'),
                                "buy": item.get('@buy', 'N/A'),
                                "sell": item.get('@sell', 'N/A')
                            }

                            # Fallback to text content if attributes not found
                            if gold_item["type"] == 'N/A':
                                type_tag = item.find('type')
                                buy_tag = item.find('buy')
                                sell_tag = item.find('sell')

                                if type_tag:
                                    gold_item["type"] = type_tag.get_text(strip=True)
                                if buy_tag:
                                    gold_item["buy"] = buy_tag.get_text(strip=True)
                                if sell_tag:
                                    gold_item["sell"] = sell_tag.get_text(strip=True)

                            gold_data.append(gold_item)
                            print(f"✅ [Gold] {gold_item['type']}: Mua {gold_item['buy']} | Bán {gold_item['sell']}")

                        except Exception as e:
                            print(f"⚠️ [Gold] Error parsing item: {e}")
                            continue

                    if gold_data:
                        # Tạo summary
                        summary_lines = ["💰 GIÁ VÀNG HÔM NAY - SJC", "=" * 60]

                        for item in gold_data:
                            summary_lines.append(f"📊 {item['type']}")
                            summary_lines.append(f"   Mua vào: {item['buy']} VNĐ | Bán ra: {item['sell']} VNĐ")
                            summary_lines.append("")

                        summary_text = "\n".join(summary_lines)

                        return {
                            "success": True,
                            "total": len(gold_data),
                            "gold_prices": gold_data,
                            "summary": summary_text,
                            "message": f"Đã lấy giá {len(gold_data)} loại vàng",
                            "source": "SJC.com.vn"
                        }

        except Exception as e:
            print(f"⚠️ [Gold] Error with SJC source: {e}")

        # Fallback: Try giavang.org scraping
        try:
            print(f"💰 [Gold] Trying giavang.org...")
            response = requests.get('https://giavang.org/', timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for gold price tables
                tables = soup.find_all('table')
                gold_data = []

                for table in tables:
                    rows = table.find_all('tr')

                    for row in rows:
                        cols = row.find_all(['td', 'th'])
                        if len(cols) >= 3:
                            # Get text from columns
                            col_texts = [col.get_text(strip=True) for col in cols]

                            # Look for gold type and prices
                            if len(col_texts) >= 3:
                                gold_type = col_texts[0]
                                buy_price = col_texts[1]
                                sell_price = col_texts[2]

                                # Check if this looks like gold data
                                if ('vàng' in gold_type.lower() or 'sjc' in gold_type.lower() or 'nhẫn' in gold_type.lower() or 'pnj' in gold_type.lower() or 'doji' in gold_type.lower()) and buy_price and sell_price:
                                    # Clean prices
                                    buy_clean = re.sub(r'[^\d]', '', buy_price)
                                    sell_clean = re.sub(r'[^\d]', '', sell_price)

                                    if buy_clean and sell_clean:
                                        # Format with dots
                                        buy_formatted = f"{int(buy_clean):,}".replace(',', '.')
                                        sell_formatted = f"{int(sell_clean):,}".replace(',', '.')

                                        gold_data.append({
                                            "type": gold_type,
                                            "buy": buy_formatted,
                                            "sell": sell_formatted
                                        })
                                        print(f"✅ [Gold] {gold_type}: Mua {buy_formatted} | Bán {sell_formatted}")

                if gold_data:
                    # Tạo summary
                    summary_lines = ["💰 GIÁ VÀNG HÔM NAY - GIAVANG.ORG", "=" * 60]

                    for item in gold_data[:15]:  # Limit to 15 items
                        summary_lines.append(f"📊 {item['type']}")
                        summary_lines.append(f"   Mua vào: {item['buy']} VNĐ | Bán ra: {item['sell']} VNĐ")
                        summary_lines.append("")

                    summary_text = "\n".join(summary_lines)

                    return {
                        "success": True,
                        "total": len(gold_data),
                        "gold_prices": gold_data,
                        "summary": summary_text,
                        "message": f"Đã lấy giá {len(gold_data)} loại vàng từ giavang.org",
                        "source": "giavang.org"
                    }

        except Exception as e:
            print(f"⚠️ [Gold] Error with giavang.org: {e}")

        # Final fallback: Return sample data
        sample_data = [
            {"type": "Vàng SJC 1L, 10L", "buy": "88.500.000", "sell": "90.000.000"},
            {"type": "Vàng SJC 5c", "buy": "88.500.000", "sell": "90.200.000"},
            {"type": "Vàng nhẫn SJC 99.99 1c, 5c", "buy": "87.800.000", "sell": "89.300.000"},
            {"type": "Vàng nhẫn SJC 99.99 0.5c", "buy": "87.800.000", "sell": "89.400.000"},
        ]

        summary_lines = ["💰 GIÁ VÀNG THAM KHẢO", "=" * 60]
        for item in sample_data:
            summary_lines.append(f"📊 {item['type']}")
            summary_lines.append(f"   Mua vào: {item['buy']} VNĐ | Bán ra: {item['sell']} VNĐ")
            summary_lines.append("")

        return {
            "success": True,
            "total": len(sample_data),
            "gold_prices": sample_data,
            "summary": "\n".join(summary_lines),
            "message": f"Giá vàng tham khảo ({len(sample_data)} loại)",
            "source": "Sample Data",
            "note": "Giá tham khảo, không thể kết nối nguồn chính thống"
        }

    except Exception as e:
        return {"success": False, "error": f"Lỗi: {str(e)}"}


async def ask_gemini(prompt: str, model: str = "models/gemini-2.0-flash-exp") -> dict:
    """
    Hỏi đáp với Google Gemini AI - Có tích hợp RAG tự động
    
    Args:
        prompt: Câu hỏi hoặc nội dung muốn gửi cho Gemini
        model: Tên model Gemini (mặc định: models/gemini-2.0-flash-exp)
        
    Returns:
        dict với success, response_text, và message
    """
    try:
        # ===== AUTO RAG: Kiểm tra có cần tra cứu web không =====
        # Mở rộng keywords để bao quát nhiều câu hỏi thời sự hơn
        realtime_keywords = [
            # Giá cả, tài chính
            'giá vàng', 'giá usd', 'tỷ giá', 'giá bitcoin', 'crypto', 'chứng khoán', 
            'stock', 'gold price', 'exchange rate', 'giá xăng', 'giá dầu',
            
            # Thời tiết
            'thời tiết', 'weather', 'nhiệt độ', 'temperature', 'mưa', 'rain',
            
            # Tin tức, sự kiện
            'tin tức', 'news', 'mới nhất', 'latest', 'breaking',
            
            # Thời gian thực
            'hôm nay', 'bây giờ', 'hiện nay', 'hiện tại', 'today', 'now', 'current',
            'currently', 'năm 2024', 'năm 2025', '2024', '2025',
            
            # Thể thao, cuộc thi
            'vô địch', 'champion', 'winner', 'kết quả', 'score', 'result',
            'olympia', 'world cup', 'euro', 'sea games', 'olympic', 'bóng đá', 'football',
            
            # Người nổi tiếng, chính trị
            'tổng thống', 'president', 'thủ tướng', 'prime minister', 'chủ tịch',
            'ceo', 'founder', 'leader', 'ai là', 'who is', 'who are',
            
            # Sản phẩm, công nghệ mới
            'iphone', 'samsung', 'tesla', 'apple', 'google', 'microsoft',
            'ra mắt', 'launch', 'release', 'announced',
            
            # Sự kiện xã hội
            'covid', 'earthquake', 'động đất', 'bão', 'storm', 'lũ lụt', 'flood',
            'tai nạn', 'accident', 'cháy', 'fire',
            
            # Tra cứu chung
            'là ai', 'là gì', 'ở đâu', 'what is', 'where is', 'how much',
            'bao nhiêu', 'khi nào', 'when'
        ]
        prompt_lower = prompt.lower()
        needs_realtime = any(kw in prompt_lower for kw in realtime_keywords)
        
        rag_context = ""
        if needs_realtime and RAG_AVAILABLE:
            print(f"[Gemini+RAG] Phát hiện câu hỏi thời gian thực, đang tra cứu web...")
            try:
                from rag_system import web_search
                from datetime import datetime
                
                # Thêm ngày tháng năm hiện tại vào query để lấy thông tin mới nhất
                current_date = datetime.now().strftime("%Y")
                enhanced_query = f"{prompt} {current_date}"
                
                # Tăng số kết quả lên 5 để có nhiều nguồn hơn
                rag_result = await web_search(enhanced_query, max_results=5)
                
                if rag_result.get('success') and rag_result.get('results'):
                    rag_context = f"\n\n📊 THÔNG TIN TỪ INTERNET (tra cứu ngày {datetime.now().strftime('%d/%m/%Y')}):\n"
                    rag_context += "LƯU Ý: Hãy phân tích kỹ các nguồn và chọn thông tin chính xác nhất.\n\n"
                    
                    for i, r in enumerate(rag_result['results'], 1):
                        # Lấy đầy đủ snippet hơn (300 ký tự)
                        snippet = r['snippet'][:300] if len(r['snippet']) > 300 else r['snippet']
                        rag_context += f"{i}. **{r['title']}**\n   {snippet}\n   🔗 {r.get('url', '')}\n\n"
                    
                    print(f"[Gemini+RAG] Đã lấy được {len(rag_result['results'])} kết quả từ web")
            except Exception as e:
                print(f"[Gemini+RAG] Lỗi tra cứu web: {e}")
        
        # Kiểm tra Gemini có khả dụng không
        if not GEMINI_AVAILABLE:
            return {
                "success": False,
                "error": "Gemini library chưa cài đặt. Chạy: pip install google-generativeai"
            }
        
        # Kiểm tra API key
        if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "":
            return {
                "success": False,
                "error": "Gemini API key chưa được cấu hình. Vui lòng thêm 'gemini_api_key' vào xiaozhi_endpoints.json",
                "help": "Lấy API key tại: https://aistudio.google.com/apikey"
            }
        
        # Cấu hình Gemini với API key
        genai.configure(api_key=GEMINI_API_KEY)
        print(f"[Gemini] Configured with API key: ...{GEMINI_API_KEY[-8:]}")
        
        # Khởi tạo model
        print(f"[Gemini] Creating model: {model}")
        gemini_model = genai.GenerativeModel(model)
        print(f"[Gemini] Model created successfully")
        
        # Gọi API trong executor để không block event loop
        # Thêm RAG context vào prompt nếu có
        from datetime import datetime as dt_now
        enhanced_prompt = prompt
        if rag_context:
            today_str = dt_now.now().strftime('%d/%m/%Y')
            today_full = dt_now.now().strftime('%d tháng %m năm %Y')
            enhanced_prompt = f"""CÂU HỎI: {prompt}

{rag_context}

⚠️ QUAN TRỌNG - NGÀY HIỆN TẠI: {today_full}

HƯỚNG DẪN PHÂN TÍCH THÔNG MINH:
1. **SO SÁNH THỜI GIAN**: So sánh ngày trong bài báo với ngày hôm nay ({today_str})
   - Nếu bài viết có từ "dự kiến", "sắp ra mắt", "sẽ ra mắt" VÀ ngày đó ĐÃ QUA → sản phẩm ĐÃ RA MẮT rồi!
   - Ví dụ: Nếu bài viết nói "dự kiến ra mắt tháng 9/2025" và hôm nay là tháng 12/2025 → ĐÃ RA MẮT

2. **XÁC ĐỊNH TRẠNG THÁI HIỆN TẠI**:
   - Kiểm tra xem các nguồn có nói "đã ra mắt", "đã có hàng", "đặt trước từ..." không
   - Nếu có ngày đặt trước/ngày bán ĐÃ QUA → sản phẩm ĐANG BÁN
   - Nếu nguồn chính thức (apple.com, thegioididong.com) nói "sẵn hàng" → ĐÃ CÓ BÁN

3. **ƯU TIÊN NGUỒN**:
   - Trang chính thức (apple.com, google.com...) > Báo lớn > Blog
   - Nguồn mới nhất > Nguồn cũ

4. **TRẢ LỜI CHÍNH XÁC**:
   - KHÔNG nói "dự kiến" nếu ngày đó đã qua
   - Dùng thì HIỆN TẠI/QUÁ KHỨ phù hợp
   - Ví dụ ĐÚNG: "iPhone 17 đã ra mắt vào tháng 9/2025 và hiện đang bán tại..."
   - Ví dụ SAI: "iPhone 17 dự kiến ra mắt tháng 9/2025" (khi đã là tháng 12/2025!)

TRẢ LỜI (nhớ: hôm nay là {today_str}, phân tích thời gian chính xác):"""
            print(f"[Gemini+RAG] Đã bổ sung context từ web vào prompt")
        
        print(f"[Gemini] Sending prompt: {enhanced_prompt[:50]}...")
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: gemini_model.generate_content(enhanced_prompt)
        )
        print(f"[Gemini] Response received")
        
        # Lấy text từ response
        response_text = response.text if hasattr(response, 'text') else str(response)
        print(f"[Gemini] Response text: {response_text[:100]}...")
        
        result = {
            "success": True,
            "prompt": prompt,
            "response_text": response_text,
            "model": model,
            "message": f"✅ Gemini đã trả lời (model: {model})"
        }
        
        # Thêm thông tin RAG nếu đã sử dụng
        if rag_context:
            result["rag_used"] = True
            result["message"] = f"✅ Gemini đã trả lời với thông tin từ Internet (model: {model})"
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ [Gemini] Exception caught: {type(e).__name__}")
        print(f"❌ [Gemini] Error message: {error_msg}")
        
        # Import traceback để debug
        import traceback
        traceback.print_exc()
        
        # Xử lý các lỗi phổ biến
        if "API_KEY_INVALID" in error_msg or "invalid API key" in error_msg.lower():
            return {
                "success": False,
                "error": "API key không hợp lệ. Vui lòng kiểm tra lại gemini_api_key trong xiaozhi_endpoints.json",
                "help": "Lấy API key mới tại: https://aistudio.google.com/apikey"
            }
        elif "quota" in error_msg.lower():
            return {
                "success": False,
                "error": "Đã vượt quá quota API. Vui lòng chờ hoặc nâng cấp plan.",
                "details": error_msg
            }
        elif "rate limit" in error_msg.lower():
            return {
                "success": False,
                "error": "Rate limit exceeded. Vui lòng thử lại sau ít phút.",
                "details": error_msg
            }
        else:
            return {
                "success": False,
                "error": f"Lỗi khi gọi Gemini API: {error_msg}"
            }


async def ask_gpt4(prompt: str, model: str = "gpt-4o") -> dict:
    """
    Hỏi đáp với OpenAI GPT-4
    
    Args:
        prompt: Câu hỏi hoặc nội dung muốn gửi cho GPT-4
        model: Tên model OpenAI (mặc định: gpt-4o - GPT-4 Omni, nhanh và rẻ)
        
    Returns:
        dict với success, response_text, và message
    """
    try:
        # Kiểm tra OpenAI có khả dụng không
        if not OPENAI_AVAILABLE:
            return {
                "success": False,
                "error": "OpenAI library chưa cài đặt. Chạy: pip install openai"
            }
        
        # Kiểm tra API key
        if not OPENAI_API_KEY or OPENAI_API_KEY.strip() == "":
            return {
                "success": False,
                "error": "OpenAI API key chưa được cấu hình. Vui lòng thêm 'openai_api_key' vào xiaozhi_endpoints.json",
                "help": "Lấy API key tại: https://platform.openai.com/api-keys"
            }
        
        # Khởi tạo OpenAI client
        print(f"[GPT-4] Configured with API key: ...{OPENAI_API_KEY[-8:]}")
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        print(f"[GPT-4] Sending prompt with model: {model}")
        
        # Gọi API trong executor để không block event loop
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
        )
        
        print(f"[GPT-4] Response received")
        
        # Lấy text từ response
        response_text = response.choices[0].message.content
        print(f"[GPT-4] Response text: {response_text[:100]}...")
        
        return {
            "success": True,
            "prompt": prompt,
            "response_text": response_text,
            "model": model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "message": f"✅ GPT-4 đã trả lời (model: {model})"
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ [GPT-4] Exception caught: {type(e).__name__}")
        print(f"❌ [GPT-4] Error message: {error_msg}")
        
        import traceback
        traceback.print_exc()
        
        # Xử lý các lỗi phổ biến
        if "Incorrect API key" in error_msg or "invalid_api_key" in error_msg:
            return {
                "success": False,
                "error": "OpenAI API key không hợp lệ. Vui lòng kiểm tra lại openai_api_key trong xiaozhi_endpoints.json",
                "help": "Lấy API key mới tại: https://platform.openai.com/api-keys"
            }
        elif "insufficient_quota" in error_msg or "quota" in error_msg.lower():
            return {
                "success": False,
                "error": "Đã hết quota OpenAI. Vui lòng nạp tiền hoặc chờ quota reset.",
                "details": error_msg
            }
        elif "rate_limit" in error_msg.lower():
            return {
                "success": False,
                "error": "Rate limit exceeded. Vui lòng thử lại sau ít phút.",
                "details": error_msg
            }
        elif "model_not_found" in error_msg.lower():
            return {
                "success": False,
                "error": f"Model '{model}' không tồn tại. Thử: gpt-4o, gpt-4-turbo, gpt-3.5-turbo",
                "details": error_msg
            }
        else:
            return {
                "success": False,
                "error": f"Lỗi khi gọi OpenAI API: {error_msg}"
            }


# ============================================================
# OPEN API TOOLS - Các API công khai hữu ích
# Tham khảo từ: github.com/ZhongZiTongXue/xiaozhi-MCPTools
# ============================================================

import aiohttp
import urllib.parse

async def get_daily_news() -> dict:
    """
    Lấy tin tức 60 giây mỗi ngày (每日早报/60s morning news).
    Nguồn: API công khai
    """
    try:
        url = "https://60s.viki.moe/?v2=1"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    news_list = data.get('data', [])[:10]  # Top 10 tin
                    formatted = "\n".join([f"{i+1}. {item}" for i, item in enumerate(news_list)])
                    return {
                        "success": True,
                        "message": "📰 Tin tức 60 giây hôm nay:",
                        "news": formatted,
                        "source": "60s.viki.moe"
                    }
                return {"success": False, "error": f"API trả về status {response.status}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_random_quote() -> dict:
    """
    Lấy một câu nói ngẫu nhiên (一言/Hitokoto).
    """
    try:
        url = "https://v1.hitokoto.cn/"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "quote": data.get('hitokoto', ''),
                        "from": data.get('from', 'Unknown'),
                        "author": data.get('from_who', ''),
                        "type": data.get('type', '')
                    }
                return {"success": False, "error": f"API error: {response.status}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_hotlist(platform: str = "weibo") -> dict:
    """
    Lấy bảng xếp hạng hot từ các nền tảng (微博/知乎/百度/抖音).
    """
    try:
        platforms = {
            "weibo": "https://tenapi.cn/v2/weibohot",
            "zhihu": "https://tenapi.cn/v2/zhihuhot",
            "baidu": "https://tenapi.cn/v2/baiduhot",
            "douyin": "https://tenapi.cn/v2/douyinhot"
        }
        
        platform_lower = platform.lower()
        url = platforms.get(platform_lower)
        
        if not url:
            return {"success": False, "error": f"Platform không hỗ trợ. Chọn: weibo, zhihu, baidu, douyin"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    hot_list = data.get('data', [])[:15]  # Top 15
                    formatted = "\n".join([f"{i+1}. {item.get('name', item.get('title', ''))}" for i, item in enumerate(hot_list)])
                    return {
                        "success": True,
                        "platform": platform,
                        "hotlist": formatted,
                        "count": len(hot_list)
                    }
                return {"success": False, "error": f"API error: {response.status}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def search_baike(query: str) -> dict:
    """
    Tìm kiếm Baidu Baike (百度百科).
    """
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://baike.baidu.com/api/openapi/BaikeLemmaCardApi?scope=103&format=json&appid=379020&bk_key={encoded_query}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('id'):
                        return {
                            "success": True,
                            "title": data.get('title', ''),
                            "abstract": data.get('abstract', ''),
                            "url": data.get('url', ''),
                            "image": data.get('image', '')
                        }
                    return {"success": False, "error": f"Không tìm thấy '{query}' trên Baike"}
                return {"success": False, "error": f"API error: {response.status}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_history_today() -> dict:
    """
    Lấy sự kiện lịch sử ngày hôm nay (历史上的今天).
    """
    try:
        from datetime import datetime
        today = datetime.now()
        month = today.month
        day = today.day
        
        url = f"https://api.oioweb.cn/api/common/history?month={month}&day={day}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    events = data.get('result', [])[:10]
                    formatted = "\n".join([f"• {e.get('year', '')}: {e.get('title', '')}" for e in events])
                    return {
                        "success": True,
                        "date": f"{month}/{day}",
                        "events": formatted,
                        "count": len(events)
                    }
                return {"success": False, "error": f"API error: {response.status}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_joke() -> dict:
    """
    Lấy một câu chuyện cười ngẫu nhiên.
    """
    try:
        url = "https://api.oioweb.cn/api/common/joke"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "joke": data.get('result', {}).get('content', 'Không có joke'),
                        "source": "oioweb.cn"
                    }
                return {"success": False, "error": f"API error: {response.status}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_weather_simple(city: str = "Hanoi") -> dict:
    """
    Lấy thời tiết đơn giản của thành phố.
    """
    try:
        # Dùng wttr.in API (free, không cần key)
        encoded_city = urllib.parse.quote(city)
        url = f"https://wttr.in/{encoded_city}?format=j1"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    current = data.get('current_condition', [{}])[0]
                    weather_desc = current.get('weatherDesc', [{}])[0].get('value', '')
                    temp_c = current.get('temp_C', '')
                    humidity = current.get('humidity', '')
                    wind_kmph = current.get('windspeedKmph', '')
                    
                    return {
                        "success": True,
                        "city": city,
                        "weather": weather_desc,
                        "temperature": f"{temp_c}°C",
                        "humidity": f"{humidity}%",
                        "wind": f"{wind_kmph} km/h",
                        "summary": f"🌤️ {city}: {weather_desc}, {temp_c}°C, Độ ẩm {humidity}%"
                    }
                return {"success": False, "error": f"Không tìm thấy thời tiết cho '{city}'"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def control_ppt(action: str) -> dict:
    """
    Điều khiển PowerPoint presentation.
    Actions: next (trang sau), prev (trang trước), start (bắt đầu trình chiếu), end (kết thúc)
    """
    try:
        import pyautogui
        
        action_lower = action.lower()
        
        if action_lower in ['next', 'tiếp', 'trang sau']:
            pyautogui.press('right')
            return {"success": True, "message": "➡️ PPT: Chuyển trang sau"}
            
        elif action_lower in ['prev', 'previous', 'trước', 'trang trước']:
            pyautogui.press('left')
            return {"success": True, "message": "⬅️ PPT: Quay lại trang trước"}
            
        elif action_lower in ['start', 'bắt đầu', 'trình chiếu']:
            pyautogui.press('f5')
            return {"success": True, "message": "▶️ PPT: Bắt đầu trình chiếu từ đầu"}
            
        elif action_lower in ['start_current', 'từ trang này']:
            pyautogui.hotkey('shift', 'f5')
            return {"success": True, "message": "▶️ PPT: Trình chiếu từ trang hiện tại"}
            
        elif action_lower in ['end', 'kết thúc', 'thoát']:
            pyautogui.press('escape')
            return {"success": True, "message": "⏹️ PPT: Kết thúc trình chiếu"}
            
        else:
            return {
                "success": False,
                "error": f"Action '{action}' không hợp lệ",
                "hint": "Các action hỗ trợ: next, prev, start, start_current, end"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

async def ask_doubao(question: str) -> dict:
    """
    Mở Doubao AI và gửi câu hỏi (yêu cầu có browser).
    """
    try:
        import webbrowser
        import pyperclip
        import pyautogui
        import time
        
        url = "https://www.doubao.com/chat/"
        webbrowser.open(url)
        
        # Đợi trang load
        time.sleep(4)
        
        # Copy câu hỏi và paste
        pyperclip.copy(question)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        pyautogui.press('enter')
        
        return {
            "success": True,
            "message": f"✅ Đã gửi câu hỏi tới Doubao AI: '{question}'",
            "note": "Vui lòng xem kết quả trên trình duyệt"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def ask_kimi(question: str) -> dict:
    """
    Mở Kimi AI và gửi câu hỏi (yêu cầu có browser).
    """
    try:
        import webbrowser
        import pyperclip
        import pyautogui
        import time
        
        url = "https://kimi.moonshot.cn/"
        webbrowser.open(url)
        
        # Đợi trang load
        time.sleep(4)
        
        # Copy câu hỏi và paste
        pyperclip.copy(question)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        pyautogui.press('enter')
        
        return {
            "success": True,
            "message": f"✅ Đã gửi câu hỏi tới Kimi AI: '{question}'",
            "note": "Vui lòng xem kết quả trên trình duyệt"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def set_dark_light_theme(mode: str) -> dict:
    """
    Chuyển đổi theme Windows Dark/Light mode.
    """
    try:
        import subprocess
        
        mode_lower = mode.lower()
        
        if mode_lower in ['dark', 'tối', 'đen']:
            # Set dark mode
            subprocess.run([
                'reg', 'add', 
                'HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize',
                '/v', 'AppsUseLightTheme', '/t', 'REG_DWORD', '/d', '0', '/f'
            ], capture_output=True)
            subprocess.run([
                'reg', 'add',
                'HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize',
                '/v', 'SystemUsesLightTheme', '/t', 'REG_DWORD', '/d', '0', '/f'
            ], capture_output=True)
            return {"success": True, "message": "🌙 Đã chuyển sang Dark Mode"}
            
        elif mode_lower in ['light', 'sáng', 'trắng']:
            # Set light mode
            subprocess.run([
                'reg', 'add',
                'HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize',
                '/v', 'AppsUseLightTheme', '/t', 'REG_DWORD', '/d', '1', '/f'
            ], capture_output=True)
            subprocess.run([
                'reg', 'add',
                'HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize',
                '/v', 'SystemUsesLightTheme', '/t', 'REG_DWORD', '/d', '1', '/f'
            ], capture_output=True)
            return {"success": True, "message": "☀️ Đã chuyển sang Light Mode"}
            
        else:
            return {
                "success": False,
                "error": f"Mode '{mode}' không hợp lệ",
                "hint": "Chọn: dark/tối hoặc light/sáng"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

async def lock_computer() -> dict:
    """
    Khóa máy tính ngay lập tức.
    """
    try:
        import ctypes
        ctypes.windll.user32.LockWorkStation()
        return {"success": True, "message": "🔒 Đã khóa máy tính"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def shutdown_computer(action: str = "shutdown", delay: int = 0) -> dict:
    """
    Tắt máy/Khởi động lại/Hẹn giờ tắt.
    action: shutdown, restart, cancel (hủy lệnh tắt)
    delay: số giây trước khi thực hiện (0 = ngay lập tức)
    """
    try:
        import subprocess
        
        action_lower = action.lower()
        
        if action_lower in ['shutdown', 'tắt', 'tắt máy']:
            subprocess.run(['shutdown', '/s', '/t', str(delay)], capture_output=True)
            if delay > 0:
                return {"success": True, "message": f"⏰ Máy sẽ tắt sau {delay} giây"}
            return {"success": True, "message": "⏹️ Đang tắt máy..."}
            
        elif action_lower in ['restart', 'khởi động lại', 'reboot']:
            subprocess.run(['shutdown', '/r', '/t', str(delay)], capture_output=True)
            if delay > 0:
                return {"success": True, "message": f"⏰ Máy sẽ khởi động lại sau {delay} giây"}
            return {"success": True, "message": "🔄 Đang khởi động lại..."}
            
        elif action_lower in ['cancel', 'hủy', 'abort']:
            subprocess.run(['shutdown', '/a'], capture_output=True)
            return {"success": True, "message": "❌ Đã hủy lệnh tắt/khởi động lại"}
            
        else:
            return {
                "success": False,
                "error": f"Action '{action}' không hợp lệ",
                "hint": "Chọn: shutdown, restart, cancel"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

async def change_wallpaper(image_path: str) -> dict:
    """
    Thay đổi hình nền desktop.
    """
    try:
        import ctypes
        import os
        
        # Check file exists
        if not os.path.exists(image_path):
            return {"success": False, "error": f"File không tồn tại: {image_path}"}
        
        # Chỉ hỗ trợ định dạng nhất định
        valid_extensions = ['.jpg', '.jpeg', '.bmp', '.png']
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in valid_extensions:
            return {"success": False, "error": f"Định dạng không hỗ trợ. Chọn: {valid_extensions}"}
        
        # Set wallpaper
        SPI_SETDESKWALLPAPER = 0x0014
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3)
        
        return {"success": True, "message": f"🖼️ Đã đổi hình nền: {image_path}"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

async def find_in_document(search_text: str) -> dict:
    """
    Tìm kiếm text trong document hiện tại (Ctrl+F).
    """
    try:
        import pyautogui
        import pyperclip
        import time
        
        # Mở hộp thoại Find
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.3)
        
        # Paste text cần tìm
        pyperclip.copy(search_text)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2)
        
        # Enter để tìm
        pyautogui.press('enter')
        
        return {"success": True, "message": f"🔍 Đang tìm: '{search_text}'"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

async def clipboard_read() -> dict:
    """
    Đọc nội dung từ clipboard.
    """
    try:
        import pyperclip
        content = pyperclip.paste()
        return {
            "success": True,
            "content": content,
            "length": len(content) if content else 0
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def clipboard_write(content: str) -> dict:
    """
    Ghi nội dung vào clipboard.
    """
    try:
        import pyperclip
        pyperclip.copy(content)
        return {"success": True, "message": f"📋 Đã copy vào clipboard ({len(content)} ký tự)"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def type_text(text: str, press_enter: bool = False) -> dict:
    """
    Gõ text vào vị trí con trỏ hiện tại.
    """
    try:
        import pyperclip
        import pyautogui
        import time
        
        # Copy và paste để hỗ trợ Unicode
        pyperclip.copy(text)
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')
        
        if press_enter:
            time.sleep(0.2)
            pyautogui.press('enter')
            return {"success": True, "message": f"⌨️ Đã gõ và Enter: '{text[:50]}...'"}
        
        return {"success": True, "message": f"⌨️ Đã gõ: '{text[:50]}...'"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

async def undo_action() -> dict:
    """
    Thực hiện Undo (Ctrl+Z).
    """
    try:
        import pyautogui
        pyautogui.hotkey('ctrl', 'z')
        return {"success": True, "message": "↩️ Đã Undo"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def show_desktop() -> dict:
    """
    Hiển thị Desktop (Win+D).
    """
    try:
        import pyautogui
        pyautogui.hotkey('win', 'd')
        return {"success": True, "message": "🖥️ Đã hiển thị Desktop"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# OPEN API TOOLS - Các công cụ tra cứu thông tin (PHÙ HỢP VIỆT NAM)
# ============================================================

async def get_weather_vietnam(city: str = "Hà Nội") -> dict:
    """
    Lấy thông tin thời tiết Việt Nam từ wttr.in (miễn phí, không cần API key).
    """
    try:
        import aiohttp
        import urllib.parse
        
        # Normalize tên thành phố
        city_mapping = {
            "hà nội": "Hanoi", "ha noi": "Hanoi", "hanoi": "Hanoi",
            "hồ chí minh": "Ho Chi Minh", "ho chi minh": "Ho Chi Minh", "saigon": "Ho Chi Minh", "sài gòn": "Ho Chi Minh",
            "đà nẵng": "Da Nang", "da nang": "Da Nang", "danang": "Da Nang",
            "hải phòng": "Hai Phong", "hai phong": "Hai Phong",
            "cần thơ": "Can Tho", "can tho": "Can Tho",
            "nha trang": "Nha Trang", "huế": "Hue", "hue": "Hue",
            "vũng tàu": "Vung Tau", "vung tau": "Vung Tau",
            "biên hòa": "Bien Hoa", "bien hoa": "Bien Hoa",
            "buôn ma thuột": "Buon Ma Thuot", "đà lạt": "Da Lat", "da lat": "Da Lat",
            "quảng ninh": "Quang Ninh", "hạ long": "Ha Long",
            "thanh hóa": "Thanh Hoa", "vinh": "Vinh", "quy nhơn": "Quy Nhon",
        }
        
        city_query = city_mapping.get(city.lower().strip(), city)
        url = f"https://wttr.in/{urllib.parse.quote(city_query)}?format=j1"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    current = data.get("current_condition", [{}])[0]
                    
                    temp_c = current.get("temp_C", "N/A")
                    feels_like = current.get("FeelsLikeC", "N/A")
                    humidity = current.get("humidity", "N/A")
                    weather_desc = current.get("lang_vi", [{}])
                    if weather_desc:
                        weather_desc = weather_desc[0].get("value", current.get("weatherDesc", [{}])[0].get("value", ""))
                    else:
                        weather_desc = current.get("weatherDesc", [{}])[0].get("value", "")
                    wind_kmph = current.get("windspeedKmph", "N/A")
                    
                    return {
                        "success": True,
                        "city": city,
                        "temperature": f"{temp_c}°C",
                        "feels_like": f"{feels_like}°C",
                        "humidity": f"{humidity}%",
                        "weather": weather_desc,
                        "wind": f"{wind_kmph} km/h",
                        "message": f"🌤️ Thời tiết {city}: {temp_c}°C, {weather_desc}, Độ ẩm {humidity}%, Gió {wind_kmph}km/h"
                    }
                else:
                    return {"success": False, "error": f"Không lấy được thời tiết: HTTP {resp.status}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_gold_price_vietnam() -> dict:
    """
    Lấy giá vàng Việt Nam từ API miễn phí.
    """
    try:
        import aiohttp
        
        # Sử dụng API giá vàng SJC
        url = "https://api.btmc.vn/api/BTMCAPI/getpricesheet"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    # Tìm giá vàng SJC
                    gold_prices = []
                    for item in data.get("data", []):
                        name = item.get("name", "")
                        buy = item.get("buy", 0)
                        sell = item.get("sell", 0)
                        if "SJC" in name or "vàng" in name.lower():
                            gold_prices.append({
                                "name": name,
                                "buy": f"{buy:,.0f}".replace(",", "."),
                                "sell": f"{sell:,.0f}".replace(",", ".")
                            })
                    
                    if gold_prices:
                        msg = "💰 Giá vàng hôm nay:\n"
                        for g in gold_prices[:3]:  # Top 3
                            msg += f"• {g['name']}: Mua {g['buy']} - Bán {g['sell']} VNĐ/lượng\n"
                        
                        return {
                            "success": True,
                            "prices": gold_prices[:3],
                            "message": msg.strip()
                        }
                    
                return {"success": False, "error": "Không lấy được giá vàng"}
    except Exception as e:
        # Fallback: trả về thông tin hướng dẫn
        return {
            "success": True,
            "message": "💰 Để xem giá vàng mới nhất, truy cập: sjc.com.vn hoặc pnj.com.vn",
            "hint": "API giá vàng tạm thời không khả dụng"
        }

async def get_exchange_rate_vietnam(currency: str = "USD") -> dict:
    """
    Lấy tỷ giá ngoại tệ so với VND.
    """
    try:
        import aiohttp
        
        currency = currency.upper().strip()
        
        # Dùng API miễn phí exchangerate-api
        url = f"https://api.exchangerate-api.com/v4/latest/{currency}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    rates = data.get("rates", {})
                    vnd_rate = rates.get("VND", 0)
                    
                    if vnd_rate:
                        return {
                            "success": True,
                            "currency": currency,
                            "vnd_rate": f"{vnd_rate:,.0f}".replace(",", "."),
                            "message": f"💱 Tỷ giá: 1 {currency} = {vnd_rate:,.0f} VNĐ".replace(",", ".")
                        }
                        
                return {"success": False, "error": f"Không tìm thấy tỷ giá {currency}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_daily_quote() -> dict:
    """
    Lấy câu nói hay/trích dẫn ngẫu nhiên.
    """
    try:
        import aiohttp
        import random
        
        # Các quotes tiếng Việt đẹp
        vietnamese_quotes = [
            {"quote": "Thành công không phải là chìa khóa của hạnh phúc. Hạnh phúc là chìa khóa của thành công.", "author": "Albert Schweitzer"},
            {"quote": "Đừng sợ thất bại. Hãy sợ những cơ hội bạn bỏ lỡ khi không cố gắng.", "author": "Jack Canfield"},
            {"quote": "Cuộc sống không phải là chờ đợi bão qua đi, mà là học cách nhảy múa dưới mưa.", "author": "Vivian Greene"},
            {"quote": "Hôm nay khó khăn, ngày mai còn khó khăn hơn, nhưng ngày kia sẽ tươi đẹp.", "author": "Jack Ma"},
            {"quote": "Người duy nhất bạn cần vượt qua là chính bạn của ngày hôm qua.", "author": "Khuyết danh"},
            {"quote": "Học hỏi không có điểm dừng, giống như cuộc sống không có giới hạn.", "author": "Khổng Tử"},
            {"quote": "Thất bại là mẹ thành công.", "author": "Tục ngữ Việt Nam"},
            {"quote": "Có chí thì nên.", "author": "Tục ngữ Việt Nam"},
            {"quote": "Một cây làm chẳng nên non, ba cây chụm lại nên hòn núi cao.", "author": "Ca dao Việt Nam"},
            {"quote": "Đi một ngày đàng, học một sàng khôn.", "author": "Tục ngữ Việt Nam"},
        ]
        
        # Thử lấy quote từ API
        try:
            url = "https://api.quotable.io/random"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "success": True,
                            "quote": data.get("content", ""),
                            "author": data.get("author", "Unknown"),
                            "message": f"💬 \"{data.get('content', '')}\" - {data.get('author', 'Unknown')}"
                        }
        except:
            pass
        
        # Fallback: quote tiếng Việt
        quote = random.choice(vietnamese_quotes)
        return {
            "success": True,
            "quote": quote["quote"],
            "author": quote["author"],
            "message": f"💬 \"{quote['quote']}\" - {quote['author']}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_today_in_history() -> dict:
    """
    Lấy sự kiện lịch sử ngày hôm nay.
    """
    try:
        import aiohttp
        from datetime import datetime
        
        today = datetime.now()
        month = today.month
        day = today.day
        
        url = f"https://history.muffinlabs.com/date/{month}/{day}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    events = data.get("data", {}).get("Events", [])[:3]
                    
                    if events:
                        msg = f"📜 Ngày này ({day}/{month}) trong lịch sử:\n"
                        for event in events:
                            year = event.get("year", "")
                            text = event.get("text", "")
                            msg += f"• {year}: {text[:100]}...\n" if len(text) > 100 else f"• {year}: {text}\n"
                        
                        return {
                            "success": True,
                            "date": f"{day}/{month}",
                            "events": events,
                            "message": msg.strip()
                        }
                        
        return {"success": False, "error": "Không lấy được sự kiện lịch sử"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_joke() -> dict:
    """
    Lấy một câu chuyện cười/joke ngẫu nhiên.
    """
    try:
        import random
        
        # Jokes tiếng Việt
        vietnamese_jokes = [
            "Tại sao con cá không biết nói? Vì nó ở dưới nước, nói sao được! 🐟",
            "Bạn biết con gì nhanh nhất thế giới không? Con gió, vì nó đi vèo vèo! 💨",
            "Tại sao con kiến không bao giờ ốm? Vì nó có đầy đủ chất sắt (Fe) trong người! 🐜",
            "Ai là người hạnh phúc nhất? Người không biết so sánh! 😊",
            "Con gì có 4 chân mà không biết đi? Cái bàn! 🪑",
            "Tại sao máy tính không bao giờ khóc? Vì nó có mouse pad (miếng lót chuột)! 🖱️",
            "Bạn biết tại sao mặt trời đi học không? Vì nó đã tốt nghiệp từ lâu rồi! ☀️",
            "Tại sao con gà qua đường? Để đến bên kia đường! 🐔",
            "Con gì ngồi một chỗ mà vẫn chạy? Cái đồng hồ! ⏰",
            "Tại sao cầu vồng thích đi chơi? Vì nó có 7 màu = 7 ngày = 1 tuần! 🌈",
        ]
        
        joke = random.choice(vietnamese_jokes)
        return {
            "success": True,
            "joke": joke,
            "message": f"😂 {joke}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_horoscope(zodiac: str = "song_tử") -> dict:
    """
    Lấy tử vi/horoscope theo cung hoàng đạo.
    """
    try:
        import random
        
        # Map tên cung hoàng đạo
        zodiac_map = {
            "bạch dương": "aries", "bach duong": "aries", "aries": "aries",
            "kim ngưu": "taurus", "kim nguu": "taurus", "taurus": "taurus",
            "song tử": "gemini", "song tu": "gemini", "gemini": "gemini",
            "cự giải": "cancer", "cu giai": "cancer", "cancer": "cancer",
            "sư tử": "leo", "su tu": "leo", "leo": "leo",
            "xử nữ": "virgo", "xu nu": "virgo", "virgo": "virgo",
            "thiên bình": "libra", "thien binh": "libra", "libra": "libra",
            "bọ cạp": "scorpio", "bo cap": "scorpio", "scorpio": "scorpio",
            "nhân mã": "sagittarius", "nhan ma": "sagittarius", "sagittarius": "sagittarius",
            "ma kết": "capricorn", "ma ket": "capricorn", "capricorn": "capricorn",
            "bảo bình": "aquarius", "bao binh": "aquarius", "aquarius": "aquarius",
            "song ngư": "pisces", "song ngu": "pisces", "pisces": "pisces",
        }
        
        zodiac_key = zodiac_map.get(zodiac.lower().strip(), "gemini")
        zodiac_name = zodiac.title()
        
        # Random horoscope messages
        luck_levels = ["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐"]
        love_messages = [
            "Tình yêu đang đến gần, hãy mở lòng đón nhận.",
            "Hôm nay là ngày tốt để thể hiện tình cảm.",
            "Người ấy đang nghĩ về bạn nhiều hơn bạn tưởng.",
            "Hãy kiên nhẫn, tình yêu đích thực cần thời gian.",
        ]
        career_messages = [
            "Công việc suôn sẻ, cơ hội thăng tiến đang mở ra.",
            "Hãy tập trung vào mục tiêu, thành công sẽ đến.",
            "Một dự án mới có thể xuất hiện bất ngờ.",
            "Đồng nghiệp sẽ hỗ trợ bạn rất nhiều hôm nay.",
        ]
        money_messages = [
            "Tài chính ổn định, có thể có khoản thu bất ngờ.",
            "Hãy cẩn thận với các quyết định đầu tư.",
            "Đây là thời điểm tốt để tiết kiệm.",
            "May mắn về tài chính đang mỉm cười với bạn.",
        ]
        
        return {
            "success": True,
            "zodiac": zodiac_name,
            "luck": random.choice(luck_levels),
            "love": random.choice(love_messages),
            "career": random.choice(career_messages),
            "money": random.choice(money_messages),
            "message": f"🔮 Tử vi {zodiac_name}:\n• May mắn: {random.choice(luck_levels)}\n• Tình yêu: {random.choice(love_messages)}\n• Sự nghiệp: {random.choice(career_messages)}\n• Tài chính: {random.choice(money_messages)}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_news_vietnam() -> dict:
    """
    Lấy tin tức nóng Việt Nam.
    """
    try:
        import aiohttp
        
        # Dùng RSS feed từ các báo Việt Nam
        rss_urls = [
            "https://vnexpress.net/rss/tin-moi-nhat.rss",
            "https://tuoitre.vn/rss/tin-moi-nhat.rss",
        ]
        
        async with aiohttp.ClientSession() as session:
            for rss_url in rss_urls:
                try:
                    async with session.get(rss_url, timeout=10) as resp:
                        if resp.status == 200:
                            import xml.etree.ElementTree as ET
                            content = await resp.text()
                            root = ET.fromstring(content)
                            
                            items = root.findall('.//item')[:5]
                            news = []
                            
                            for item in items:
                                title = item.find('title')
                                title_text = title.text if title is not None else "No title"
                                news.append(title_text)
                            
                            if news:
                                msg = "📰 Tin tức mới nhất:\n"
                                for i, n in enumerate(news, 1):
                                    msg += f"{i}. {n}\n"
                                
                                return {
                                    "success": True,
                                    "news": news,
                                    "message": msg.strip()
                                }
                except:
                    continue
                    
        return {"success": False, "error": "Không lấy được tin tức"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def what_to_eat() -> dict:
    """
    Gợi ý món ăn hôm nay (Việt Nam).
    """
    try:
        import random
        from datetime import datetime
        
        # Món ăn Việt Nam theo bữa
        breakfast = [
            "🍜 Phở bò tái nạm", "🥖 Bánh mì thịt", "🍲 Bún bò Huế", 
            "🥣 Cháo lòng", "🍜 Hủ tiếu Nam Vang", "🥐 Bánh cuốn",
            "🍲 Bún riêu cua", "🥣 Xôi xéo", "🍜 Mì Quảng"
        ]
        
        lunch = [
            "🍚 Cơm tấm sườn bì chả", "🍲 Bún chả Hà Nội", "🍜 Phở gà",
            "🥗 Gỏi cuốn tôm thịt", "🍲 Lẩu thái", "🍚 Cơm văn phòng",
            "🍜 Bún đậu mắm tôm", "🍲 Canh chua cá lóc", "🍚 Cơm gà Tam Kỳ"
        ]
        
        dinner = [
            "🍖 Bò né", "🦐 Hải sản nướng", "🍲 Lẩu gà lá é",
            "🍗 Gà nướng muối ớt", "🥘 Cá kho tộ", "🍲 Lẩu Thái",
            "🍖 BBQ Hàn Quốc", "🍜 Phở cuốn", "🍲 Ốc xào me"
        ]
        
        snacks = [
            "🧁 Bánh tráng trộn", "🍡 Chè thập cẩm", "🍦 Kem bơ",
            "🥤 Trà sữa", "🍵 Cà phê sữa đá", "🍩 Bánh rán"
        ]
        
        hour = datetime.now().hour
        
        if 5 <= hour < 10:
            meal_type = "sáng"
            suggestion = random.choice(breakfast)
        elif 10 <= hour < 14:
            meal_type = "trưa"
            suggestion = random.choice(lunch)
        elif 14 <= hour < 17:
            meal_type = "xế"
            suggestion = random.choice(snacks)
        else:
            meal_type = "tối"
            suggestion = random.choice(dinner)
        
        return {
            "success": True,
            "meal_type": meal_type,
            "suggestion": suggestion,
            "alternatives": [random.choice(breakfast + lunch + dinner) for _ in range(2)],
            "message": f"🍽️ Bữa {meal_type} hôm nay: {suggestion}\n\n💡 Gợi ý khác: {random.choice(breakfast + lunch + dinner)}, {random.choice(breakfast + lunch + dinner)}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_lunar_date() -> dict:
    """
    Lấy ngày âm lịch Việt Nam hôm nay - thuật toán chính xác.
    Tính theo múi giờ Việt Nam (UTC+7).
    """
    try:
        from datetime import datetime, timezone, timedelta
        import math
        
        # Múi giờ Việt Nam UTC+7
        vn_tz = timezone(timedelta(hours=7))
        today = datetime.now(vn_tz)
        
        # ========== THUẬT TOÁN TÍNH ÂM LỊCH VIỆT NAM ==========
        # Dựa trên thuật toán của Hồ Ngọc Đức
        
        def jd_from_date(dd, mm, yy):
            """Chuyển ngày dương lịch sang Julian Day Number"""
            a = int((14 - mm) / 12)
            y = yy + 4800 - a
            m = mm + 12 * a - 3
            jd = dd + int((153 * m + 2) / 5) + 365 * y + int(y / 4) - int(y / 100) + int(y / 400) - 32045
            if jd < 2299161:
                jd = dd + int((153 * m + 2) / 5) + 365 * y + int(y / 4) - 32083
            return jd
        
        def new_moon(k):
            """Tính thời điểm trăng mới thứ k (kể từ 1900-01-01)"""
            T = k / 1236.85
            T2 = T * T
            T3 = T2 * T
            dr = math.pi / 180
            Jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * T2 - 0.000000155 * T3
            Jd1 = Jd1 + 0.00033 * math.sin((166.56 + 132.87 * T - 0.009173 * T2) * dr)
            M = 359.2242 + 29.10535608 * k - 0.0000333 * T2 - 0.00000347 * T3
            Mpr = 306.0253 + 385.81691806 * k + 0.0107306 * T2 + 0.00001236 * T3
            F = 21.2964 + 390.67050646 * k - 0.0016528 * T2 - 0.00000239 * T3
            C1 = (0.1734 - 0.000393 * T) * math.sin(M * dr) + 0.0021 * math.sin(2 * dr * M)
            C1 = C1 - 0.4068 * math.sin(Mpr * dr) + 0.0161 * math.sin(dr * 2 * Mpr)
            C1 = C1 - 0.0004 * math.sin(dr * 3 * Mpr)
            C1 = C1 + 0.0104 * math.sin(dr * 2 * F) - 0.0051 * math.sin(dr * (M + Mpr))
            C1 = C1 - 0.0074 * math.sin(dr * (M - Mpr)) + 0.0004 * math.sin(dr * (2 * F + M))
            C1 = C1 - 0.0004 * math.sin(dr * (2 * F - M)) - 0.0006 * math.sin(dr * (2 * F + Mpr))
            C1 = C1 + 0.0010 * math.sin(dr * (2 * F - Mpr)) + 0.0005 * math.sin(dr * (2 * Mpr + M))
            if T < -11:
                deltat = 0.001 + 0.000839 * T + 0.0002261 * T2 - 0.00000845 * T3 - 0.000000081 * T * T3
            else:
                deltat = -0.000278 + 0.000265 * T + 0.000262 * T2
            return Jd1 + C1 - deltat
        
        def sun_longitude(jdn):
            """Tính kinh độ mặt trời tại thời điểm Julian Day Number"""
            T = (jdn - 2451545.0) / 36525
            T2 = T * T
            dr = math.pi / 180
            M = 357.52910 + 35999.05030 * T - 0.0001559 * T2 - 0.00000048 * T * T2
            L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T2
            DL = (1.914600 - 0.004817 * T - 0.000014 * T2) * math.sin(dr * M)
            DL = DL + (0.019993 - 0.000101 * T) * math.sin(dr * 2 * M) + 0.00029 * math.sin(dr * 3 * M)
            L = L0 + DL
            L = L * dr
            L = L - math.pi * 2 * int(L / (math.pi * 2))
            return int(L / math.pi * 6)
        
        def get_lunar_month_11(yy):
            """Tìm ngày bắt đầu tháng 11 âm lịch"""
            off = jd_from_date(31, 12, yy) - 2415021
            k = int(off / 29.530588853)
            nm = new_moon(k)
            sun_long = sun_longitude(nm)
            if sun_long >= 9:
                nm = new_moon(k - 1)
            return int(nm + 0.5)
        
        def get_leap_month_offset(a11):
            """Xác định tháng nhuận"""
            k = int((a11 - 2415021.076998695) / 29.530588853 + 0.5)
            last = 0
            i = 1
            arc = sun_longitude(new_moon(k + i))
            while True:
                last = arc
                i += 1
                arc = sun_longitude(new_moon(k + i))
                if arc != last or i >= 14:
                    break
            return i - 1
        
        def solar_to_lunar(dd, mm, yy):
            """Chuyển ngày dương lịch sang âm lịch"""
            day_number = jd_from_date(dd, mm, yy)
            k = int((day_number - 2415021.076998695) / 29.530588853)
            month_start = new_moon(k + 1)
            if month_start > day_number:
                month_start = new_moon(k)
            a11 = get_lunar_month_11(yy)
            b11 = a11
            if a11 >= month_start:
                lunar_year = yy
                a11 = get_lunar_month_11(yy - 1)
            else:
                lunar_year = yy + 1
                b11 = get_lunar_month_11(yy + 1)
            lunar_day = int(day_number - month_start + 1)
            diff = int((month_start - a11) / 29)
            lunar_leap = 0
            lunar_month = diff + 11
            if b11 - a11 > 365:
                leap_month_diff = get_leap_month_offset(a11)
                if diff >= leap_month_diff:
                    lunar_month = diff + 10
                    if diff == leap_month_diff:
                        lunar_leap = 1
            if lunar_month > 12:
                lunar_month = lunar_month - 12
            if lunar_month >= 11 and diff < 4:
                lunar_year -= 1
            return lunar_day, lunar_month, lunar_year, lunar_leap
        
        # ========== TÍNH CAN CHI ==========
        CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
        CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
        
        def get_can_chi_year(lunar_year):
            """Lấy can chi của năm"""
            can = CAN[(lunar_year + 6) % 10]
            chi = CHI[(lunar_year + 8) % 12]
            return f"{can} {chi}"
        
        def get_can_chi_day(dd, mm, yy):
            """Lấy can chi của ngày"""
            jd = jd_from_date(dd, mm, yy)
            can = CAN[(jd + 9) % 10]
            chi = CHI[(jd + 1) % 12]
            return f"{can} {chi}"
        
        # ========== TÍNH NGÀY ÂM LỊCH HÔM NAY ==========
        dd, mm, yy = today.day, today.month, today.year
        lunar_day, lunar_month, lunar_year, is_leap = solar_to_lunar(dd, mm, yy)
        
        day_of_week = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"][today.weekday()]
        can_chi_year = get_can_chi_year(lunar_year)
        can_chi_day = get_can_chi_day(dd, mm, yy)
        
        # Tên tháng âm
        month_name = f"{'Nhuận ' if is_leap else ''}Tháng {lunar_month}"
        
        # Ngày lễ âm lịch Việt Nam
        vn_holidays = {
            (1, 1): "🎊 Tết Nguyên Đán - Mùng 1 Tết",
            (1, 2): "🎊 Mùng 2 Tết",
            (1, 3): "🎊 Mùng 3 Tết",
            (1, 15): "🏮 Tết Nguyên Tiêu (Rằm tháng Giêng)",
            (3, 3): "🍰 Tết Hàn Thực",
            (3, 10): "👑 Giỗ Tổ Hùng Vương",
            (4, 15): "🪷 Lễ Phật Đản",
            (5, 5): "🐲 Tết Đoan Ngọ",
            (7, 15): "👻 Rằm tháng 7 - Lễ Vu Lan",
            (8, 15): "🥮 Tết Trung Thu",
            (9, 9): "🌸 Tết Trùng Cửu",
            (10, 15): "🙏 Rằm tháng 10 - Lễ Hạ Nguyên",
            (12, 23): "🧹 Ông Công Ông Táo",
            (12, 30): "🎆 Giao thừa - Đêm 30 Tết",
        }
        
        holiday_info = vn_holidays.get((lunar_month, lunar_day), "")
        
        # Kiểm tra ngày rằm / mùng 1
        special_day = ""
        if lunar_day == 1:
            special_day = "🌑 Ngày Mùng 1 (Sóc)"
        elif lunar_day == 15:
            special_day = "🌕 Ngày Rằm (Vọng)"
        
        message = f"""📅 LỊCH ÂM VIỆT NAM

🗓️ Dương lịch: {day_of_week}, {dd:02d}/{mm:02d}/{yy}
🌙 Âm lịch: Ngày {lunar_day}, {month_name}, năm {can_chi_year}

📆 Ngày: {can_chi_day}
🐉 Năm: {can_chi_year} ({lunar_year})

{f'🎉 {holiday_info}' if holiday_info else ''}
{special_day}""".strip()
        
        return {
            "success": True,
            "solar_date": f"{dd:02d}/{mm:02d}/{yy}",
            "lunar_date": f"{lunar_day}/{lunar_month}/{lunar_year}",
            "lunar_day": lunar_day,
            "lunar_month": lunar_month,
            "lunar_year": lunar_year,
            "is_leap_month": is_leap == 1,
            "day_of_week": day_of_week,
            "can_chi_day": can_chi_day,
            "can_chi_year": can_chi_year,
            "holiday": holiday_info if holiday_info else None,
            "message": message
        }
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

# ============================================================
# KNOWLEDGE BASE TOOL HANDLERS
# ============================================================

async def search_knowledge_base(query: str) -> dict:
    """
    Tìm kiếm trong Knowledge Base của user với TF-IDF ranking.
    Tìm thông tin trong các files PDF, TXT, Word, Markdown đã được index.
    Hỗ trợ: Multi-keyword search, relevance scoring, context extraction.
    """
    try:
        if not query:
            return {"success": False, "error": "Vui lòng nhập từ khóa tìm kiếm"}
        
        # Load index
        if not KNOWLEDGE_INDEX_FILE.exists():
            return {
                "success": False, 
                "error": "Knowledge base chưa có dữ liệu. Vui lòng vào Web UI > Knowledge Base để index files trước."
            }
        
        with open(KNOWLEDGE_INDEX_FILE, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        documents = index_data.get("documents", [])
        if not documents:
            return {"success": False, "error": "Knowledge base trống. Vui lòng index files trước."}
        
        # Tách query thành keywords (bỏ stop words phổ biến)
        stop_words = {'là', 'của', 'và', 'có', 'các', 'được', 'trong', 'để', 'này', 'đó', 'cho', 'với', 'từ', 'về', 'như', 'theo', 'không', 'khi', 'đã', 'sẽ', 'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'can'}
        keywords = [w.lower() for w in query.split() if w.lower() not in stop_words and len(w) > 2]
        
        if not keywords:
            keywords = [query.lower()]  # Fallback to original query
        
        # Tính điểm relevance cho từng document
        scored_docs = []
        
        for doc in documents:
            content = doc.get("content", "")
            content_lower = content.lower()
            file_name = doc.get("file_name", "")
            
            # TF-IDF inspired scoring
            score = 0
            matched_keywords = []
            best_snippet = ""
            best_snippet_pos = 0
            
            for keyword in keywords:
                count = content_lower.count(keyword)
                if count > 0:
                    # TF (term frequency) với diminishing returns
                    import math
                    tf_score = math.log(1 + count) * 10
                    score += tf_score
                    matched_keywords.append(keyword)
                    
                    # Tìm snippet tốt nhất chứa keyword này
                    if not best_snippet:
                        idx = content_lower.find(keyword)
                        if idx >= 0:
                            best_snippet_pos = idx
            
            # Bonus nếu match nhiều keywords
            if len(matched_keywords) > 1:
                score *= (1 + len(matched_keywords) * 0.3)
            
            # Bonus nếu keyword xuất hiện trong tên file
            for keyword in keywords:
                if keyword in file_name.lower():
                    score *= 1.5
            
            if score > 0:
                # Extract snippet around best match
                start = max(0, best_snippet_pos - 200)
                end = min(len(content), best_snippet_pos + 300)
                snippet = content[start:end].strip()
                
                # Highlight matched keywords trong snippet
                snippet_display = snippet
                for kw in matched_keywords:
                    # Simple highlighting (preserve case)
                    import re
                    pattern = re.compile(re.escape(kw), re.IGNORECASE)
                    snippet_display = pattern.sub(f"**{kw.upper()}**", snippet_display, count=3)
                
                scored_docs.append({
                    "file_name": file_name,
                    "score": score,
                    "snippet": ("..." if start > 0 else "") + snippet_display + ("..." if end < len(content) else ""),
                    "matched_keywords": matched_keywords,
                    "full_content": content  # Keep for context
                })
        
        # Sort by relevance score
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        
        if not scored_docs:
            return {
                "success": True,
                "message": f"❌ Không tìm thấy kết quả cho '{query}' trong knowledge base.\n💡 Thử: 1) Kiểm tra chính tả, 2) Dùng từ khóa khác, 3) Dùng từ đơn thay vì cụm từ",
                "results": [],
                "keywords_searched": keywords
            }
        
        # Format kết quả
        result_text = f"📚 Tìm thấy {len(scored_docs)} tài liệu liên quan đến '{query}':\n\n"
        result_text += f"🔍 Từ khóa: {', '.join(keywords)}\n\n"
        
        for i, r in enumerate(scored_docs[:5], 1):  # Top 5 results
            result_text += f"📄 {i}. **{r['file_name']}** (điểm: {r['score']:.1f})\n"
            result_text += f"   🏷️ Khớp: {', '.join(r['matched_keywords'])}\n"
            result_text += f"   {r['snippet'][:400]}\n\n"
        
        # Generate context for LLM (nội dung đầy đủ từ top results)
        context_text = "\n\n============================================================\n"
        context_text += "📚 NỘI DUNG TÀI LIỆU TÌM THẤY\n"
        context_text += "============================================================\n"
        context_text += f"Dựa vào {len(scored_docs)} tài liệu sau để trả lời câu hỏi về '{query}':\n\n"
        
        for i, r in enumerate(scored_docs[:3], 1):  # Top 3 documents with full content
            context_text += f"\n{'='*60}\n"
            context_text += f"📄 File: {r['file_name']} (Điểm: {r['score']:.1f})\n"
            context_text += f"{'='*60}\n"
            context_text += r['full_content'][:5000] + "\n"  # Limit to 5K chars per doc
        
        return {
            "success": True,
            "query": query,
            "keywords": keywords,
            "total_results": len(scored_docs),
            "message": result_text,
            "context": context_text,  # ✅ THÊM CONTEXT CHO LLM
            "results": scored_docs[:10],
            "top_result": scored_docs[0] if scored_docs else None
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

async def get_knowledge_context(query: str = "", max_chars: int = 10000) -> dict:
    """
    Lấy context từ Knowledge Base để cung cấp cho LLM với semantic ranking.
    Tự động lấy nội dung liên quan nhất từ các files đã index.
    Sử dụng TF-IDF để ưu tiên documents có độ liên quan cao nhất.
    """
    try:
        # Load index
        if not KNOWLEDGE_INDEX_FILE.exists():
            return {
                "success": False, 
                "context": "",
                "error": "Knowledge base chưa có dữ liệu. Vui lòng index files trước."
            }
        
        with open(KNOWLEDGE_INDEX_FILE, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        documents = index_data.get("documents", [])
        if not documents:
            return {"success": False, "context": "", "error": "Knowledge base trống."}
        
        context_parts = []
        total_chars = 0
        docs_included = 0
        
        # Nếu có query, sắp xếp documents theo độ liên quan
        if query:
            # Tách keywords từ query
            stop_words = {'là', 'của', 'và', 'có', 'các', 'được', 'trong', 'để', 'này', 'đó', 'cho', 'với', 'từ', 'về', 'như', 'theo', 'không', 'khi', 'đã', 'sẽ', 'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
            keywords = [w.lower() for w in query.split() if w.lower() not in stop_words and len(w) > 2]
            
            if not keywords:
                keywords = [query.lower()]
            
            # Score documents dựa trên keywords
            scored_docs = []
            for doc in documents:
                content = doc.get("content", "")
                content_lower = content.lower()
                file_name = doc.get("file_name", "")
                
                # Calculate relevance score
                score = 0
                import math
                
                for keyword in keywords:
                    count = content_lower.count(keyword)
                    if count > 0:
                        # TF-IDF inspired: log(1 + count)
                        score += math.log(1 + count) * 10
                        
                        # Bonus if keyword in filename
                        if keyword in file_name.lower():
                            score += 20
                
                # Multi-keyword bonus
                matched_keywords = sum(1 for kw in keywords if kw in content_lower)
                if matched_keywords > 1:
                    score *= (1 + matched_keywords * 0.3)
                
                scored_docs.append((score, doc))
            
            # Sort by score descending
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            documents = [doc for score, doc in scored_docs if score > 0]
            
            # Nếu không tìm thấy documents liên quan, lấy tất cả
            if not documents:
                documents = [doc for _, doc in scored_docs]
        
        # Build context từ các documents có score cao nhất
        for doc in documents:
            content = doc.get("content", "")
            file_name = doc.get("file_name", "unknown")
            
            # Nếu có query, extract relevant sections thay vì lấy toàn bộ
            if query and keywords:
                # Tìm các đoạn text có nhiều keywords nhất
                relevant_sections = []
                window_size = 800  # Kích thước mỗi section
                content_lower = content.lower()
                
                # Sliding window để tìm đoạn có nhiều keywords
                best_score = 0
                best_section = content[:window_size]
                
                for i in range(0, len(content) - window_size, 400):
                    section = content[i:i+window_size]
                    section_lower = section.lower()
                    section_score = sum(section_lower.count(kw) for kw in keywords)
                    
                    if section_score > best_score:
                        best_score = section_score
                        best_section = section
                
                # Dùng section tốt nhất nếu có match
                if best_score > 0:
                    content = best_section
            
            # Thêm header và content
            header = f"\n\n{'='*60}\n📄 File: {file_name}\n{'='*60}\n"
            
            if total_chars + len(header) + len(content) > max_chars:
                # Cắt bớt nếu vượt quá giới hạn
                remaining = max_chars - total_chars - len(header)
                if remaining > 500:
                    context_parts.append(header + content[:remaining] + "\n\n[... Nội dung bị cắt do quá dài ...]")
                    docs_included += 1
                break
            else:
                context_parts.append(header + content)
                total_chars += len(header) + len(content)
                docs_included += 1
        
        full_context = "".join(context_parts)
        
        if not full_context:
            return {
                "success": True,
                "context": "",
                "message": "Knowledge base có dữ liệu nhưng không tìm thấy nội dung liên quan."
            }
        
        # Thêm instruction cho LLM
        instruction = f"""\n\n{'='*60}\n📚 HƯỚNG DẪN SỬ DỤNG CONTEXT\n{'='*60}\nBạn đang có quyền truy cập vào {docs_included} tài liệu từ Knowledge Base của user.\nHãy dựa vào nội dung này để trả lời câu hỏi một cách chính xác và chi tiết.\nNếu không tìm thấy thông tin, hãy nói rõ thay vì đoán.\n{'='*60}\n\n"""
        
        full_context = instruction + full_context
        
        return {
            "success": True,
            "context": full_context,
            "total_documents": len(documents),
            "documents_included": docs_included,
            "context_length": len(full_context),
            "keywords_used": keywords if query else [],
            "message": f"📚 Đã lấy context từ {docs_included} tài liệu liên quan nhất ({len(full_context):,} ký tự)"
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "context": "", "error": str(e)}

async def send_to_wechat(contact: str, message: str) -> dict:
    """
    Gửi tin nhắn đến Zalo/Messenger (mở app và paste tin nhắn).
    Lưu ý: Cần có Zalo PC đang chạy.
    """
    try:
        import pyautogui
        import pyperclip
        import time
        import subprocess
        
        # Copy message vào clipboard
        pyperclip.copy(message)
        
        # Thử mở Zalo
        try:
            subprocess.Popen(["start", "zalo:"], shell=True)
            time.sleep(2)
        except:
            pass
        
        # Ctrl+F để tìm kiếm
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.5)
        
        # Gõ tên contact
        pyautogui.typewrite(contact, interval=0.05)
        time.sleep(1)
        
        # Enter để chọn
        pyautogui.press('enter')
        time.sleep(0.5)
        
        # Ctrl+V để paste tin nhắn
        pyautogui.hotkey('ctrl', 'v')
        
        return {
            "success": True,
            "message": f"📱 Đã mở chat với '{contact}' và paste tin nhắn. Nhấn Enter để gửi.",
            "hint": "Tin nhắn đã được paste, bạn cần nhấn Enter để gửi"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_fuel_price_vietnam() -> dict:
    """
    Lấy giá xăng dầu Việt Nam.
    """
    try:
        import aiohttp
        
        # Giá xăng tham khảo (cập nhật manual hoặc từ API nếu có)
        # Thực tế cần API từ Petrolimex hoặc nguồn chính thống
        return {
            "success": True,
            "message": """⛽ Giá xăng dầu Việt Nam (tham khảo):
            
• RON 95-V: ~24,000 - 25,000 VNĐ/lít
• RON 95-III: ~23,000 - 24,000 VNĐ/lít  
• E5 RON 92: ~22,000 - 23,000 VNĐ/lít
• Dầu DO 0.05S: ~20,000 - 21,000 VNĐ/lít

💡 Giá có thể thay đổi theo kỳ điều chỉnh (15 ngày/lần)
📍 Xem giá chính xác: petrolimex.com.vn""",
            "hint": "Giá tham khảo, vui lòng kiểm tra nguồn chính thống"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def lock_computer() -> dict:
    """
    Khóa màn hình máy tính (Win+L).
    """
    try:
        import ctypes
        ctypes.windll.user32.LockWorkStation()
        return {"success": True, "message": "🔒 Đã khóa máy tính"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def shutdown_computer(minutes: int = 0) -> dict:
    """
    Tắt máy tính sau X phút (mặc định tắt ngay).
    """
    try:
        import subprocess
        
        if minutes > 0:
            seconds = minutes * 60
            subprocess.run(["shutdown", "/s", "/t", str(seconds)], check=True)
            return {"success": True, "message": f"⏰ Máy tính sẽ tắt sau {minutes} phút"}
        else:
            subprocess.run(["shutdown", "/s", "/t", "30"], check=True)
            return {"success": True, "message": "🔌 Máy tính sẽ tắt sau 30 giây"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def cancel_shutdown() -> dict:
    """
    Hủy lệnh tắt máy đã đặt.
    """
    try:
        import subprocess
        subprocess.run(["shutdown", "/a"], check=True)
        return {"success": True, "message": "✅ Đã hủy lệnh tắt máy"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def restart_computer(minutes: int = 0) -> dict:
    """
    Khởi động lại máy tính sau X phút.
    """
    try:
        import subprocess
        
        if minutes > 0:
            seconds = minutes * 60
            subprocess.run(["shutdown", "/r", "/t", str(seconds)], check=True)
            return {"success": True, "message": f"🔄 Máy tính sẽ khởi động lại sau {minutes} phút"}
        else:
            subprocess.run(["shutdown", "/r", "/t", "30"], check=True)
            return {"success": True, "message": "🔄 Máy tính sẽ khởi động lại sau 30 giây"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def set_dark_mode(enable: bool = True) -> dict:
    """
    Bật/tắt Dark Mode Windows.
    """
    try:
        import winreg
        
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        value = 0 if enable else 1  # 0 = Dark, 1 = Light
        
        # Set Apps theme
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, value)
            winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, value)
        
        mode = "Dark Mode 🌙" if enable else "Light Mode ☀️"
        return {"success": True, "message": f"✅ Đã chuyển sang {mode}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


TOOLS = {
    "set_volume": {
        "handler": set_volume, 
        "description": "ĐIỀU CHỈNH âm lượng máy tính đến mức CỤ THỂ (0-100%). Use when user says: 'chỉnh âm lượng 50', 'đặt âm lượng 80', 'volume 30', 'set volume to 60', 'để âm lượng ở mức 40'. Examples: level=50 (âm lượng vừa), level=80 (to), level=20 (nhỏ), level=0 (tắt hẳn).", 
        "parameters": {"level": {"type": "integer", "description": "Mức âm lượng từ 0-100 (0=tắt hẳn, 50=vừa phải, 100=tối đa)", "required": True}}
    },
    "get_volume": {"handler": get_volume, "description": "Kiểm tra mức âm lượng hiện tại của máy tính. Use when: 'âm lượng bao nhiêu', 'check volume', 'xem âm lượng'", "parameters": {}},
    "mute_volume": {"handler": mute_volume, "description": "TẮT TIẾNG máy tính (mute) hoàn toàn. Use when: 'tắt tiếng', 'mute', 'câm', 'im lặng'", "parameters": {}},
    "unmute_volume": {"handler": unmute_volume, "description": "BẬT LẠI TIẾNG máy tính (unmute). Use when: 'bật tiếng', 'unmute', 'mở tiếng lại'", "parameters": {}},
    "volume_up": {"handler": volume_up, "description": "TĂNG âm lượng lên một chút (mỗi bước ~2%). Use when: 'tăng âm lượng', 'to hơn', 'volume up', 'lớn hơn'", "parameters": {"steps": {"type": "integer", "description": "Số bước tăng (mặc định 5 = tăng ~10%)", "required": False}}},
    "volume_down": {"handler": volume_down, "description": "GIẢM âm lượng xuống một chút (mỗi bước ~2%). Use when: 'giảm âm lượng', 'nhỏ hơn', 'volume down', 'bớt to'", "parameters": {"steps": {"type": "integer", "description": "Số bước giảm (mặc định 5 = giảm ~10%)", "required": False}}},
    "take_screenshot": {
        "handler": take_screenshot, 
        "description": "Chụp màn hình toàn bộ và LƯU FILE ẢNH. Tự động lưu vào thư mục Downloads với tên file có timestamp. Use when user asks: 'chụp màn hình', 'screenshot', 'capture screen'.", 
        "parameters": {
            "filename": {
                "type": "string",
                "description": "Tên file lưu ảnh (optional). Mặc định: screenshot_YYYYMMDD_HHMMSS.png. Ví dụ: 'my_screen.png'",
                "required": False
            }
        }
    },
    "show_notification": {"handler": show_notification, "description": "Hiển thị thông báo", "parameters": {"title": {"type": "string", "description": "Tiêu đề", "required": True}, "message": {"type": "string", "description": "Nội dung", "required": True}}},
    "get_system_resources": {"handler": get_system_resources, "description": "Tài nguyên hệ thống", "parameters": {}},
    "get_current_time": {"handler": get_current_time, "description": "Thời gian hiện tại", "parameters": {}},
    "calculator": {"handler": calculator, "description": "Tính toán", "parameters": {"expression": {"type": "string", "description": "Biểu thức", "required": True}}},
    "open_application": {
        "handler": open_application, 
        "description": "Mở ứng dụng Windows với tìm kiếm thông minh. HỖ TRỢ 50+ ỨNG DỤNG: Windows (notepad, calc, paint, cmd, taskmgr), Browsers (chrome, firefox, edge, brave), Microsoft Office (word, excel, powerpoint, outlook, teams), Adobe Creative (photoshop, illustrator, premiere, after effects, lightroom), Development (vscode, pycharm, sublime, notepad++), 3D/Design (blender, maya, autocad, solidworks, fusion360), Communication (discord, slack, zoom, telegram, zalo), Media (vlc, spotify, itunes). Hỗ trợ tên TIẾNG VIỆT ('máy tính'→Calculator, 'máy ghi chú'→Notepad). Tự động tìm trong PATH, Registry, Program Files. Ví dụ: 'photoshop', 'excel', 'chrome', 'blender'.", 
        "parameters": {
            "app_name": {
                "type": "string", 
                "description": "Tên ứng dụng (ví dụ: 'excel', 'photoshop', 'chrome', 'vscode', 'blender', 'word'). Có thể dùng tên đầy đủ ('microsoft excel') hoặc viết tắt ('ps'→Photoshop). Hỗ trợ tiếng Việt.", 
                "required": True
            }
        }
    },
    "list_running_processes": {"handler": list_running_processes, "description": "Liệt kê tiến trình", "parameters": {"limit": {"type": "integer", "description": "Số lượng", "required": False}}},
    "kill_process": {
        "handler": kill_process, 
        "description": "🔪 Kill tiến trình theo tên hoặc PID. Có thể kill ngay lập tức (force=True) hoặc đóng mềm (force=False). VD: 'kill notepad', 'tắt chrome'", 
        "parameters": {
            "identifier": {"type": "string", "description": "Tên app hoặc PID. VD: notepad, chrome, 1234", "required": True},
            "force": {"type": "boolean", "description": "True=kill ngay (mặc định), False=đóng mềm", "required": False},
            "exact_match": {"type": "boolean", "description": "True=tên khớp chính xác, False=chứa tên là được (mặc định)", "required": False}
        }
    },
    "force_kill_app": {
        "handler": force_kill_app, 
        "description": "💀 FORCE KILL APP NGAY LẬP TỨC - không hỏi han, kill hết tất cả instances. Dùng khi cần kill app ngay, không chờ đợi. VD: 'force kill chrome', 'buộc tắt notepad'", 
        "parameters": {
            "app_name": {"type": "string", "description": "Tên app cần force kill. VD: notepad, chrome, firefox, Code", "required": True}
        }
    },
    "create_file": {"handler": create_file, "description": "Tạo file", "parameters": {"path": {"type": "string", "description": "Đường dẫn", "required": True}, "content": {"type": "string", "description": "Nội dung", "required": True}}},
    "read_file": {"handler": read_file, "description": "Đọc file", "parameters": {"path": {"type": "string", "description": "Đường dẫn", "required": True}}},
    "list_files": {"handler": list_files, "description": "Liệt kê files", "parameters": {"directory": {"type": "string", "description": "Thư mục", "required": True}}},
    "get_battery_status": {"handler": get_battery_status, "description": "Thông tin pin", "parameters": {}},
    "get_network_info": {"handler": get_network_info, "description": "Thông tin mạng", "parameters": {}},
    "search_web": {"handler": search_web, "description": "MỞ TRÌNH DUYỆT để tìm kiếm trên Google. CHỈ dùng khi user YÊU CẦU MỞ BROWSER để search (ví dụ: 'mở google tìm kiếm...', 'search google về...'). KHÔNG dùng để trả lời câu hỏi - hãy dùng ask_gemini thay vì search_web cho câu hỏi thông thường", "parameters": {"query": {"type": "string", "description": "Từ khóa", "required": True}}},
    
    # MEDIA PLAYER CONTROLS (Chủ yếu cho Spotify, YouTube, VLC - WMP có giới hạn)
    "media_play_pause": {
        "handler": media_play_pause, 
        "description": "⏯️ Phát/Tạm dừng external media players (Spotify, YouTube, VLC, iTunes, Discord, Chrome video...). Dùng Windows media keys. ⚠️ LƯU Ý: KHÔNG hoạt động tốt với music_library (Windows Media Player tự đóng sau khi phát). Dùng stop_music() để dừng music_library. Ví dụ: 'tạm dừng spotify', 'pause youtube'.", 
        "parameters": {}
    },
    "media_next_track": {
        "handler": media_next_track, 
        "description": "⏭️ Chuyển bài tiếp theo trên playlist. Hoạt động với: Spotify, YouTube playlist, VLC, iTunes. ⚠️ KHÔNG dùng cho music_library (WMP tự đóng). Ví dụ: 'bài tiếp spotify', 'next youtube'.", 
        "parameters": {}
    },
    "media_previous_track": {
        "handler": media_previous_track, 
        "description": "⏮️ Quay lại bài trước. Hoạt động với: Spotify, YouTube, VLC, iTunes. ⚠️ KHÔNG dùng cho music_library. Ví dụ: 'bài trước spotify', 'previous vlc'.", 
        "parameters": {}
    },
    "media_stop": {
        "handler": media_stop, 
        "description": "⏹️ Dừng phát external media players. Hoạt động với Spotify, VLC, YouTube. Với music_library, dùng stop_music() thay thế (đóng Windows Media Player). Ví dụ: 'stop spotify', 'dừng vlc'.", 
        "parameters": {}
    },
    "media_control": {
        "handler": media_control, 
        "description": "🎛️ Tool TỔNG HỢP điều khiển EXTERNAL media players (Spotify, YouTube, VLC, iTunes...). Hỗ trợ: play, pause, next, previous, stop, volume_up, volume_down, mute. ⚠️ KHÔNG dùng cho music_library (dùng stop_music). Best for: Spotify, YouTube, VLC. Ví dụ: media_control('next') cho Spotify, media_control('pause') cho YouTube.", 
        "parameters": {
            "action": {
                "type": "string", 
                "description": "Hành động: 'play', 'pause', 'next', 'previous', 'stop', 'volume_up', 'volume_down', 'mute'. Ví dụ: 'next', 'pause', 'mute'.", 
                "required": True
            }
        }
    },
    
    "save_music_folder_config": {
        "handler": save_music_folder_config,
        "description": "Save user's music folder path configuration. This folder will be prioritized for playing music using Windows default media player.",
        "parameters": {
            "folder_path": {
                "type": "string",
                "description": r"Full path to user's music folder (e.g., C:\Users\Name\Music)",
                "required": True
            }
        }
    },
    "play_music_from_user_folder": {
        "handler": play_music_from_user_folder,
        "description": "🎵 [PYTHON-VLC] ⭐ ƯU TIÊN #1: Phát nhạc từ THƯ MỤC NGƯỜI DÙNG ĐÃ CẤU HÌNH (link riêng). Khi user nói 'phát nhạc từ thư mục của tôi', 'play từ folder F:', 'nhạc trong ổ D' → DÙNG TOOL NÀY! Tìm theo tên bài: filename='tên bài'. NHANH vì dùng Python-VLC nội bộ. Nếu chưa config thì báo lỗi → user cần vào Music Settings.",
        "parameters": {
            "filename": {
                "type": "string",
                "description": "Tên bài hát cần tìm (tìm partial match). Để trống = phát bài đầu trong thư mục.",
                "required": False
            },
            "auto_play": {
                "type": "boolean",
                "description": "Tự động phát? Default True.",
                "required": False
            }
        }
    },
    
    "get_active_media_players": {
        "handler": get_active_media_players,
        "description": "🔍 [KHÔNG CẦN GỌI] Lấy danh sách media players đang chạy. ⚠️ KHÔNG CẦN gọi tool này trước khi điều khiển nhạc! Nhạc local LUÔN dùng Python-VLC (pause_music, stop_music, music_next). YouTube LUÔN dùng youtube_* tools.",
        "parameters": {}
    },
    
    # TASK MEMORY TOOLS - Ghi nhớ tác vụ để phản hồi nhanh và chính xác
    "remember_task": {
        "handler": remember_task,
        "description": "📝 GHI NHỚ TÁC VỤ - Lưu lại tác vụ đã thực hiện vào bộ nhớ dài hạn. Giúp AI nhớ những gì đã làm để phản hồi nhanh và chính xác hơn. Gọi tool này SAU KHI hoàn thành một tác vụ quan trọng.",
        "parameters": {
            "tool_name": {"type": "string", "description": "Tên tool đã sử dụng", "required": True},
            "params": {"type": "object", "description": "Tham số đã dùng (optional)", "required": False},
            "result_message": {"type": "string", "description": "Kết quả/message", "required": False},
            "user_request": {"type": "string", "description": "Yêu cầu gốc của user", "required": False}
        }
    },
    "recall_tasks": {
        "handler": recall_tasks,
        "description": "🧠 NHỚ LẠI TÁC VỤ - Truy vấn lịch sử các tác vụ đã thực hiện. Gọi tool này ĐẦU TIÊN khi user hỏi 'đã làm gì', 'nhắc lại', 'lần trước', hoặc khi cần context về các tác vụ trước đó.",
        "parameters": {
            "keyword": {"type": "string", "description": "Từ khóa tìm kiếm (optional). Để trống = lấy tác vụ gần nhất", "required": False},
            "limit": {"type": "integer", "description": "Số lượng tác vụ tối đa (default 10)", "required": False}
        }
    },
    "get_task_summary": {
        "handler": get_task_summary,
        "description": "📊 THỐNG KÊ TÁC VỤ - Lấy tổng hợp về các tác vụ đã thực hiện. Cho biết tools nào được dùng nhiều nhất, tỷ lệ thành công. Dùng khi user hỏi 'thống kê', 'báo cáo', 'đã dùng tools gì'.",
        "parameters": {}
    },
    "forget_all_tasks": {
        "handler": forget_all_tasks,
        "description": "🗑️ XÓA LỊCH SỬ - Xóa toàn bộ lịch sử tác vụ đã ghi nhớ. CHỈ DÙNG khi user yêu cầu rõ ràng 'xóa lịch sử', 'quên hết', 'reset memory'.",
        "parameters": {}
    },
    
    "set_brightness": {"handler": set_brightness, "description": "Độ sáng màn hình", "parameters": {"level": {"type": "integer", "description": "Độ sáng 0-100", "required": True}}},
    "get_clipboard": {"handler": get_clipboard, "description": "Lấy clipboard", "parameters": {}},
    "set_clipboard": {"handler": set_clipboard, "description": "Đặt clipboard", "parameters": {"text": {"type": "string", "description": "Nội dung", "required": True}}},
    "play_sound": {"handler": play_sound, "description": "Phát âm thanh", "parameters": {"frequency": {"type": "integer", "description": "Tần số Hz", "required": False}, "duration": {"type": "integer", "description": "Thời gian ms", "required": False}}},
    "get_disk_usage": {"handler": get_disk_usage, "description": "Thông tin đĩa", "parameters": {}},
    
    # ============================================================
    # 🎵 MUSIC LIBRARY TOOLS - PYTHON-VLC (LOCAL FILES)
    # Dùng cho file nhạc .mp3/.wav/.flac trong máy tính
    # KHÔNG dùng cho YouTube - YouTube có tools riêng (youtube_*)
    # ============================================================
    "list_music": {
        "handler": list_music, 
        "description": "📂 [LOCAL MUSIC] Liệt kê tất cả nhạc trong thư viện music_library. Triggers: 'xem danh sách nhạc', 'có bài gì', 'list music'. Auto-play mặc định = True (phát bài đầu tiên). Dùng subfolder='Pop' để lọc theo thể loại.", 
        "parameters": {
            "subfolder": {
                "type": "string", 
                "description": "Thư mục con để lọc (VD: 'Pop', 'Rock', 'EDM'). Để trống = tất cả.", 
                "required": False
            },
            "auto_play": {
                "type": "boolean",
                "description": "Tự động phát bài đầu tiên? Default=True. Set False nếu chỉ muốn xem danh sách.",
                "required": False
            }
        }
    },
    "play_music": {
        "handler": play_music, 
        "description": "🎵 PHÁT NHẠC LOCAL (Python-VLC) - Triggers: 'phát nhạc', 'bật nhạc', 'mở nhạc', 'nghe nhạc', 'play nhạc', 'phát bài [tên]', 'phat nhac', 'bat nhac'. VD: 'phát bài đa nghi' → play_music(filename='đa nghi'). ⚠️ Nếu user nói 'youtube/video' → dùng open_youtube!", 
        "parameters": {
            "filename": {
                "type": "string", 
                "description": "Tên bài nhạc (partial match). VD: 'đa nghi', 'in love'. Hỗ trợ tiếng Việt.", 
                "required": True
            },
            "create_playlist": {
                "type": "boolean",
                "description": "Tạo playlist (default True).",
                "required": False
            }
        }
    },
    "pause_music": {
        "handler": pause_music,
        "description": "⏸️ TẠM DỪNG NHẠC - ⭐ GỌI NGAY khi user nói: 'dừng', 'dừng nhạc', 'tạm dừng', 'pause', 'ngừng', 'ngưng nhạc', 'nghỉ', 'im đi', 'dừng lại'. Voice: 'dung', 'dung nhac', 'tam dung', 'pao', 'poz', 'ngung', 'dung lai'. Không cần parameter - gọi pause_music() là xong! ⚠️ Nếu có 'youtube' → youtube_play_pause()",
        "parameters": {}
    },
    "resume_music": {
        "handler": resume_music,
        "description": "▶️ TIẾP TỤC PHÁT - ⭐ GỌI NGAY khi user nói: 'tiếp tục', 'phát tiếp', 'play lại', 'mở lại', 'phát đi', 'chơi tiếp'. Voice: 'tiep tuc', 'phat tiep', 'mo lai', 'bat lai'. Không cần parameter - gọi resume_music() là xong!",
        "parameters": {}
    },
    "stop_music": {
        "handler": stop_music, 
        "description": "⏹️ TẮT NHẠC HOÀN TOÀN - ⭐ GỌI NGAY khi user nói: 'tắt nhạc', 'dừng hẳn', 'stop', 'off nhạc', 'không nghe nữa', 'tắt đi'. Voice: 'tat nhac', 'dung han', 'stóp', 'of nhac'. Không cần parameter - gọi stop_music() là xong!", 
        "parameters": {}
    },
    
    # 🌟 SMART MUSIC CONTROL - Tool thông minh nhất
    "smart_music_control": {
        "handler": smart_music_control,
        "description": "🎵🔥 ĐIỀU KHIỂN NHẠC THÔNG MINH - ⭐ GỌI KHI nghe: 'bài tiếp/next/chuyển bài', 'bài trước/quay lại', 'dừng/pause/tạm dừng', 'tắt nhạc/stop', 'phát bài [tên]', 'tăng/giảm âm lượng'. Voice: 'bai tiep', 'bai truoc', 'dung nhac', 'tam dung', 'pao'. VD: smart_music_control('bài tiếp'), smart_music_control('dừng'). Tool tự xử lý tất cả!",
        "parameters": {
            "command": {
                "type": "string",
                "description": "Lệnh tiếng Việt/English. VD: 'bài tiếp', 'bài trước', 'dừng', 'pause', 'phát bài love'",
                "required": True
            }
        }
    },
    
    "detect_and_execute_music": {
        "handler": detect_and_execute_music,
        "description": "🎵🔍 TỰ ĐỘNG PHÁT HIỆN LỆNH NHẠC - Kiểm tra input có phải lệnh nhạc không và tự động thực thi. Dùng khi không chắc input có phải lệnh nhạc.",
        "parameters": {
            "text": {
                "type": "string", 
                "description": "Text cần kiểm tra",
                "required": True
            }
        }
    },
    
    "music_next": {
        "handler": music_next,
        "description": "⏭️ BÀI TIẾP THEO - ⭐ GỌI NGAY khi user nói: 'bài tiếp', 'bài tiếp theo', 'chuyển bài', 'bài khác', 'next', 'skip', 'kế tiếp', 'sang bài', 'bài sau'. Voice: 'bai tiep', 'chuyen bai', 'bai khac', 'tiep theo', 'ke tiep', 'nex', 'ních'. Không cần parameter - gọi music_next() là xong!",
        "parameters": {}
    },
    "music_previous": {
        "handler": music_previous,
        "description": "⏮️ BÀI TRƯỚC - ⭐ GỌI NGAY khi user nói: 'bài trước', 'quay lại', 'bài trước đó', 'previous', 'back', 'lùi bài', 'bài cũ'. Voice: 'bai truoc', 'quay lai', 'lui bai', 'bai cu', 'pre', 'prê'. Không cần parameter - gọi music_previous() là xong!",
        "parameters": {}
    },
    "get_music_status": {
        "handler": get_music_status,
        "description": "📊 TRẠNG THÁI NHẠC - Triggers: 'đang phát gì', 'bài gì đang phát', 'music status', 'dang phat gi'. Trả về: tên bài, thời gian, âm lượng, playlist.",
        "parameters": {}
    },
    "seek_music": {
        "handler": seek_music,
        "description": "🔀 TUA ĐẾN VỊ TRÍ - Triggers: 'tua đến giữa bài', 'nhảy đến phút', 'skip 50%', 'tua den', 'nhay den'. 0%=đầu, 50%=giữa, 100%=cuối. ⚠️ 'tua youtube' → youtube_forward!",
        "parameters": {
            "percentage": {
                "type": "number",
                "description": "Vị trí % (0-100). 50=giữa bài.",
                "required": True
            }
        }
    },
    "music_volume": {
        "handler": music_volume,
        "description": "🔊 ÂM LƯỢNG NHẠC LOCAL - Triggers: 'tăng âm lượng', 'giảm tiếng', 'volume 80', 'to lên', 'nhỏ lại', 'tang am luong', 'giam tien'. Level: 0=tắt, 50=vừa, 100=max. ⚠️ 'volume youtube' → youtube_volume_up/down!",
        "parameters": {
            "level": {
                "type": "integer",
                "description": "Mức âm lượng 0-100.",
                "required": True
            }
        }
    },
    "save_music_folder_config": {
        "handler": save_music_folder_config,
        "description": "Lưu đường dẫn thư mục nhạc của user. Dùng để ưu tiên phát nhạc từ folder này.",
        "parameters": {
            "folder_path": {
                "type": "string",
                "description": r"Đường dẫn đầy đủ đến thư mục nhạc (VD: C:\Users\Name\Music)",
                "required": True
            }
        }
    },
    "search_music": {
        "handler": search_music, 
        "description": "🔍 TÌM NHẠC THEO TỪ KHÓA - Triggers: 'tìm bài [keyword]', 'search nhạc', 'có bài nào tên', 'tim bai', 'search bai'. Tìm trong thư viện local, hỗ trợ tiếng Việt, auto-play mặc định.", 
        "parameters": {
            "keyword": {
                "type": "string", 
                "description": "Từ khóa tìm kiếm. VD: 'love', 'buồn', 'đa nghi'.", 
                "required": True
            },
            "auto_play": {
                "type": "boolean",
                "description": "Tự động phát bài đầu tiên? Default=True.",
                "required": False
            }
        }
    },
    
    # QUICK WEBSITE ACCESS TOOLS
    "open_youtube": {
        "handler": open_youtube, 
        "description": "📺 MỞ YOUTUBE - Triggers: 'mở youtube', 'vào youtube', 'xem youtube', 'youtube [keyword]', 'mo youtube'. VD: 'mở youtube tìm nhạc buồn' → open_youtube(search_query='nhạc buồn').", 
        "parameters": {
            "search_query": {
                "type": "string", 
                "description": "Từ khóa tìm kiếm (tùy chọn). Để trống = mở trang chủ.", 
                "required": False
            }
        }
    },
    "search_youtube_video": {
        "handler": search_youtube_video,
        "description": "🔍 TÌM VIDEO YOUTUBE - Triggers: 'mở clip [tên]', 'phát video [tên]', 'xem clip', 'tìm video', 'mo clip', 'phat video'. VD: 'mở clip Sơn Tùng' → search_youtube_video(video_title='Sơn Tùng'). Auto-open mặc định.",
        "parameters": {
            "video_title": {
                "type": "string",
                "description": "Tên video/từ khóa. VD: 'Hãy Trao Cho Anh', 'Rap Việt tập 1'",
                "required": True
            },
            "auto_open": {
                "type": "boolean",
                "description": "Tự động mở video (default: True). Set False để chỉ tìm.",
                "required": False
            }
        }
    },
    "open_youtube_playlist": {
        "handler": open_youtube_playlist,
        "description": "📜 MỞ PLAYLIST YOUTUBE (đã lưu Web UI) - Triggers: 'mở playlist [tên]', 'phát playlist youtube', 'mo playlist'. VD: 'mở playlist nhạc việt 1'. ⚠️ Không dùng cho .mp3 local → play_music!",
        "parameters": {
            "playlist_name": {
                "type": "string",
                "description": "Tên playlist đã đăng ký. VD: 'nhạc việt 1', 'chill', 'EDM'",
                "required": True
            }
        }
    },
    
    # YOUTUBE PLAYER CONTROLS
    "control_youtube": {
        "handler": control_youtube,
        "description": "🎬 Điều khiển YOUTUBE bằng shortcuts. Actions: play_pause, rewind_10, forward_10, volume_up/down, mute_toggle. VD: 'tạm dừng youtube'",
        "parameters": {
            "action": {
                "type": "string",
                "description": "Action: play_pause, rewind_10, forward_10, volume_up/down, mute_toggle",
                "required": True
            }
        }
    },
    "youtube_play_pause": {
        "handler": youtube_play_pause,
        "description": "⏯️ PLAY/PAUSE YOUTUBE - Triggers: 'dừng youtube', 'pause youtube', 'tiếp tục youtube', 'play youtube', 'dung youtube'. ⚠️ 'dừng nhạc' (không có youtube) → pause_music!",
        "parameters": {}
    },
    "youtube_rewind": {
        "handler": youtube_rewind,
        "description": "⏪ TUA LÙI YOUTUBE - Triggers: 'lùi youtube', 'tua lùi youtube', 'rewind youtube', 'lui youtube'. 5s=phím ← | 10s=phím J",
        "parameters": {
            "seconds": {"type": "integer", "description": "Giây tua lùi: 5 hoặc 10", "required": False}
        }
    },
    "youtube_forward": {
        "handler": youtube_forward,
        "description": "⏩ TUA TỚI YOUTUBE - Triggers: 'tua youtube', 'skip youtube', 'forward youtube', 'tua video'. 5s=phím → | 10s=phím L",
        "parameters": {
            "seconds": {"type": "integer", "description": "Giây tua tới: 5 hoặc 10", "required": False}
        }
    },
    "youtube_volume_up": {
        "handler": youtube_volume_up,
        "description": "🔊 TĂNG ÂM LƯỢNG YOUTUBE - Triggers: 'tăng tiếng youtube', 'volume up youtube', 'tang am luong youtube'. ⚠️ 'tăng tiếng nhạc' → music_volume!",
        "parameters": {}
    },
    "youtube_volume_down": {
        "handler": youtube_volume_down,
        "description": "🔉 GIẢM ÂM LƯỢNG YOUTUBE - Triggers: 'giảm tiếng youtube', 'volume down youtube', 'giam am luong youtube'. ⚠️ 'giảm tiếng nhạc' → music_volume!",
        "parameters": {}
    },
    "youtube_mute": {
        "handler": youtube_mute,
        "description": "🔇 TẮT/BẬT TIẾNG YOUTUBE - Triggers: 'tắt tiếng youtube', 'mute youtube', 'bật tiếng youtube', 'tat tien youtube'.",
        "parameters": {}
    },
    "youtube_fullscreen": {
        "handler": youtube_fullscreen,
        "description": "📺 FULLSCREEN YOUTUBE - Triggers: 'fullscreen youtube', 'toàn màn hình', 'phóng to youtube', 'thu nhỏ youtube', 'toan man hinh'.",
        "parameters": {}
    },
    "youtube_captions": {
        "handler": youtube_captions,
        "description": "💬 BẬT/TẮT PHỤ ĐỀ YOUTUBE - Triggers: 'bật sub', 'tắt sub', 'bật phụ đề', 'tắt phụ đề', 'caption youtube', 'bat sub', 'tat sub'.",
        "parameters": {}
    },
    "youtube_speed": {
        "handler": youtube_speed,
        "description": "⚡ ĐỔI TỐC ĐỘ YOUTUBE - Triggers: 'youtube nhanh hơn', 'youtube chậm hơn', 'tăng tốc youtube'. faster=+0.25x | slower=-0.25x | normal=1x",
        "parameters": {
            "speed": {"type": "string", "description": "'faster', 'slower', 'normal'", "required": False}
        }
    },
    
    # VLC PLAYER CONTROLS
    "control_vlc": {
        "handler": control_vlc,
        "description": "🎵 Điều khiển VLC PLAYER. Actions: play_pause, stop, next, previous, volume_up/down, mute, fullscreen",
        "parameters": {
            "action": {
                "type": "string",
                "description": "Action điều khiển VLC",
                "required": True
            }
        }
    },
    "vlc_play_pause": {
        "handler": vlc_play_pause,
        "description": "⏯️ Play/Pause VLC Player. VD: 'dừng vlc', 'pause vlc', 'tiếp tục vlc'",
        "parameters": {}
    },
    "vlc_stop": {
        "handler": vlc_stop,
        "description": "⏹️ Dừng phát VLC hoàn toàn. VD: 'stop vlc', 'tắt nhạc vlc'",
        "parameters": {}
    },
    "vlc_next": {
        "handler": vlc_next,
        "description": "⏭️ Chuyển bài tiếp theo trong VLC. VD: 'bài tiếp vlc', 'next vlc', 'chuyển bài vlc'",
        "parameters": {}
    },
    "vlc_previous": {
        "handler": vlc_previous,
        "description": "⏮️ Quay lại bài trước trong VLC. VD: 'bài trước vlc', 'previous vlc'",
        "parameters": {}
    },
    "vlc_volume_up": {
        "handler": vlc_volume_up,
        "description": "🔊 Tăng âm lượng VLC. VD: 'tăng âm lượng vlc', 'vlc to hơn'",
        "parameters": {}
    },
    "vlc_volume_down": {
        "handler": vlc_volume_down,
        "description": "🔉 Giảm âm lượng VLC. VD: 'giảm âm lượng vlc', 'vlc nhỏ hơn'",
        "parameters": {}
    },
    "vlc_mute": {
        "handler": vlc_mute,
        "description": "🔇 Bật/Tắt tiếng VLC. VD: 'tắt tiếng vlc', 'mute vlc'",
        "parameters": {}
    },
    "vlc_forward": {
        "handler": vlc_forward,
        "description": "⏩ Tua tới trong VLC. Tự động chọn 3s/10s/60s. VD: 'tua tới vlc', 'skip vlc'",
        "parameters": {
            "seconds": {"type": "integer", "description": "Số giây tua tới (≤5→3s, ≤30→10s, >30→60s)", "required": False}
        }
    },
    "vlc_backward": {
        "handler": vlc_backward,
        "description": "⏪ Tua lùi trong VLC. Tự động chọn 3s/10s/60s. VD: 'lùi vlc', 'rewind vlc'",
        "parameters": {
            "seconds": {"type": "integer", "description": "Số giây tua lùi", "required": False}
        }
    },
    
    # ============================================================
    # WINDOWS MEDIA PLAYER CONTROLS
    # ============================================================
    "control_wmp": {
        "handler": control_wmp,
        "description": "🎶 Điều khiển Windows Media Player. Actions: play_pause, stop, next, previous, volume_up, volume_down, mute, fullscreen, forward, backward",
        "parameters": {
            "action": {"type": "string", "description": "Hành động điều khiển WMP", "required": True}
        }
    },
    "wmp_play_pause": {
        "handler": wmp_play_pause,
        "description": "⏯️ Play/Pause Windows Media Player. VD: 'dừng wmp', 'pause media player'",
        "parameters": {}
    },
    "wmp_stop": {
        "handler": wmp_stop,
        "description": "⏹️ Dừng Windows Media Player. VD: 'stop wmp', 'tắt media player'",
        "parameters": {}
    },
    "wmp_next": {
        "handler": wmp_next,
        "description": "⏭️ Bài tiếp theo trong Windows Media Player. VD: 'bài tiếp wmp', 'next media player'",
        "parameters": {}
    },
    "wmp_previous": {
        "handler": wmp_previous,
        "description": "⏮️ Bài trước trong Windows Media Player. VD: 'bài trước wmp', 'previous media player'",
        "parameters": {}
    },
    "wmp_volume_up": {
        "handler": wmp_volume_up,
        "description": "🔊 Tăng âm lượng Windows Media Player. VD: 'tăng âm lượng wmp'",
        "parameters": {}
    },
    "wmp_volume_down": {
        "handler": wmp_volume_down,
        "description": "🔉 Giảm âm lượng Windows Media Player. VD: 'giảm âm lượng wmp'",
        "parameters": {}
    },
    "wmp_mute": {
        "handler": wmp_mute,
        "description": "🔇 Bật/Tắt tiếng Windows Media Player. VD: 'tắt tiếng wmp', 'mute media player'",
        "parameters": {}
    },
    
    # ============================================================
    # SMART MEDIA CONTROL - Ưu tiên Python-VLC nội bộ
    # ============================================================
    "smart_media_control": {
        "handler": smart_media_control,
        "description": "🎵 [PYTHON-VLC ƯU TIÊN] Điều khiển nhạc - ƯU TIÊN PYTHON-VLC TRƯỚC, sau đó mới tới Spotify/WMP/YouTube. Actions: play_pause, stop, next, previous, volume_up, volume_down, mute. Nếu chưa phát nhạc, dùng play_music() trước!",
        "parameters": {
            "action": {
                "type": "string",
                "description": "Hành động: play_pause, stop, next, previous, volume_up, volume_down, mute",
                "required": True
            }
        }
    },
    
    # BROWSER AUTOMATION TOOLS
    "browser_open_url": {
        "handler": browser_open_url,
        "description": "Mở URL trong browser được điều khiển bởi Selenium (có thể tương tác với element). Khác với open_youtube/open_google là mở browser thông thường.",
        "parameters": {
            "url": {
                "type": "string",
                "description": "URL cần mở (VD: https://google.com, https://facebook.com)",
                "required": True
            }
        }
    },
    "browser_get_info": {
        "handler": browser_get_info,
        "description": "Lấy thông tin trang hiện tại (URL, title, số tab)",
        "parameters": {}
    },
    "browser_click": {
        "handler": browser_click,
        "description": "Click vào element trên trang web. Dùng để click button, link, etc.",
        "parameters": {
            "selector": {
                "type": "string",
                "description": "Selector để tìm element. VD: '#submit-btn', '.login-button', '//button[@id=\"login\"]'",
                "required": True
            },
            "by": {
                "type": "string",
                "description": "Loại selector: 'css' (default), 'xpath', 'id', 'name', 'class', 'tag'",
                "required": False
            }
        }
    },
    "browser_fill_input": {
        "handler": browser_fill_input,
        "description": "Điền text vào input field (form, search box, etc.)",
        "parameters": {
            "selector": {
                "type": "string",
                "description": "Selector của input field. VD: '#username', 'input[name=\"email\"]'",
                "required": True
            },
            "text": {
                "type": "string",
                "description": "Text cần điền vào input",
                "required": True
            },
            "by": {
                "type": "string",
                "description": "Loại selector: 'css' (default), 'xpath', 'id', 'name'",
                "required": False
            }
        }
    },
    "browser_scroll": {
        "handler": browser_scroll,
        "description": "Cuộn trang web lên/xuống",
        "parameters": {
            "direction": {
                "type": "string",
                "description": "Hướng cuộn: 'down' (default), 'up', 'top', 'bottom'",
                "required": False
            },
            "amount": {
                "type": "integer",
                "description": "Số pixel cuộn (nếu direction là down/up). Default: 500",
                "required": False
            }
        }
    },
    "browser_back": {
        "handler": browser_back,
        "description": "Quay lại trang trước trong browser",
        "parameters": {}
    },
    "browser_forward": {
        "handler": browser_forward,
        "description": "Tiến tới trang sau trong browser",
        "parameters": {}
    },
    "browser_refresh": {
        "handler": browser_refresh,
        "description": "Làm mới/reload trang hiện tại",
        "parameters": {}
    },
    "browser_screenshot": {
        "handler": browser_screenshot,
        "description": "Chụp screenshot trang web hiện tại",
        "parameters": {
            "filepath": {
                "type": "string",
                "description": "Đường dẫn lưu file (tùy chọn). VD: 'screenshot.png'. Mặc định: screenshot_YYYYMMDD_HHMMSS.png",
                "required": False
            }
        }
    },
    "browser_new_tab": {
        "handler": browser_new_tab,
        "description": "Mở tab mới trong browser",
        "parameters": {
            "url": {
                "type": "string",
                "description": "URL cần mở trong tab mới (tùy chọn)",
                "required": False
            }
        }
    },
    "browser_close_tab": {
        "handler": browser_close_tab,
        "description": "Đóng tab hiện tại",
        "parameters": {}
    },
    "browser_execute_js": {
        "handler": browser_execute_js,
        "description": "Thực thi JavaScript code trên trang web. Dùng cho các thao tác phức tạp.",
        "parameters": {
            "script": {
                "type": "string",
                "description": "JavaScript code cần chạy. VD: 'return document.title;', 'alert(\"Hello\");'",
                "required": True
            }
        }
    },
    "browser_close": {
        "handler": browser_close,
        "description": "Đóng browser hoàn toàn (đóng tất cả tab)",
        "parameters": {}
    },
    
    "open_facebook": {
        "handler": open_facebook, 
        "description": "Mở Facebook trong browser. Truy cập nhanh vào mạng xã hội phổ biến nhất.", 
        "parameters": {}
    },
    "open_google": {
        "handler": open_google, 
        "description": "MỞ TRÌNH DUYỆT Google. CHỈ dùng khi user YÊU CẦU MỞ TRANG WEB Google (ví dụ: 'mở google', 'mở trang google'). Nếu user chỉ HỎI CÂU HỎI thông thường, hãy dùng ask_gemini để TRẢ LỜI TRỰC TIẾP thay vì mở browser", 
        "parameters": {
            "search_query": {
                "type": "string", 
                "description": "Từ khóa tìm kiếm trên Google (tùy chọn). Để trống để mở trang chủ Google.", 
                "required": False
            }
        }
    },
    "open_tiktok": {
        "handler": open_tiktok, 
        "description": "Mở TikTok trong browser. Xem video ngắn trending và giải trí.", 
        "parameters": {}
    },
    "open_website": {
        "handler": open_website, 
        "description": "Mở trang web tùy chỉnh trong browser. Nhập URL đầy đủ hoặc tên miền.", 
        "parameters": {
            "url": {
                "type": "string", 
                "description": "URL của trang web (ví dụ: 'github.com' hoặc 'https://github.com/user/repo')", 
                "required": True
            }
        }
    },
    
    # YOUTUBE CONTROL TOOLS
    "control_youtube": {
        "handler": control_youtube, 
        "description": "Điều khiển YouTube player bằng keyboard shortcuts. Phải có cửa sổ YouTube đang active/focused. Hỗ trợ play/pause, tua video, điều chỉnh âm lượng, v.v.", 
        "parameters": {
            "action": {
                "type": "string", 
                "description": "Hành động điều khiển: play_pause, rewind_10, forward_10, rewind_5, forward_5, beginning, end, frame_back, frame_forward, volume_up, volume_down, mute_toggle", 
                "required": True
            }
        }
    },
    
    # NEWS TOOLS
    "get_vnexpress_news": {
        "handler": get_vnexpress_news,
        "description": "Lấy tin tức mới nhất từ VnExpress theo chủ đề. Trả về danh sách bài viết với tiêu đề, link, mô tả. Categories: home (mới nhất), thoi-su, the-gioi, kinh-doanh, giai-tri, the-thao, phap-luat, giao-duc, suc-khoe, du-lich, khoa-hoc, so-hoa, xe",
        "parameters": {
            "category": {
                "type": "string",
                "description": "Chủ đề tin tức: home, thoi-su, the-gioi, kinh-doanh, giai-tri, the-thao, phap-luat, giao-duc, suc-khoe, du-lich, khoa-hoc, so-hoa, xe. Mặc định: home",
                "required": False
            },
            "max_articles": {
                "type": "integer",
                "description": "Số lượng bài viết tối đa (1-20). Mặc định: 5",
                "required": False
            }
        }
    },
    "get_news_summary": {
        "handler": get_news_summary,
        "description": "Lấy tóm tắt nhanh tin tức (chỉ tiêu đề) từ VnExpress. Tự động lấy 10 tin mới nhất và hiển thị dạng danh sách ngắn gọn.",
        "parameters": {
            "category": {
                "type": "string",
                "description": "Chủ đề: home, thoi-su, the-gioi, kinh-doanh, giai-tri, the-thao, etc. Mặc định: home",
                "required": False
            }
        }
    },
    "search_news": {
        "handler": search_news,
        "description": "Tìm kiếm tin tức theo từ khóa trong các bài viết gần đây từ VnExpress. Tự động tìm trong nhiều chủ đề và trả về kết quả phù hợp nhất.",
        "parameters": {
            "keyword": {
                "type": "string",
                "description": "Từ khóa tìm kiếm (ví dụ: 'bóng đá', 'kinh tế', 'Covid', 'chính trị')",
                "required": True
            },
            "max_results": {
                "type": "integer",
                "description": "Số kết quả tối đa (1-10). Mặc định: 5",
                "required": False
            }
        }
    },
    "get_gold_price": {
        "handler": get_gold_price,
        "description": "Lấy giá vàng hôm nay từ BNews RSS feed. Hiển thị giá mua vào và bán ra của các loại vàng phổ biến (SJC, 9999, nhẫn tròn, v.v.). Tự động cập nhật giá mới nhất.",
        "parameters": {}
    },
    
    # AI ASSISTANT TOOLS
    "ask_gemini": {
        "handler": ask_gemini,
        "description": "✅ ƯU TIÊN DÙNG TOOL NÀY cho MỌI CÂU HỎI (MIỄN PHÍ 1500 requests/day). Gemini trả lời TRỰC TIẾP, NHANH, CHÍNH XÁC. Hữu ích cho: câu hỏi thông thường ('thủ tướng VN 2023 là ai', 'what is...', 'how to...'), phân tích, viết nội dung, dịch thuật, lịch sử, kiến thức tổng quát. Knowledge cutoff: ~10/2024 (đủ cho hầu hết câu hỏi). CHỈ dùng search_google_text nếu CẦN thông tin SAU 10/2024.",
        "parameters": {
            "prompt": {
                "type": "string",
                "description": "Câu hỏi hoặc nội dung muốn gửi cho Gemini AI",
                "required": True
            },
            "model": {
                "type": "string",
                "description": "Tên model Gemini (mặc định: models/gemini-2.0-flash-exp). Options: models/gemini-2.0-flash-exp (nhanh, miễn phí), models/gemini-exp-1206 (chất lượng cao hơn)",
                "required": False
            }
        }
    },
    
    "ask_gpt4": {
        "handler": ask_gpt4,
        "description": "TRẢ LỜI CÂU HỎI bằng OpenAI GPT-4 (TRẢ PHÍ, cần API key). DÙNG KHI CẦN: 1) Thông tin MỚI HƠN (knowledge đến 04/2024), 2) Phân tích PHỨC TẠP, 3) Reasoning SÂU, 4) Code generation chuyên nghiệp. GPT-4 MẠN HƠN Gemini cho code và phân tích, nhưng TRẢ PHÍ (~$0.01-0.03/1K tokens). Chọn GPT-4 khi cần chất lượng tối đa.",
        "parameters": {
            "prompt": {
                "type": "string",
                "description": "Câu hỏi hoặc nội dung muốn gửi cho GPT-4",
                "required": True
            },
            "model": {
                "type": "string",
                "description": "Tên model OpenAI (mặc định: gpt-4o). Options: gpt-4o (GPT-4 Omni, nhanh & rẻ nhất), gpt-4-turbo (mạnh nhất), gpt-3.5-turbo (rẻ & nhanh)",
                "required": False
            }
        }
    },
    
    # NEW TOOLS FROM REFERENCE
    "lock_computer": {"handler": lock_computer, "description": "Khóa máy tính", "parameters": {}},
    "shutdown_schedule": {"handler": shutdown_schedule, "description": "Lên lịch tắt máy", "parameters": {"action": {"type": "string", "description": "shutdown/restart/cancel", "required": True}, "delay": {"type": "integer", "description": "Trì hoãn (giây)", "required": False}}},
    "show_desktop": {"handler": show_desktop, "description": "Hiển thị desktop (Win+D)", "parameters": {}},
    "undo_operation": {"handler": undo_operation, "description": "Hoàn tác (Ctrl+Z)", "parameters": {}},
    "set_theme": {"handler": set_theme, "description": "Đổi theme Windows", "parameters": {"dark_mode": {"type": "boolean", "description": "True=tối, False=sáng", "required": False}}},
    "change_wallpaper": {"handler": change_wallpaper, "description": "Đổi hình nền", "parameters": {"keyword": {"type": "string", "description": "Từ khóa (phong cảnh, anime...)", "required": False}}},
    "get_desktop_path": {"handler": get_desktop_path, "description": "Lấy đường dẫn Desktop", "parameters": {}},
    "paste_content": {"handler": paste_content, "description": "Dán nội dung (Ctrl+V)", "parameters": {"content": {"type": "string", "description": "Nội dung cần dán (tùy chọn)", "required": False}}},
    "press_enter": {"handler": press_enter, "description": "Nhấn Enter", "parameters": {}},
    "save_text_to_file": {
        "handler": save_text_to_file,
        "description": "LƯU VĂN BẢN do LLM soạn thành FILE. Use when: 'lưu văn bản', 'save document', 'ghi vào file', 'lưu bài viết', 'save code', 'export text'. LLM có thể soạn bài viết/báo cáo/code dài và lưu trực tiếp. File tự động lưu vào Documents\\miniZ_LLM_Documents\\ với tên có timestamp. Examples: Soạn CV→lưu file, viết báo cáo→lưu file, tạo code→lưu file.",
        "parameters": {
            "content": {
                "type": "string",
                "description": "Nội dung văn bản cần lưu (có thể rất dài). Hỗ trợ Unicode tiếng Việt, code, markdown, v.v.",
                "required": True
            },
            "filename": {
                "type": "string",
                "description": "Tên file (optional). Ví dụ: 'bao_cao.txt', 'code.py', 'cv.md'. Nếu không có, tự động tạo tên với timestamp.",
                "required": False
            }
        }
    },
    "text_to_speech": {
        "handler": text_to_speech,
        "description": "TEXT-TO-SPEECH (TTS): Đọc văn bản thành GIỌNG NÓI. Use when: 'đọc văn bản', 'text to speech', 'đọc cho tôi nghe', 'phát âm', 'nói ra'. Dùng Windows SAPI voice (có sẵn). Có thể lưu thành file WAV. Examples: 'đọc bài viết này', 'đọc và lưu audio', 'text to speech tiếng Việt'.",
        "parameters": {
            "text": {
                "type": "string",
                "description": "Văn bản cần đọc. Hỗ trợ tiếng Việt và tiếng Anh.",
                "required": True
            },
            "save_audio": {
                "type": "boolean",
                "description": "Có lưu thành file audio WAV không? (True/False). Mặc định False (chỉ đọc không lưu).",
                "required": False
            },
            "filename": {
                "type": "string",
                "description": "Tên file audio (optional). VD: 'doc_van_ban.wav'. Nếu không có, tự động tạo tên.",
                "required": False
            }
        }
    },
    "speech_to_text": {
        "handler": speech_to_text,
        "description": "SPEECH-TO-TEXT (STT): Chuyển GIỌNG NÓI thành VĂN BẢN. Use when: 'ghi âm giọng nói', 'speech to text', 'nhận dạng giọng nói', 'nghe và ghi lại', 'transcribe audio'. Dùng Google Speech Recognition (cần Internet). Hỗ trợ tiếng Việt + English. Examples: 'ghi âm 10 giây', 'nhận dạng giọng nói của tôi', 'speech to text'.",
        "parameters": {
            "duration": {
                "type": "integer",
                "description": "Thời gian ghi âm (giây). Mặc định 5 giây. VD: 10 để ghi âm 10 giây.",
                "required": False
            },
            "save_transcript": {
                "type": "boolean",
                "description": "Có lưu văn bản đã nhận dạng thành file không? (True/False). Mặc định True.",
                "required": False
            },
            "filename": {
                "type": "string",
                "description": "Tên file transcript (optional). VD: 'ghi_chu.txt'. Tự động tạo nếu không có.",
                "required": False
            }
        }
    },
    "export_conversation": {
        "handler": export_conversation_to_file,
        "description": "EXPORT LỊCH SỬ HỘI THOẠI ra file JSON. Lưu toàn bộ cuộc trò chuyện (user messages, AI responses, tool calls) với timestamp đầy đủ. Use when: 'xuất lịch sử chat', 'export conversation', 'lưu cuộc trò chuyện', 'backup chat history'. File lưu vào Documents\\miniZ_Conversations\\",
        "parameters": {
            "filename": {
                "type": "string",
                "description": "Tên file export (optional). VD: 'chat_history.json'. Tự động tạo tên với timestamp nếu không có.",
                "required": False
            }
        }
    },
    "find_in_document": {"handler": find_in_document, "description": "Tìm trong tài liệu (Ctrl+F)", "parameters": {"search_text": {"type": "string", "description": "Nội dung tìm kiếm", "required": True}}},
    
    # ============================================================
    # CONVERSATION HISTORY TOOLS - Lưu & Hiểu người dùng
    # ============================================================
    
    "get_user_context": {
        "handler": lambda: {
            "success": True,
            "user_profile": get_user_profile_summary(),
            "recent_conversation": get_conversation_context(10),
            "hint": "Dùng thông tin này để hiểu người dùng tốt hơn"
        },
        "description": "📚 LẤY CONTEXT NGƯỜI DÙNG - Trả về lịch sử hội thoại gần đây + user profile (chủ đề quan tâm, giờ hoạt động). Dùng để hiểu người dùng tốt hơn trước khi trả lời.",
        "parameters": {}
    },
    
    "save_user_message": {
        "handler": lambda message, context="": (
            add_to_conversation("user", message, {"source": "robot", "context": context}),
            {"success": True, "message": "Đã lưu tin nhắn người dùng"}
        )[1],
        "description": "💾 LƯU TIN NHẮN NGƯỜI DÙNG - Lưu toàn bộ tin nhắn người dùng vào lịch sử (kể cả không gọi tool). QUAN TRỌNG: Gọi tool này để lưu mọi câu hỏi/tin nhắn của user!",
        "parameters": {
            "message": {
                "type": "string",
                "description": "Nội dung tin nhắn của người dùng",
                "required": True
            },
            "context": {
                "type": "string",
                "description": "Context bổ sung (VD: người dùng đang nói về gì)",
                "required": False
            }
        }
    },
    
    "save_assistant_response": {
        "handler": lambda response, tool_used="": (
            add_to_conversation("assistant", response, {"source": "robot", "tool_used": tool_used}),
            {"success": True, "message": "Đã lưu response của AI"}
        )[1],
        "description": "💾 LƯU RESPONSE CỦA AI - Lưu câu trả lời của AI vào lịch sử. Gọi tool này sau khi trả lời xong để lưu lại!",
        "parameters": {
            "response": {
                "type": "string",
                "description": "Nội dung response của AI",
                "required": True
            },
            "tool_used": {
                "type": "string",
                "description": "Tool đã dùng để tạo response (nếu có)",
                "required": False
            }
        }
    },
    
    "list_conversation_files": {
        "handler": list_conversation_files,
        "description": "📂 LIỆT KÊ CÁC FILE HỘI THOẠI - Xem danh sách các file lịch sử hội thoại đã lưu theo ngày.",
        "parameters": {}
    },
    
    # ============================================================
    # OPEN API TOOLS - PHÙ HỢP VIỆT NAM
    # ============================================================
    
    "get_weather_vietnam": {
        "handler": get_weather_vietnam,
        "description": "🌤️ LẤY THỜI TIẾT VIỆT NAM. Hỗ trợ: Hà Nội, Hồ Chí Minh, Đà Nẵng, Hải Phòng, Cần Thơ, Nha Trang, Huế, Đà Lạt, Vũng Tàu, Quảng Ninh... Triggers: 'thời tiết', 'weather', 'trời hôm nay', 'nhiệt độ'.",
        "parameters": {
            "city": {
                "type": "string",
                "description": "Tên thành phố VN. VD: 'Hà Nội', 'Hồ Chí Minh', 'Đà Nẵng'. Mặc định: Hà Nội",
                "required": False
            }
        }
    },
    
    "get_gold_price_vietnam": {
        "handler": get_gold_price_vietnam,
        "description": "💰 GIÁ VÀNG VIỆT NAM hôm nay (SJC, PNJ...). Triggers: 'giá vàng', 'gold price', 'vàng hôm nay'.",
        "parameters": {}
    },
    
    "get_exchange_rate_vietnam": {
        "handler": get_exchange_rate_vietnam,
        "description": "💱 TỶ GIÁ NGOẠI TỆ so với VNĐ. Hỗ trợ: USD, EUR, JPY, GBP, CNY, KRW... Triggers: 'tỷ giá', 'exchange rate', 'đô la bao nhiêu'.",
        "parameters": {
            "currency": {
                "type": "string",
                "description": "Mã ngoại tệ (USD, EUR, JPY...). Mặc định: USD",
                "required": False
            }
        }
    },
    
    "get_fuel_price_vietnam": {
        "handler": get_fuel_price_vietnam,
        "description": "⛽ GIÁ XĂNG DẦU VIỆT NAM (RON 95, E5 RON 92, Diesel). Triggers: 'giá xăng', 'fuel price', 'xăng bao nhiêu'.",
        "parameters": {}
    },
    
    "get_daily_quote": {
        "handler": get_daily_quote,
        "description": "💬 CÂU NÓI HAY / TRÍCH DẪN ngẫu nhiên. Có quotes tiếng Việt và tiếng Anh. Triggers: 'câu nói hay', 'quote', 'danh ngôn', 'trích dẫn'.",
        "parameters": {}
    },
    
    "get_joke": {
        "handler": get_joke,
        "description": "😂 CHUYỆN CƯỜI tiếng Việt. Triggers: 'kể chuyện cười', 'joke', 'hài hước', 'vui vẻ', 'giải trí'.",
        "parameters": {}
    },
    
    "get_horoscope": {
        "handler": get_horoscope,
        "description": "🔮 TỬ VI / HOROSCOPE theo cung hoàng đạo. Triggers: 'tử vi', 'horoscope', 'cung hoàng đạo', 'xem vận mệnh'.",
        "parameters": {
            "zodiac": {
                "type": "string",
                "description": "Cung hoàng đạo (Bạch Dương, Kim Ngưu, Song Tử, Cự Giải, Sư Tử, Xử Nữ, Thiên Bình, Bọ Cạp, Nhân Mã, Ma Kết, Bảo Bình, Song Ngư)",
                "required": False
            }
        }
    },
    
    "get_today_in_history": {
        "handler": get_today_in_history,
        "description": "📜 SỰ KIỆN LỊCH SỬ ngày hôm nay. Triggers: 'lịch sử ngày này', 'today in history', 'ngày này năm xưa'.",
        "parameters": {}
    },
    
    "get_news_vietnam": {
        "handler": get_news_vietnam,
        "description": "📰 TIN TỨC MỚI NHẤT Việt Nam (VnExpress, Tuổi Trẻ). Triggers: 'tin tức', 'news', 'tin mới', 'đọc báo'.",
        "parameters": {}
    },
    
    "what_to_eat": {
        "handler": what_to_eat,
        "description": "🍽️ GỢI Ý MÓN ĂN hôm nay (ẩm thực Việt Nam). Triggers: 'ăn gì', 'gợi ý món ăn', 'what to eat', 'đói bụng'.",
        "parameters": {}
    },
    
    "get_lunar_date": {
        "handler": get_lunar_date,
        "description": "📅 NGÀY ÂM LỊCH hôm nay. Triggers: 'âm lịch', 'lunar date', 'ngày mấy âm'.",
        "parameters": {}
    },
    
    # KNOWLEDGE BASE TOOLS
    "search_knowledge_base": {
        "handler": search_knowledge_base,
        "description": "🔍 TÌM KIẾM TRONG TÀI LIỆU CỦA USER (TF-IDF Ranking). ⚡ Dùng khi user hỏi về dữ liệu riêng/tài liệu của họ. Hỗ trợ: Multi-keyword search, relevance scoring, snippet highlighting. Triggers: 'tìm trong tài liệu', 'tìm trong file của tôi', 'tra cứu dữ liệu', 'search my documents', 'tìm thông tin về...'. VD: 'tìm trong tài liệu về hợp đồng mua bán', 'tra cứu thông tin khách hàng Nguyễn Văn A'. Trả về: Top 5 documents có độ liên quan cao nhất với score, matched keywords, và snippets.",
        "parameters": {
            "query": {
                "type": "string",
                "description": "Từ khóa/câu hỏi cần tìm. Có thể dùng nhiều từ khóa. VD: 'hợp đồng mua bán 2024', 'thông tin khách hàng', 'báo cáo tài chính quý 3'",
                "required": True
            }
        }
    },
    "get_knowledge_context": {
        "handler": get_knowledge_context,
        "description": "📚 LẤY CONTEXT ĐẦY ĐỦ TỮ TÀI LIỆU ĐỂ TRẢ LỜI (Semantic Ranking). ⚡ GỌI TOOL NÀY ĐẦU TIÊN khi user hỏi về dữ liệu của họ! Tool này lấy nội dung đầy đủ từ top documents liên quan nhất, sau đó LLM dùng context đó để trả lời. Triggers: 'hỏi về tài liệu', 'thông tin trong file', 'theo dữ liệu của tôi', 'based on my docs', 'what does my document say about...'. QUY TRÌNH: 1) Gọi get_knowledge_context(query='...') 2) Nhận context 3) Dùng context để trả lời user. VD: User hỏi 'Dự án ABC có bao nhiêu giai đoạn?' → Gọi get_knowledge_context(query='dự án ABC giai đoạn') → Nhận context → Trả lời dựa trên context.",
        "parameters": {
            "query": {
                "type": "string",
                "description": "Câu hỏi/chủ đề cần context. Nên dùng keywords từ câu hỏi của user. VD: 'dự án ABC', 'hợp đồng khách hàng X', 'báo cáo tài chính quý 3 2024'. Càng cụ thể càng tốt!",
                "required": False
            },
            "max_chars": {
                "type": "integer",
                "description": "Giới hạn ký tự (default: 10000). Tăng lên nếu cần nhiều context hơn. VD: 20000 cho câu hỏi phức tạp",
                "required": False
            }
        }
    },
    
    # =====================================================
    # 🔍 RAG SYSTEM - RETRIEVAL AUGMENTED GENERATION
    # =====================================================
    
    "web_search": {
        "handler": web_search if RAG_AVAILABLE else None,
        "description": "🌐⚡ TÌM KIẾM WEB (DuckDuckGo) - ⛔ BẮT BUỘC GỌI KHI HỎI VỀ: tổng thống/thủ tướng/CEO, giá vàng/USD/bitcoin, thời tiết, tin tức, sự kiện 2024-2025, 'ai là', 'là ai'. ⚠️ CẢNH BÁO: Kiến thức của bạn LỖI THỜI, PHẢI tra cứu! Query nên thêm '2024' hoặc 'mới nhất'. VD: 'tổng thống Mỹ 2024', 'giá vàng SJC hôm nay'.",
        "parameters": {
            "query": {
                "type": "string",
                "description": "Từ khóa tìm kiếm (nên thêm năm hoặc 'mới nhất')",
                "required": True
            },
            "max_results": {
                "type": "integer",
                "description": "Số kết quả tối đa (mặc định 5)",
                "required": False
            }
        }
    },
    
    "get_realtime_info": {
        "handler": get_realtime_info if RAG_AVAILABLE else None,
        "description": "⚡⚡ THÔNG TIN THỜI GIAN THỰC - ⛔⛔ BẮT BUỘC GỌI TRƯỚC MỌI CÂU TRẢ LỜI về: giá cả, tỷ giá, thời tiết, người nổi tiếng, chức vụ hiện tại, sự kiện đang xảy ra. ❌ KHÔNG BAO GIỜ tự trả lời bằng kiến thức cũ! ✅ GỌI TOOL NÀY TRƯỚC → nhận kết quả → rồi trả lời user.",
        "parameters": {
            "query": {
                "type": "string",
                "description": "Câu hỏi cần thông tin thời gian thực",
                "required": True
            }
        }
    },
    
    "rag_search": {
        "handler": rag_search if RAG_AVAILABLE else None,
        "description": "🔍 RAG SEARCH HYBRID - Tìm kiếm KẾT HỢP từ Internet + Tài liệu nội bộ. Tự động chọn nguồn phù hợp nhất. sources='web' cho Internet, 'local' cho tài liệu nội bộ, 'hybrid' cho cả hai, 'auto' để AI tự chọn.",
        "parameters": {
            "query": {
                "type": "string",
                "description": "Câu hỏi hoặc từ khóa tìm kiếm",
                "required": True
            },
            "sources": {
                "type": "string",
                "description": "Nguồn: 'auto', 'web', 'local', 'hybrid' (mặc định: auto)",
                "required": False
            },
            "max_results": {
                "type": "integer",
                "description": "Số kết quả tối đa (mặc định 8)",
                "required": False
            }
        }
    },
    
    "smart_answer": {
        "handler": smart_answer if RAG_AVAILABLE else None,
        "description": "🧠 SMART ANSWER - AI tự động phân tích câu hỏi và chọn nguồn TỐT NHẤT (Internet/Tài liệu nội bộ/Hybrid) để trả lời. Dùng khi không chắc nguồn nào phù hợp. Tool trả về context đã tối ưu để trả lời.",
        "parameters": {
            "query": {
                "type": "string",
                "description": "Câu hỏi của user",
                "required": True
            }
        }
    }
}

# ============================================================
# MINIZ MCP CLIENT
# ============================================================

def get_vlc_context_for_llm() -> str:
    """Tạo context về VLC status để gửi cho LLM"""
    try:
        if vlc_player and vlc_player._player:
            status = vlc_player.get_full_status()
            is_playing = status.get('is_playing', False)
            current_track = status.get('current_track', 'Không có')
            volume = status.get('volume', 0)
            playlist_count = status.get('playlist_count', 0)
            
            context = f"""
📍 [PYTHON-VLC STATUS]
• Trạng thái: {'▶️ Đang phát' if is_playing else '⏸️ Tạm dừng/Dừng'}
• Bài hiện tại: {current_track}
• Âm lượng: {volume}%
• Playlist: {playlist_count} bài
• Player: Python-VLC (nội bộ)

🎯 Dùng smart_music_control() cho mọi lệnh nhạc!"""
            return context
        else:
            return """
📍 [PYTHON-VLC STATUS]
• Trạng thái: ⏹️ Chưa khởi tạo/Chưa phát
• Dùng play_music() hoặc list_music() để bắt đầu phát nhạc
• Player: Python-VLC (sẵn sàng)"""
    except:
        return ""

async def handle_xiaozhi_message(message: dict) -> dict:
    method = message.get("method")
    params = message.get("params", {})
    
    if method == "initialize":
        # Trả về với instructions + VLC context
        vlc_context = get_vlc_context_for_llm()
        full_instructions = MUSIC_SYSTEM_PROMPT + vlc_context
        
        return {
            "protocolVersion": "2024-11-05", 
            "capabilities": {"tools": {}}, 
            "serverInfo": {"name": "xiaozhi-final", "version": "4.3.0"},
            "instructions": full_instructions
        }
    elif method == "tools/list":
        # Support cursor pagination (từ xiaozhi-esp32-server)
        cursor = params.get("cursor", "")
        tools = []
        for name, info in TOOLS.items():
            # Sanitize tool name để tương thích với server chính thức
            sanitized_name = sanitize_tool_name(name) if 'sanitize_tool_name' in dir() else name
            tool = {
                "name": name,  # Giữ nguyên tên gốc để handler hoạt động
                "description": info["description"], 
                "inputSchema": {"type": "object", "properties": {}, "required": []}
            }
            for pname, pinfo in info["parameters"].items():
                tool["inputSchema"]["properties"][pname] = {"type": pinfo["type"], "description": pinfo["description"]}
                if pinfo.get("required"):
                    tool["inputSchema"]["required"].append(pname)
            tools.append(tool)
        
        # Log số lượng tools
        print(f"📋 [tools/list] Returning {len(tools)} tools to robot")
        
        # Response theo format chuẩn với optional nextCursor
        return {"tools": tools}  # nextCursor sẽ được thêm nếu cần pagination
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        print(f"🔧 [Tool Call] {tool_name} with args: {args}")
        
        # Lưu tool call vào history
        add_to_conversation(
            role="tool",
            content=f"Tool: {tool_name}",
            metadata={
                "tool_name": tool_name,
                "arguments": args,
                "event_type": "tool_call"
            }
        )
        
        if tool_name not in TOOLS:
            error_msg = f"Error: Tool '{tool_name}' not found"
            print(f"❌ {error_msg}")
            add_to_conversation(role="tool", content=error_msg, metadata={"error": True})
            return {"content": [{"type": "text", "text": error_msg}], "isError": True}
        
        # Retry mechanism (từ xiaozhi-esp32-server)
        max_retries = MAX_TOOL_RETRIES
        retry_interval = TOOL_RETRY_INTERVAL
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = await TOOLS[tool_name]["handler"](**args)
                print(f"✅ [Tool Result] {tool_name}: {result}")
                
                # Thêm VLC context vào music-related tools
                music_tools = ['smart_music_control', 'play_music', 'pause_music', 'resume_music', 
                              'stop_music', 'music_next', 'music_previous', 'music_volume', 
                              'get_music_status', 'list_music', 'search_music', 'detect_and_execute_music']
                if tool_name in music_tools:
                    result["_vlc_hint"] = "🎵 Đang dùng Python-VLC Player nội bộ. Tiếp tục dùng smart_music_control() cho các lệnh nhạc tiếp theo."
                
                # Lưu tool result vào history
                add_to_conversation(
                    role="tool",
                    content=json.dumps(result, ensure_ascii=False),
                    metadata={
                        "tool_name": tool_name,
                        "success": result.get("success", True),
                        "event_type": "tool_result",
                        "attempt": attempt + 1
                    }
                )
                
                return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"⚠️ [Tool Retry] {tool_name} failed (attempt {attempt + 1}/{max_retries}): {e}")
                    await asyncio.sleep(retry_interval)
                else:
                    error_msg = f"Error calling {tool_name} after {max_retries} attempts: {str(e)}"
                    print(f"❌ {error_msg}")
                    import traceback
                    traceback.print_exc()
                    add_to_conversation(role="tool", content=error_msg, metadata={"error": True})
                    return {"content": [{"type": "text", "text": error_msg}], "isError": True}
    return {"error": f"Unknown method: {method}"}

async def xiaozhi_websocket_client():
    global xiaozhi_connected, xiaozhi_ws, should_reconnect, active_endpoint_index
    retry = 0
    
    # ===== OPTIMIZED CONNECTION SETTINGS =====
    INITIAL_DELAY = 1        # Delay ban đầu 1s (giảm từ 2s)
    MAX_DELAY = 15           # Max delay 15s (giảm từ 60s)
    CONNECT_TIMEOUT = 10     # Timeout kết nối 10s
    FAST_RETRY_COUNT = 3     # Số lần fast retry đầu tiên
    FAST_RETRY_DELAY = 0.5   # Delay 0.5s cho fast retry
    AUTO_SWITCH_THRESHOLD = 5  # Sau 5 lần thất bại, thử endpoint khác
    
    while True:
        try:
            ep = endpoints_config[active_endpoint_index]
            if not ep.get("enabled") or not ep.get("token"):
                # Thử tìm endpoint khác có token
                found_valid = False
                for i, other_ep in enumerate(endpoints_config):
                    if other_ep.get("enabled") and other_ep.get("token") and i != active_endpoint_index:
                        print(f"🔄 [Xiaozhi] Switching to {other_ep['name']} (current endpoint has no token)")
                        active_endpoint_index = i
                        found_valid = True
                        break
                if not found_valid:
                    await asyncio.sleep(5)
                    continue
                ep = endpoints_config[active_endpoint_index]
            
            ws_url = f"wss://api.xiaozhi.me/mcp/?token={ep['token']}"
            retry += 1
            
            # Auto-switch endpoint nếu thất bại quá nhiều lần
            if retry > AUTO_SWITCH_THRESHOLD:
                for i, other_ep in enumerate(endpoints_config):
                    if other_ep.get("enabled") and other_ep.get("token") and i != active_endpoint_index:
                        print(f"⚠️ [Xiaozhi] Too many failures, trying {other_ep['name']}...")
                        active_endpoint_index = i
                        retry = 0  # Reset retry cho endpoint mới
                        ep = other_ep
                        ws_url = f"wss://api.xiaozhi.me/mcp/?token={ep['token']}"
                        break
            
            # Fast retry cho 3 lần đầu, sau đó dùng exponential backoff
            if retry <= FAST_RETRY_COUNT:
                print(f"📡 [Xiaozhi] Fast connecting {ep['name']}... ({retry}/{FAST_RETRY_COUNT})")
            else:
                print(f"📡 [Xiaozhi] Connecting {ep['name']}... (retry {retry})")
            
            # Sử dụng asyncio.wait_for để có timeout
            async with websockets.connect(
                ws_url, 
                ping_interval=20, 
                ping_timeout=10,
                close_timeout=5,
                open_timeout=CONNECT_TIMEOUT  # Timeout mở kết nối
            ) as ws:
                xiaozhi_ws = ws
                xiaozhi_connected = True
                should_reconnect = False  # Reset flag khi kết nối thành công
                retry = 0  # Reset retry counter khi kết nối thành công
                print(f"✅ [Xiaozhi] Connected! ({ep['name']})")
                
                # Batch broadcast kết nối - tạo tasks và chạy parallel
                broadcast_msg = {"type": "endpoint_connected", "endpoint": ep['name'], "index": active_endpoint_index}
                tasks = []
                for conn in active_connections:
                    tasks.append(asyncio.create_task(conn.send_json(broadcast_msg)))
                # Chạn tất cả broadcasts cùng lúc
                await asyncio.gather(*tasks, return_exceptions=True)
                
                init_msg = {"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "xiaozhi-final", "version": "4.3.0"}}, "id": 1}
                
                # Không log initialize request - chỉ log tool calls thực sự
                
                await ws.send(json.dumps(init_msg))
                
                async for msg in ws:
                    # Kiểm tra nếu cần reconnect (user đã chuyển thiết bị)
                    if should_reconnect:
                        print(f"🔄 [Xiaozhi] Reconnecting to new endpoint...")
                        await ws.close()
                        break
                    
                    try:
                        data = json.loads(msg)
                        method = data.get("method", "unknown")
                        if method != "ping":
                            print(f"📨 [{method}]")
                        
                        response = await handle_xiaozhi_message(data)
                        
                        # CHỈ log conversation thực sự (tools/call), KHÔNG log MCP protocol messages
                        # Bỏ qua: initialize, notifications/initialized, tools/list
                        if method == "tools/call" and method != "ping":
                            # Lấy thông tin tool
                            params = data.get("params", {})
                            tool_name = params.get("name", "unknown")
                            tool_args = params.get("arguments", {})
                            
                            # Tạo nội dung dễ đọc từ tool arguments
                            user_message = format_tool_request(tool_name, tool_args)
                            
                            # Log tool call request
                            add_to_conversation(
                                role="user",
                                content=user_message,
                                metadata={
                                    "source": "mcp",
                                    "method": method,
                                    "tool_name": tool_name,
                                    "tool_arguments": tool_args,
                                    "endpoint": ep['name']
                                }
                            )
                            
                            # Tạo nội dung response dễ đọc
                            assistant_message = format_tool_response(tool_name, response)
                            
                            # Log tool call response
                            add_to_conversation(
                                role="assistant",
                                content=assistant_message,
                                metadata={
                                    "source": "mcp",
                                    "method": method,
                                    "tool_name": tool_name,
                                    "response_data": response,
                                    "success": not isinstance(response, dict) or not response.get("isError")
                                }
                            )
                        
                        await ws.send(json.dumps({"jsonrpc": "2.0", "id": data.get("id"), "result": response}))

                        # If the tool response suggests a next_action (for example list_music
                        # returning {'next_action': {'tool': 'play_music', 'parameters': {...}}}),
                        # execute it locally on the server as a fallback so music actually plays
                        # even if the remote AI/client doesn't invoke the follow-up.
                        try:
                            if isinstance(response, dict) and response.get("next_action"):
                                na = response.get("next_action")
                                next_tool = na.get("tool")
                                next_params = na.get("parameters", {}) or {}
                                # Only execute if the tool exists locally
                                if next_tool and next_tool in TOOLS:
                                    print(f"⏯️ [Auto Action] Executing suggested next_action {next_tool} with params: {next_params}")
                                    try:
                                        # call the handler (handlers may be async)
                                        handler = TOOLS[next_tool]["handler"]
                                        if asyncio.iscoroutinefunction(handler):
                                            res2 = await handler(**next_params)
                                        else:
                                            # run sync handlers in executor
                                            loop = asyncio.get_event_loop()
                                            res2 = await loop.run_in_executor(None, lambda: handler(**next_params))
                                        print(f"⏯️ [Auto Action Result] {next_tool}: {res2}")
                                    except Exception as e:
                                        print(f"❌ [Auto Action] Error executing {next_tool}: {e}")
                                        import traceback
                                        traceback.print_exc()
                        except Exception:
                            # defensive: do not let auto-action failures disrupt websocket loop
                            import traceback
                            traceback.print_exc()
                        
                        # Batch broadcast - chỉ broadcast cho methods quan trọng
                        if method in ["tools/call", "initialize"]:
                            broadcast_msg = {"type": "xiaozhi_activity", "method": method, "timestamp": datetime.now().isoformat()}
                            # Cleanup dead connections trước khi broadcast
                            dead_connections = []
                            for conn in active_connections:
                                try:
                                    await conn.send_json(broadcast_msg)
                                except Exception:
                                    dead_connections.append(conn)
                            # Remove dead connections
                            for conn in dead_connections:
                                active_connections.remove(conn)
                    except json.JSONDecodeError as e:
                        print(f"⚠️ [Xiaozhi] JSON decode error: {e}")
                    except Exception as e:
                        print(f"⚠️ [Xiaozhi] Message handling error: {e}")
        except websockets.exceptions.WebSocketException as e:
            xiaozhi_connected = False
            # Fast retry cho 3 lần đầu
            if retry <= FAST_RETRY_COUNT:
                wait = FAST_RETRY_DELAY
            else:
                # Exponential backoff với max 15s
                wait = min(INITIAL_DELAY * (2 ** min(retry - FAST_RETRY_COUNT, 4)), MAX_DELAY)
            print(f"❌ [Xiaozhi] WebSocket error: {e} (retry in {wait}s)")
            await asyncio.sleep(wait)
        except Exception as e:
            xiaozhi_connected = False
            # Fast retry cho 3 lần đầu
            if retry <= FAST_RETRY_COUNT:
                wait = FAST_RETRY_DELAY
            else:
                wait = min(INITIAL_DELAY * (2 ** min(retry - FAST_RETRY_COUNT, 4)), MAX_DELAY)
            print(f"❌ [Xiaozhi] Error: {e} (retry in {wait}s)")
            await asyncio.sleep(wait)

# ============================================================
# FASTAPI WEB SERVER
# ============================================================

app = FastAPI(title="miniZ MCP", version="4.3.0")

class VolumeRequest(BaseModel):
    level: int

class NotificationRequest(BaseModel):
    title: str
    message: str

class CalculatorRequest(BaseModel):
    expression: str

@app.get("/", response_class=HTMLResponse)
async def index():
    html = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 miniZ MCP - Điều Khiển Máy Tính</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; }
        
        /* SIDEBAR */
        .sidebar { width: 280px; background: #1a1a2e; color: white; padding: 30px 20px; display: flex; flex-direction: column; box-shadow: 2px 0 20px rgba(0,0,0,0.3); }
        .logo { 
            font-size: 1.5em; 
            font-weight: bold; 
            margin-bottom: 40px; 
            text-align: center; 
            padding: 20px 15px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 15px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
        }
        .logo-icon {
            width: 120px;
            height: auto;
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
            transition: transform 0.3s;
        }
        .logo-icon:hover {
            transform: scale(1.05);
        }
        .logo-text {
            font-size: 1.8em;
            font-weight: 900;
            letter-spacing: 2px;
            color: #ff9a8b;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .menu-item { padding: 15px 20px; margin: 8px 0; border-radius: 10px; cursor: pointer; transition: all 0.3s; display: flex; align-items: center; gap: 12px; font-size: 1.05em; }
        .menu-item:hover { background: rgba(102, 126, 234, 0.2); transform: translateX(5px); }
        .menu-item.active { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }
        
        /* MAIN CONTENT */
        .main-content { flex: 1; padding: 30px; overflow-y: auto; }
        .header { background: white; border-radius: 15px; padding: 25px 30px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); display: flex; justify-content: space-between; align-items: center; }
        .header h1 { color: #667eea; font-size: 2em; }
        .status { display: flex; gap: 20px; }
        .status-badge { padding: 8px 20px; border-radius: 20px; font-weight: 600; display: flex; align-items: center; gap: 8px; }
        .status-badge.online { background: #d4edda; color: #155724; }
        .status-badge.offline { background: #f8d7da; color: #721c24; }
        .status-dot { width: 10px; height: 10px; border-radius: 50%; background: currentColor; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        
        /* QUICK ACTIONS */
        .quick-actions { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .action-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); cursor: pointer; transition: all 0.3s; text-align: center; }
        .action-card:hover { transform: translateY(-5px); box-shadow: 0 15px 40px rgba(0,0,0,0.2); }
        .action-card.blue { border-left: 5px solid #3b82f6; }
        .action-card.green { border-left: 5px solid #10b981; }
        .action-card.orange { border-left: 5px solid #f59e0b; }
        .action-card.red { border-left: 5px solid #ef4444; }
        .action-card.purple { border-left: 5px solid #8b5cf6; }
        .action-card.cyan { border-left: 5px solid #06b6d4; }
        .action-card.pink { border-left: 5px solid #ec4899; }
        .action-card.indigo { border-left: 5px solid #6366f1; }
        .action-card .icon { font-size: 2.5em; margin-bottom: 10px; }
        .action-card .title { font-weight: 600; color: #333; font-size: 1.1em; }
        
        /* TOOLS SECTION */
        .tools-section { background: white; border-radius: 15px; padding: 30px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .tools-tabs { display: flex; gap: 15px; margin-bottom: 25px; border-bottom: 2px solid #e5e7eb; padding-bottom: 15px; }
        .tab-btn { padding: 12px 30px; border: none; border-radius: 10px 10px 0 0; background: transparent; color: #666; font-weight: 600; cursor: pointer; transition: all 0.3s; font-size: 1em; }
        .tab-btn:hover { background: rgba(102, 126, 234, 0.1); color: #667eea; }
        .tab-btn.active { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; box-shadow: 0 -4px 15px rgba(102, 126, 234, 0.3); }
        .tab-content { display: none; }
        .tab-content.active { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        
        /* TOOL CARDS */
        .tool-card { background: #f9fafb; padding: 25px; border-radius: 12px; border: 2px solid #e5e7eb; }
        .tool-card h3 { color: #667eea; margin-bottom: 15px; font-size: 1.2em; display: flex; align-items: center; gap: 10px; }
        .tool-card input, .tool-card select, .tool-card textarea { width: 100%; padding: 12px; margin-top: 10px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 1em; }
        .tool-card button { width: 100%; padding: 14px; margin-top: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.3s; font-size: 1em; }
        .tool-card button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4); }
        
        /* CONFIG SECTION */
        .config-section { background: white; border-radius: 15px; padding: 30px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .device-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .device-card { background: #f9fafb; padding: 20px; border-radius: 12px; border: 2px solid #e5e7eb; }
        .device-card.active { border-color: #10b981; background: #d4edda; }
        .device-card h4 { color: #667eea; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }
        .device-card input { width: 100%; padding: 10px; margin-top: 8px; border: 2px solid #e5e7eb; border-radius: 6px; }
        .device-card button { padding: 10px 20px; margin-top: 10px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; }
        
        /* LOG */
        .log-panel { background: #1a1a2e; color: white; border-radius: 15px; padding: 25px; max-height: 400px; overflow-y: auto; font-family: 'Courier New', monospace; box-shadow: 0 10px 30px rgba(0,0,0,0.12); }
        .log-entry { padding: 8px; margin: 5px 0; border-left: 3px solid #667eea; background: rgba(102, 126, 234, 0.1); border-radius: 4px; }
        .log-time { color: #9ca3af; margin-right: 10px; }
        
        /* MUSIC PLAYER */
        .music-player { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; padding: 30px; color: white; margin-bottom: 30px; box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4); }
        .player-controls { display: flex; justify-content: center; align-items: center; gap: 20px; margin: 30px 0; }
        .player-btn { width: 60px; height: 60px; border-radius: 50%; background: rgba(255,255,255,0.2); border: 3px solid rgba(255,255,255,0.4); color: white; font-size: 24px; cursor: pointer; transition: all 0.3s; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px); }
        .player-btn:hover { background: rgba(255,255,255,0.3); transform: scale(1.1); box-shadow: 0 8px 25px rgba(0,0,0,0.3); }
        .player-btn.play { width: 80px; height: 80px; font-size: 32px; background: white; color: #667eea; }
        .now-playing { text-align: center; margin: 20px 0; }
        .now-playing h3 { font-size: 1.5em; margin-bottom: 10px; text-shadow: 0 2px 10px rgba(0,0,0,0.3); }
        .now-playing p { opacity: 0.9; font-size: 1.1em; }
        .progress-container { margin: 25px 0; }
        .progress-bar { width: 100%; height: 8px; background: rgba(255,255,255,0.3); border-radius: 10px; overflow: hidden; cursor: pointer; }
        .progress-fill { height: 100%; background: white; width: 0%; transition: width 0.3s; box-shadow: 0 0 10px rgba(255,255,255,0.5); }
        .progress-time { display: flex; justify-content: space-between; margin-top: 8px; font-size: 0.9em; opacity: 0.9; }
        /* Progress slider (draggable timeline) */
        #progress-slider { -webkit-appearance: none; width: 100%; height: 8px; border-radius: 4px; cursor: pointer; }
        #progress-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 16px; height: 16px; background: #667eea; border-radius: 50%; cursor: pointer; box-shadow: 0 2px 6px rgba(102,126,234,0.5); transition: transform 0.2s; }
        #progress-slider::-webkit-slider-thumb:hover { transform: scale(1.2); }
        #progress-slider::-moz-range-thumb { width: 16px; height: 16px; background: #667eea; border-radius: 50%; cursor: pointer; border: none; }
        .music-list { background: white; border-radius: 15px; padding: 25px; color: #333; max-height: 500px; overflow-y: auto; }
        .music-list h3 { color: #667eea; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
        .music-item { display: flex; align-items: center; padding: 15px; margin: 10px 0; background: #f9fafb; border-radius: 10px; cursor: pointer; transition: all 0.3s; border: 2px solid transparent; }
        .music-item:hover { background: #e8eaf6; border-color: #667eea; transform: translateX(5px); }
        .music-item.playing { background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); border-color: #667eea; }
        .music-item .icon { font-size: 24px; margin-right: 15px; }
        .music-item .info { flex: 1; }
        .music-item .name { font-weight: 600; color: #333; font-size: 1.05em; }
        .music-item .details { color: #666; font-size: 0.9em; margin-top: 5px; }
        .log-success { color: #10b981; border-left-color: #10b981; }
        .log-error { color: #ef4444; border-left-color: #ef4444; }
        .log-info { color: #3b82f6; border-left-color: #3b82f6; }
        
        /* SETTINGS ICON */
        .settings-icon { font-size: 1.8em; cursor: pointer; transition: all 0.3s; padding: 10px; border-radius: 50%; background: #f0f0f0; display: flex; align-items: center; justify-content: center; width: 50px; height: 50px; }
        .settings-icon:hover { transform: rotate(90deg); background: #667eea; color: white; }
        
        /* MODAL POPUP */
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); animation: fadeIn 0.3s; }
        .modal-content { background: white; margin: 5% auto; padding: 0; border-radius: 15px; width: 90%; max-width: 500px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); animation: slideDown 0.3s; }
        .modal-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px 30px; border-radius: 15px 15px 0 0; display: flex; justify-content: space-between; align-items: center; }
        .modal-header h2 { margin: 0; font-size: 1.5em; }
        .close-btn { font-size: 2em; cursor: pointer; color: white; background: none; border: none; line-height: 1; transition: transform 0.2s; }
        .close-btn:hover { transform: scale(1.2); }
        .modal-body { padding: 30px; }
        .modal-body label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
        .modal-body input { width: 100%; padding: 12px; margin-bottom: 20px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 1em; transition: border-color 0.3s; }
        .modal-body input:focus { outline: none; border-color: #667eea; }
        .modal-footer { padding: 20px 30px; background: #f9fafb; border-radius: 0 0 15px 15px; display: flex; gap: 15px; justify-content: flex-end; }
        .modal-btn { padding: 12px 30px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.3s; font-size: 1em; }
        .modal-btn.primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .modal-btn.primary:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4); }
        .modal-btn.secondary { background: #e5e7eb; color: #666; }
        .modal-btn.secondary:hover { background: #d1d5db; }
        .modal-btn.info { background: linear-gradient(135deg, #17a2b8 0%, #138496 100%); color: white; }
        .modal-btn.info:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(23, 162, 184, 0.4); }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideDown { from { transform: translateY(-50px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        
        /* AUDIO VISUALIZER - Sóng nhạc đẹp */
        .audio-visualizer {
            display: flex;
            align-items: flex-end;
            justify-content: center;
            gap: 3px;
            height: 40px;
            margin: 10px 0;
        }
        .audio-visualizer .bar {
            width: 4px;
            background: linear-gradient(to top, #667eea, #764ba2, #f472b6);
            border-radius: 2px;
            animation: visualizer-bar 0.5s ease-in-out infinite;
        }
        .audio-visualizer .bar:nth-child(1) { animation-delay: 0s; height: 20px; }
        .audio-visualizer .bar:nth-child(2) { animation-delay: 0.1s; height: 30px; }
        .audio-visualizer .bar:nth-child(3) { animation-delay: 0.15s; height: 25px; }
        .audio-visualizer .bar:nth-child(4) { animation-delay: 0.3s; height: 35px; }
        .audio-visualizer .bar:nth-child(5) { animation-delay: 0.2s; height: 28px; }
        .audio-visualizer .bar:nth-child(6) { animation-delay: 0.25s; height: 32px; }
        .audio-visualizer .bar:nth-child(7) { animation-delay: 0.05s; height: 22px; }
        .audio-visualizer .bar:nth-child(8) { animation-delay: 0.35s; height: 38px; }
        .audio-visualizer .bar:nth-child(9) { animation-delay: 0.1s; height: 26px; }
        .audio-visualizer .bar:nth-child(10) { animation-delay: 0.4s; height: 30px; }
        .audio-visualizer.paused .bar { animation-play-state: paused; }
        @keyframes visualizer-bar {
            0%, 100% { transform: scaleY(0.3); opacity: 0.6; }
            50% { transform: scaleY(1); opacity: 1; }
        }
        
        /* RUNCAT ANIMATION - JavaScript-based multi-frame like RunCat365 */
        #runcat-container {
            position: fixed;
            bottom: 15px;
            right: 15px;
            z-index: 9999;
            user-select: none;
            cursor: pointer;
        }
        
        #runcat {
            font-size: 52px;
            display: inline-block;
            filter: drop-shadow(0 3px 6px rgba(0,0,0,0.25));
            transition: transform 0.05s ease-out;
            will-change: transform;
        }
        
        #runcat:hover {
            animation: runcat-excited 0.15s ease-in-out infinite !important;
            filter: drop-shadow(0 6px 12px rgba(0,0,0,0.4));
        }
        
        @keyframes runcat-excited {
            0%, 100% { 
                transform: translateY(-2px) rotate(-8deg) scale(1.2) !important;
            }
            25% { 
                transform: translateY(-12px) rotate(8deg) scale(1.3) !important;
            }
            50% { 
                transform: translateY(-18px) rotate(-8deg) scale(1.25) !important;
            }
            75% { 
                transform: translateY(-12px) rotate(8deg) scale(1.3) !important;
            }
        }
        
        /* FOOTER MINIZ - Compact corner style */
        .footer-miniz { position: fixed; bottom: 20px; right: 20px; background: rgba(26, 26, 46, 0.95); color: white; padding: 12px 18px; border-radius: 50px; box-shadow: 0 5px 25px rgba(0,0,0,0.3); display: flex; align-items: center; gap: 12px; z-index: 1000; transition: all 0.3s; backdrop-filter: blur(10px); }
        .footer-miniz:hover { transform: translateY(-3px); box-shadow: 0 8px 35px rgba(102, 126, 234, 0.5); }
        .footer-logo-compact { display: flex; align-items: center; gap: 10px; }
        .footer-logo-compact img { width: 35px; height: 35px; border-radius: 50%; border: 2px solid #667eea; box-shadow: 0 0 10px rgba(102, 126, 234, 0.6); }
        .footer-brand-compact { font-size: 0.95em; font-weight: bold; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .footer-separator { width: 1px; height: 25px; background: rgba(255,255,255,0.3); }
        .footer-youtube-compact { display: flex; align-items: center; gap: 6px; padding: 8px 15px; background: #FF0000; color: white; border-radius: 25px; text-decoration: none; font-weight: 600; font-size: 0.85em; transition: all 0.3s; }
        .footer-youtube-compact:hover { background: #cc0000; transform: scale(1.05); }
        .footer-youtube-compact svg { width: 18px; height: 18px; fill: white; }
        
        /* RESPONSIVE - MOBILE FIRST */
        @media (max-width: 1200px) {
            .quick-actions { grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 15px; }
            .tab-content.active { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
            .device-grid { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
        }
        
        @media (max-width: 992px) {
            .sidebar { width: 240px; padding: 20px 15px; }
            .main-content { padding: 20px; }
            .header { padding: 20px; flex-direction: column; gap: 15px; text-align: center; }
            .header h1 { font-size: 1.6em; }
            .music-player { padding: 20px; }
            .player-controls { gap: 15px; }
            .player-btn { width: 50px; height: 50px; font-size: 20px; }
            .player-btn.play { width: 65px; height: 65px; font-size: 26px; }
        }
        
        @media (max-width: 768px) {
            body { flex-direction: column; }
            .sidebar { width: 100%; padding: 15px; flex-direction: row; flex-wrap: wrap; justify-content: center; gap: 10px; }
            .logo { width: 100%; margin-bottom: 15px; padding: 15px; }
            .logo-icon { width: 60px; }
            .logo-text { font-size: 1.2em; }
            .menu-item { padding: 10px 15px; margin: 3px; font-size: 0.9em; }
            .main-content { padding: 15px; min-height: calc(100vh - 200px); }
            .header { padding: 15px; margin-bottom: 20px; }
            .header h1 { font-size: 1.3em; }
            .status { flex-wrap: wrap; justify-content: center; gap: 10px; }
            .status-badge { padding: 6px 15px; font-size: 0.9em; }
            .quick-actions { grid-template-columns: repeat(2, 1fr); gap: 10px; }
            .action-card { padding: 15px; }
            .action-card .icon { font-size: 1.8em; }
            .action-card .title { font-size: 0.9em; }
            .tools-section, .config-section { padding: 20px; }
            .tools-tabs { flex-wrap: wrap; gap: 8px; }
            .tab-btn { padding: 10px 20px; font-size: 0.9em; }
            .tab-content.active { grid-template-columns: 1fr; }
            .tool-card { padding: 20px; }
            .device-grid { grid-template-columns: 1fr; }
            .music-player { padding: 15px; border-radius: 15px; }
            .now-playing h3 { font-size: 1.2em; }
            .player-controls { gap: 10px; margin: 20px 0; }
            .player-btn { width: 45px; height: 45px; font-size: 18px; }
            .player-btn.play { width: 60px; height: 60px; font-size: 24px; }
            .music-list { padding: 15px; max-height: 350px; }
            .music-item { padding: 12px; }
            .chat-bubble { max-width: 85%; }
            .modal-content { width: 95%; margin: 2% auto; }
            .modal-body { padding: 20px; }
            .modal-footer { padding: 15px 20px; flex-direction: column; }
            .modal-btn { width: 100%; }
            .footer-miniz { bottom: 10px; right: 10px; padding: 10px 14px; }
            .footer-brand-compact { font-size: 0.85em; }
            .footer-youtube-compact { padding: 6px 12px; font-size: 0.8em; }
            #runcat-container { bottom: 10px; right: 10px; }
            #runcat { font-size: 40px; }
        }
        
        @media (max-width: 480px) {
            .sidebar { padding: 10px; }
            .logo { padding: 10px; }
            .logo-icon { width: 45px; }
            .logo-text { font-size: 1em; }
            .menu-item { padding: 8px 12px; font-size: 0.85em; }
            .main-content { padding: 10px; }
            .header { padding: 12px; }
            .header h1 { font-size: 1.1em; }
            .quick-actions { grid-template-columns: repeat(2, 1fr); gap: 8px; }
            .action-card { padding: 12px; }
            .action-card .icon { font-size: 1.5em; margin-bottom: 5px; }
            .action-card .title { font-size: 0.8em; }
            .tools-section, .config-section { padding: 15px; margin-bottom: 20px; }
            .tab-btn { padding: 8px 15px; font-size: 0.85em; }
            .tool-card { padding: 15px; }
            .tool-card h3 { font-size: 1em; }
            .tool-card input, .tool-card select, .tool-card textarea { padding: 10px; font-size: 0.9em; }
            .tool-card button { padding: 12px; font-size: 0.9em; }
            .log-panel { max-height: 250px; padding: 15px; font-size: 0.85em; }
            .music-player { padding: 12px; }
            .now-playing h3 { font-size: 1em; }
            .now-playing p { font-size: 0.9em; }
            .player-btn { width: 40px; height: 40px; font-size: 16px; }
            .player-btn.play { width: 55px; height: 55px; font-size: 22px; }
            .chat-avatar { width: 32px; height: 32px; font-size: 0.9em; }
            .chat-bubble { padding: 10px 12px; }
            .chat-content { font-size: 0.9em; }
            .footer-miniz { flex-direction: column; padding: 8px 12px; gap: 8px; }
            .footer-separator { display: none; }
        }
        
        /* WECHAT STYLE CHAT BUBBLES */
        .chat-message { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 15px; animation: fadeInChat 0.3s; }
        .chat-message.user { flex-direction: row-reverse; }
        .chat-avatar { width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 1.1em; flex-shrink: 0; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
        .chat-avatar.assistant { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
        .chat-avatar.system { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
        .chat-avatar.tool { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); }
        .chat-bubble { max-width: 65%; padding: 12px 16px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); position: relative; word-wrap: break-word; }
        .chat-message.user .chat-bubble { background: #667eea; color: white; border-radius: 12px 12px 2px 12px; }
        .chat-message.assistant .chat-bubble { background: white; color: #333; border-radius: 12px 12px 12px 2px; border: 1px solid #e5e7eb; }
        .chat-message.system .chat-bubble { background: #fff7ed; color: #7c2d12; border-radius: 8px; border: 1px solid #fed7aa; }
        .chat-message.tool .chat-bubble { background: #eff6ff; color: #1e3a8a; border-radius: 8px; border: 1px solid #bfdbfe; }
        .chat-content { font-size: 0.95em; line-height: 1.5; margin-bottom: 6px; }
        .chat-metadata { font-size: 0.75em; opacity: 0.7; display: flex; gap: 10px; flex-wrap: wrap; margin-top: 8px; }
        .chat-metadata-item { display: inline-flex; align-items: center; gap: 4px; background: rgba(0,0,0,0.05); padding: 2px 8px; border-radius: 10px; }
        .chat-timestamp { font-size: 0.7em; opacity: 0.6; margin-top: 4px; text-align: right; }
        .chat-message.user .chat-timestamp { text-align: left; }
        @keyframes fadeInChat { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        #chat-container::-webkit-scrollbar { width: 8px; }
        #chat-container::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
        #chat-container::-webkit-scrollbar-thumb { background: #667eea; border-radius: 10px; }
        #chat-container::-webkit-scrollbar-thumb:hover { background: #5568d3; }
        
        /* Music Player VLC-style enhancements */
        .music-item:hover { background: linear-gradient(135deg, rgba(102,126,234,0.15) 0%, rgba(118,75,162,0.15) 100%) !important; transform: translateX(5px); }
        #volume-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 16px; height: 16px; background: #667eea; border-radius: 50%; cursor: pointer; box-shadow: 0 2px 6px rgba(102, 126, 234, 0.5); }
        #volume-slider::-moz-range-thumb { width: 16px; height: 16px; background: #667eea; border-radius: 50%; cursor: pointer; border: none; }
    </style>
</head>
<body>
    <!-- SIDEBAR -->
    <div class="sidebar">
        <div class="logo">
            <svg class="logo-icon" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#667eea"/>
                        <stop offset="100%" style="stop-color:#764ba2"/>
                    </linearGradient>
                </defs>
                <circle cx="50" cy="50" r="45" fill="url(#logoGrad)"/>
                <text x="50" y="58" text-anchor="middle" fill="white" font-size="28" font-weight="bold" font-family="Arial">MCP</text>
                <text x="50" y="75" text-anchor="middle" fill="#a5f3fc" font-size="12" font-weight="600" font-family="Arial">miniZ</text>
            </svg>
            <div class="logo-text">miniZ MCP</div>
            <small style="font-size:0.55em;opacity:0.9;font-weight:600;letter-spacing:1px;">ĐIỀU KHIỂN MÁY TÍNH</small>
        </div>
        <div class="menu-item active" onclick="showSection('dashboard')">📊Sidebar</div>
        <div class="menu-item" onclick="showSection('tools')">🛠️ Công Cụ</div>
        <div class="menu-item" onclick="showSection('music')">🎵 Music Player</div>
        <div class="menu-item" onclick="showSection('music-settings')">⚙️ Music Settings</div>
        <div class="menu-item" onclick="showSection('conversation')">💬 Lịch Sử Chat</div>
        <div class="menu-item" onclick="showSection('playlist')">🎵 Playlist YouTube</div>
        <div class="menu-item" onclick="showSection('knowledge')">📚 Knowledge Base</div>
    </div>
    
    <!-- MAIN CONTENT -->
    <div class="main-content">
        <!-- HEADER -->
        <div class="header">
            <h1>Dashboard</h1>
            <div class="status">
                <div class="settings-icon" onclick="openSettingsModal()" title="Cấu hình Endpoint">⚙️</div>
                <div class="status-badge" id="xiaozhi-status">
                    <span class="status-dot"></span>
                    <span id="xiaozhi-text">Connecting...</span>
                </div>
                <div class="status-badge online">
                    <span class="status-dot"></span>
                    Web Server
                </div>
            </div>
        </div>
        
        <!-- DASHBOARD SECTION -->
        <div id="dashboard-section">
            <h2 style="color:#667eea;margin-bottom:20px;">🚀 Tất cả công cụ (38 Tools)</h2>
            <div class="quick-actions">
                <!-- AI ASSISTANT (2) - NEW -->
                <div class="action-card purple" onclick="askGemini()"><div class="icon">🤖</div><div class="title">Hỏi Gemini AI</div></div>
                <div class="action-card indigo" onclick="askGPT4()"><div class="icon">🧠</div><div class="title">Hỏi GPT-4</div></div>
                
                <!-- HỆ THỐNG (5) -->
                <div class="action-card blue" onclick="setVolumePrompt()"><div class="icon">🔊</div><div class="title">Điều Chỉnh Âm Lượng</div></div>
                <div class="action-card cyan" onclick="screenshot()"><div class="icon">📸</div><div class="title">Chụp Màn Hình</div></div>
                <div class="action-card purple" onclick="notification()"><div class="icon">🔔</div><div class="title">Thông Báo</div></div>
                <div class="action-card green" onclick="getResources()"><div class="icon">💻</div><div class="title">Tài Nguyên Hệ Thống</div></div>
                <div class="action-card orange" onclick="setBrightness()"><div class="icon">🔆</div><div class="title">Độ Sáng Màn Hình</div></div>
                
                <!-- FILE & PROCESS (7) -->
                <div class="action-card indigo" onclick="openApp()"><div class="icon">🚀</div><div class="title">Mở Ứng Dụng</div></div>
                <div class="action-card blue" onclick="listProcesses()"><div class="icon">⚙️</div><div class="title">Tiến Trình Đang Chạy</div></div>
                <div class="action-card red" onclick="killProcess()"><div class="icon">❌</div><div class="title">Tắt Tiến Trình</div></div>
                <div class="action-card green" onclick="createFile()"><div class="icon">➕</div><div class="title">Tạo File Mới</div></div>
                <div class="action-card cyan" onclick="readFile()"><div class="icon">📖</div><div class="title">Đọc File</div></div>
                <div class="action-card purple" onclick="listFiles()"><div class="icon">📂</div><div class="title">Liệt Kê Files</div></div>
                <div class="action-card orange" onclick="diskUsage()"><div class="icon">💽</div><div class="title">Thông Tin Đĩa</div></div>
                
                <!-- MẠNG & WEB (3) -->
                <div class="action-card blue" onclick="networkInfo()"><div class="icon">🌐</div><div class="title">Thông Tin Mạng</div></div>
                <div class="action-card green" onclick="batteryStatus()"><div class="icon">🔋</div><div class="title">Thông Tin Pin</div></div>
                <div class="action-card indigo" onclick="searchWeb()"><div class="icon">🔍</div><div class="title">Tìm Kiếm Google</div></div>
                
                <!-- TIỆN ÍCH (5) -->
                <div class="action-card pink" onclick="calculator()"><div class="icon">🧮</div><div class="title">Máy Tính</div></div>
                <div class="action-card cyan" onclick="getCurrentTime()"><div class="icon">⏰</div><div class="title">Thời Gian</div></div>
                <div class="action-card purple" onclick="getClipboard()"><div class="icon">📋</div><div class="title">Lấy Clipboard</div></div>
                <div class="action-card orange" onclick="setClipboard()"><div class="icon">📝</div><div class="title">Đặt Clipboard</div></div>
                <div class="action-card red" onclick="playSound()"><div class="icon">🔊</div><div class="title">Phát Âm Thanh</div></div>
                
                <!-- NEW TOOLS -->
                <div class="action-card blue" onclick="lockComputer()"><div class="icon">🔒</div><div class="title">Khóa Máy Tính</div></div>
                <div class="action-card red" onclick="shutdownSchedule()"><div class="icon">⏰</div><div class="title">Lên Lịch Tắt Máy</div></div>
                <div class="action-card green" onclick="showDesktop()"><div class="icon">🖥️</div><div class="title">Hiển Thị Desktop</div></div>
                <div class="action-card orange" onclick="undoOperation()"><div class="icon">↩️</div><div class="title">Hoàn Tác</div></div>
                <div class="action-card purple" onclick="setTheme()"><div class="icon">🎨</div><div class="title">Đổi Theme</div></div>
                <div class="action-card cyan" onclick="changeWallpaper()"><div class="icon">🖼️</div><div class="title">Đổi Hình Nền</div></div>
                <div class="action-card indigo" onclick="getDesktopPath()"><div class="icon">📁</div><div class="title">Đường Dẫn Desktop</div></div>
                <div class="action-card pink" onclick="pasteContent()"><div class="icon">📋</div><div class="title">Dán Nội Dung</div></div>
                <div class="action-card blue" onclick="pressEnter()"><div class="icon">⏎</div><div class="title">Nhấn Enter</div></div>
                <div class="action-card green" onclick="findInDocument()"><div class="icon">🔎</div><div class="title">Tìm Trong Tài Liệu</div></div>
            </div>
            
            <!-- LOG PANEL AT BOTTOM OF DASHBOARD -->
            <div style="margin-top: 30px;">
                <h2 style="color:#667eea; margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                    <span>📋 Log Hoạt Động</span>
                    <span style="font-size: 0.6em; color: #9ca3af; font-weight: 400;">(Thời gian thực)</span>
                </h2>
                <div class="log-panel" id="log"></div>
            </div>
        </div>

        <!-- TOOLS SECTION -->
        <div id="tools-section" style="display:none;">
            <div class="tools-section">
                <h2 style="color:#667eea;margin-bottom:20px;">🛠️ Công Cụ (20 Tools)</h2>
                
                <div class="tools-tabs">
                    <button class="tab-btn active" onclick="switchTab(0)">🎛️ Hệ thống</button>
                    <button class="tab-btn" onclick="switchTab(1)">📁 File & Process</button>
                    <button class="tab-btn" onclick="switchTab(2)">🌐 Mạng & Web</button>
                    <button class="tab-btn" onclick="switchTab(3)">🔧 Tiện ích</button>
                </div>
                
                <!-- TAB 1: HỆ THỐNG -->
                <div class="tab-content active" id="tab-0">
                    <div class="tool-card">
                        <h3>🔊 Điều chỉnh âm lượng</h3>
                        <input type="number" id="volume" min="0" max="100" value="50" placeholder="0-100">
                        <button onclick="
                            const level = parseInt(document.getElementById('volume').value);
                            if (isNaN(level) || level < 0 || level > 100) {
                                addLog('❌ Âm lượng phải từ 0-100', 'error');
                            } else {
                                callAPI('/api/volume', {level: level});
                            }
                        ">Đặt âm lượng</button>
                    </div>
                    <div class="tool-card">
                        <h3>📸 Chụp màn hình</h3>
                        <button onclick="callAPI('/api/screenshot', {})">Chụp màn hình ngay</button>
                    </div>
                    <div class="tool-card">
                        <h3>🔔 Thông báo</h3>
                        <input type="text" id="notif-title" placeholder="Tiêu đề">
                        <input type="text" id="notif-message" placeholder="Nội dung">
                        <button onclick="
                            const title = document.getElementById('notif-title').value.trim();
                            const message = document.getElementById('notif-message').value.trim();
                            if (!title || !message) {
                                addLog('❌ Vui lòng nhập tiêu đề và nội dung', 'error');
                            } else {
                                callAPI('/api/notification', {title: title, message: message});
                            }
                        ">Hiển thị</button>
                    </div>
                    <div class="tool-card">
                        <h3>💻 Tài nguyên hệ thống</h3>
                        <button onclick="getResources()">Làm mới</button>
                        <div id="resources" style="margin-top:15px;">
                            <div>CPU: <span id="cpu">--%</span></div>
                            <div>RAM: <span id="ram">--%</span></div>
                            <div>Disk: <span id="disk">--%</span></div>
                        </div>
                    </div>
                    <div class="tool-card">
                        <h3>🔆 Độ sáng màn hình</h3>
                        <input type="number" id="brightness" min="0" max="100" value="50" placeholder="0-100">
                        <button onclick="
                            const level = parseInt(document.getElementById('brightness').value);
                            if (isNaN(level) || level < 0 || level > 100) {
                                addLog('❌ Độ sáng phải từ 0-100', 'error');
                            } else {
                                callTool('set_brightness', {level: level});
                            }
                        ">Đặt độ sáng</button>
                    </div>
                </div>
                
                <!-- TAB 2: FILE & PROCESS -->
                <div class="tab-content" id="tab-1">
                    <div class="tool-card">
                        <h3>🚀 Mở ứng dụng</h3>
                        <select id="app-name">
                            <option value="notepad">📝 Notepad</option>
                            <option value="calc">🧮 Calculator</option>
                            <option value="paint">🎨 Paint</option>
                            <option value="cmd">⌨️ CMD</option>
                            <option value="explorer">📂 Explorer</option>
                        </select>
                        <button onclick="callTool('open_application', {app_name: document.getElementById('app-name').value})">Mở</button>
                    </div>
                    <div class="tool-card">
                        <h3>📋 Tiến trình đang chạy</h3>
                        <input type="number" id="proc-limit" min="5" max="50" value="10" placeholder="Số lượng">
                        <button onclick="callTool('list_running_processes', {limit: parseInt(document.getElementById('proc-limit').value)})">Xem danh sách</button>
                    </div>
                    <div class="tool-card">
                        <h3>❌ Tắt tiến trình</h3>
                        <input type="text" id="kill-proc" placeholder="PID hoặc tên">
                        <button onclick="callTool('kill_process', {identifier: document.getElementById('kill-proc').value})">Tắt tiến trình</button>
                    </div>
                    <div class="tool-card">
                        <h3>📝 Tạo file mới</h3>
                        <input type="text" id="file-path" placeholder="C:/test.txt">
                        <textarea id="file-content" placeholder="Nội dung..." style="min-height:80px;"></textarea>
                        <button onclick="callTool('create_file', {path: document.getElementById('file-path').value, content: document.getElementById('file-content').value})">Tạo file</button>
                    </div>
                    <div class="tool-card">
                        <h3>📖 Đọc file</h3>
                        <input type="text" id="read-path" placeholder="C:/test.txt">
                        <button onclick="callTool('read_file', {path: document.getElementById('read-path').value})">Đọc file</button>
                    </div>
                    <div class="tool-card">
                        <h3>📂 Liệt kê files</h3>
                        <input type="text" id="list-dir" placeholder="C:/Users">
                        <button onclick="callTool('list_files', {directory: document.getElementById('list-dir').value})">Xem files</button>
                    </div>
                    <div class="tool-card">
                        <h3>💾 Thông tin đĩa</h3>
                        <button onclick="callTool('get_disk_usage', {})">Xem chi tiết</button>
                    </div>
                </div>
                
                <!-- TAB 3: MẠNG & WEB -->
                <div class="tab-content" id="tab-2">
                    <div class="tool-card">
                        <h3>🌐 Thông tin mạng</h3>
                        <button onclick="callTool('get_network_info', {})">Xem IP & hostname</button>
                    </div>
                    <div class="tool-card">
                        <h3>🔋 Thông tin pin</h3>
                        <button onclick="callTool('get_battery_status', {})">Kiểm tra pin</button>
                    </div>
                    <div class="tool-card">
                        <h3>🔍 Tìm kiếm Google</h3>
                        <input type="text" id="search-query" placeholder="Nhập từ khóa...">
                        <button onclick="callTool('search_web', {query: document.getElementById('search-query').value})">Tìm kiếm</button>
                    </div>
                </div>
                
                <!-- TAB 4: TIỆN ÍCH -->
                <div class="tab-content" id="tab-3">
                    <div class="tool-card">
                        <h3>🧮 Máy tính</h3>
                        <input type="text" id="calc-expr" placeholder="2+2*3">
                        <button onclick="calculate()">Tính toán</button>
                        <div id="calc-result" style="margin-top:10px;font-size:1.5em;font-weight:bold;color:#667eea;"></div>
                    </div>
                    <div class="tool-card">
                        <h3>🕐 Thời gian</h3>
                        <button onclick="getCurrentTime()">Lấy thời gian</button>
                        <div id="time-result" style="margin-top:10px;font-size:1.2em;color:#667eea;"></div>
                    </div>
                    <div class="tool-card">
                        <h3>📋 Lấy clipboard</h3>
                        <button onclick="callTool('get_clipboard', {})">Xem nội dung</button>
                    </div>
                    <div class="tool-card">
                        <h3>📝 Đặt clipboard</h3>
                        <input type="text" id="clip-text" placeholder="Nội dung cần copy">
                        <button onclick="callTool('set_clipboard', {text: document.getElementById('clip-text').value})">Copy vào clipboard</button>
                    </div>
                    <div class="tool-card">
                        <h3>🔊 Phát âm thanh</h3>
                        <input type="number" id="sound-freq" min="200" max="2000" value="1000" placeholder="Tần số Hz">
                        <input type="number" id="sound-dur" min="100" max="3000" value="500" placeholder="Thời gian ms">
                        <button onclick="callTool('play_sound', {frequency: parseInt(document.getElementById('sound-freq').value), duration: parseInt(document.getElementById('sound-dur').value)})">Phát beep</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- CONFIG SECTION - HIDDEN (Replaced by Modal) -->
        <div id="config-section" style="display:none;">
            <div class="config-section">
                <h2 style="color:#667eea;margin-bottom:20px;">⚙️ Cấu hình hiện tại</h2>
                <p style="color:#666;margin-bottom:20px;">Sử dụng icon ⚙️ ở góc phải trên để thay đổi endpoint</p>
                <div id="current-endpoint-info" style="background:#f9fafb;padding:20px;border-radius:12px;border:2px solid #e5e7eb;">
                    <p><strong>Thiết bị đang hoạt động:</strong> <span id="current-device-name">-</span></p>
                    <p><strong>Token:</strong> <span id="current-device-token" style="font-family:monospace;font-size:0.9em;word-break:break-all;">-</span></p>
                </div>
            </div>
        </div>
        
        
        <!-- CONVERSATION HISTORY SECTION (WeChat style) -->
        <div id="conversation-section" style="display:none;">
            <div style="background: white; border-radius: 15px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.12); height: calc(100vh - 180px); display: flex; flex-direction: column;">
                <h2 style="color:#667eea; margin-bottom: 15px; display: flex; align-items: center; justify-content: space-between;">
                    <span>💬 Lịch Sử Hội Thoại</span>
                    <div style="display:flex; gap:10px;">
                        <button onclick="loadConversationHistory()" style="padding:8px 16px; background:#10b981; color:white; border:none; border-radius:8px; cursor:pointer; font-size:0.9em;">
                            🔄 Làm mới
                        </button>
                        <button onclick="exportConversation()" style="padding:8px 16px; background:#667eea; color:white; border:none; border-radius:8px; cursor:pointer; font-size:0.9em;">
                            💾 Xuất File
                        </button>
                        <button onclick="clearConversationHistory()" style="padding:8px 16px; background:#ef4444; color:white; border:none; border-radius:8px; cursor:pointer; font-size:0.9em;">
                            🗑️ Xóa Hết
                        </button>
                    </div>
                </h2>
                
                <!-- Stats bar -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:white; padding:12px 16px; border-radius:10px; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-size:0.85em; opacity:0.9;">Tổng số tin nhắn:</span>
                        <span style="font-weight:700; font-size:1.1em; margin-left:8px;" id="total-messages">0</span>
                    </div>
                    <div style="font-size:0.85em; opacity:0.9;" id="last-update">Chưa có dữ liệu</div>
                </div>
                
                <!-- Chat container (WeChat style) -->
                <div id="chat-container" style="flex:1; overflow-y:auto; background:#f5f5f5; border-radius:10px; padding:15px; display:flex; flex-direction:column; gap:12px;">
                    <!-- Messages will be rendered here -->
                </div>
            </div>
        </div>
        
        <!-- MUSIC PLAYER SECTION - VLC Web Interface Style -->
        <div id="music-section" style="display:none;">
            <!-- Source Priority Selector -->
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span style="color: #fff; font-weight: 600; font-size: 1.1em;">🎯 Nguồn phát ưu tiên:</span>
                        <div style="display: flex; gap: 10px;">
                            <button id="source-library-btn" onclick="setMusicSource('library')" 
                                    style="padding: 10px 20px; border-radius: 25px; border: 2px solid #667eea; background: #667eea; color: white; font-weight: 600; cursor: pointer; transition: all 0.3s;">
                                📚 Music Library
                            </button>
                            <button id="source-user-btn" onclick="setMusicSource('user')" 
                                    style="padding: 10px 20px; border-radius: 25px; border: 2px solid #667eea; background: transparent; color: #667eea; font-weight: 600; cursor: pointer; transition: all 0.3s;">
                                📁 Thư mục cá nhân
                            </button>
                        </div>
                    </div>
                    <div id="current-source-info" style="color: #a5b4fc; font-size: 0.9em;">
                        Đang dùng: <span id="source-path-display" style="font-family: monospace;">music_library/</span>
                    </div>
                </div>
            </div>
            
            <!-- VLC-style Player -->
            <div class="music-player" style="position:relative; background: linear-gradient(135deg, #2b3e50 0%, #1a252f 100%); border-radius: 15px; padding: 25px; box-shadow: 0 15px 40px rgba(0,0,0,0.4);">
                <!-- Album Art & Track Info -->
                <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
                    <div id="album-art" style="width: 120px; height: 120px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 48px; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);">
                        🎵
                    </div>
                    <div class="now-playing" style="flex: 1;">
                        <h3 id="current-track" style="color: #fff; font-size: 1.4em; margin-bottom: 8px;">🎵 Chưa phát nhạc</h3>
                        <p id="track-info" style="color: #a5b4fc; font-size: 0.95em; margin-bottom: 5px;">Chọn bài hát từ danh sách bên dưới</p>
                        <!-- Audio Visualizer - Sóng nhạc -->
                        <div id="audio-visualizer" class="audio-visualizer paused" style="display: none;">
                            <div class="bar"></div>
                            <div class="bar"></div>
                            <div class="bar"></div>
                            <div class="bar"></div>
                            <div class="bar"></div>
                            <div class="bar"></div>
                            <div class="bar"></div>
                            <div class="bar"></div>
                            <div class="bar"></div>
                            <div class="bar"></div>
                        </div>
                        <p id="track-album" style="color: #6b7280; font-size: 0.85em;"></p>
                    </div>
                </div>
                
                <!-- Progress Bar (VLC style) - DRAGGABLE -->
                <div class="progress-container" style="margin-bottom: 20px;">
                    <input type="range" id="progress-slider" min="0" max="100" value="0" step="0.1"
                           oninput="onProgressDrag(this.value)" 
                           onchange="onProgressSeek(this.value)"
                           onmousedown="isDraggingProgress = true"
                           onmouseup="isDraggingProgress = false"
                           style="width: 100%; height: 8px; -webkit-appearance: none; background: linear-gradient(to right, #667eea 0%, #667eea 0%, #374151 0%, #374151 100%); border-radius: 4px; cursor: pointer; margin: 0;">
                    <div class="progress-time" style="display: flex; justify-content: space-between; margin-top: 8px; color: #9ca3af; font-size: 0.85em; font-family: monospace;">
                        <span id="current-time">0:00</span>
                        <span id="total-time">0:00</span>
                    </div>
                </div>
                
                <!-- Player Controls (VLC style) -->
                <div class="player-controls" style="display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 20px;">
                    <div class="player-btn" id="shuffle-btn" onclick="toggleShuffle()" title="Phát ngẫu nhiên" style="opacity: 0.6; cursor: pointer; font-size: 1.3em; padding: 10px; transition: all 0.2s;">🔀</div>
                    <div class="player-btn" onclick="musicPrevious()" title="Bài trước" style="cursor: pointer; font-size: 1.5em; padding: 10px;">⏮️</div>
                    <div class="player-btn play" onclick="musicPlayPause()" id="play-btn" title="Phát/Tạm dừng" style="cursor: pointer; font-size: 2.5em; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50%; box-shadow: 0 5px 20px rgba(102, 126, 234, 0.5);">▶️</div>
                    <div class="player-btn" onclick="musicNext()" title="Bài tiếp" style="cursor: pointer; font-size: 1.5em; padding: 10px;">⏭️</div>
                    <div class="player-btn" id="repeat-btn" onclick="toggleRepeat()" title="Lặp lại" style="opacity: 0.6; cursor: pointer; font-size: 1.3em; padding: 10px; transition: all 0.2s;">🔁</div>
                    <div class="player-btn" onclick="musicStop()" title="Dừng" style="cursor: pointer; font-size: 1.3em; padding: 10px;">⏹️</div>
                </div>
                
                <!-- Volume Control (VLC style) -->
                <div style="display: flex; align-items: center; justify-content: center; gap: 15px; padding: 10px 0;">
                    <span onclick="toggleMute()" style="cursor: pointer; font-size: 1.3em;" id="volume-icon">🔊</span>
                    <input type="range" id="volume-slider" min="0" max="100" value="80" 
                           oninput="setPlayerVolume(this.value)"
                           style="width: 200px; height: 6px; -webkit-appearance: none; background: linear-gradient(to right, #667eea 0%, #667eea 80%, #374151 80%, #374151 100%); border-radius: 3px; cursor: pointer;">
                    <span id="volume-value" style="color: #9ca3af; font-size: 0.85em; min-width: 40px;">80%</span>
                </div>
            </div>
            
            <!-- Music Library with Search -->
            <div class="music-list" style="margin-top: 20px; background: white; border-radius: 15px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.12);">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #333;">📁 Thư Viện Nhạc</h3>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <input type="text" id="music-search" placeholder="🔍 Tìm bài hát..." 
                               oninput="filterMusicLibrary(this.value)"
                               style="padding: 10px 15px; border: 2px solid #e5e7eb; border-radius: 25px; width: 250px; font-size: 0.95em;">
                        <button onclick="loadMusicLibrary()" style="padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 25px; cursor: pointer; font-weight: 600;">🔄 Làm mới</button>
                    </div>
                </div>
                <div id="music-library" style="max-height: 400px; overflow-y: auto;">
                    <div style="text-align:center; padding:40px; color:#999;">
                        <p style="font-size:1.2em; margin-bottom:10px;">⏳ Đang tải danh sách nhạc...</p>
                        <button onclick="loadMusicLibrary()" style="padding:12px 24px; background:#667eea; color:white; border:none; border-radius:8px; cursor:pointer; font-size:1em;">Tải ngay</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- RUNCAT ANIMATION (góc phải dưới) -->
        <div id="runcat-container">
            <div id="runcat">🐱</div>
        </div>

        <!-- MUSIC SETTINGS SECTION -->
        <div id="music-settings-section" style="display:none;">
            <div style="background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.12);">
                <h2 style="color:#667eea; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                    ⚙️ Cài Đặt Thư Mục Nhạc
                </h2>
                
                <div style="background: #f8f9fa; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #667eea;">
                    <h3 style="color: #333; margin-bottom: 15px; font-size: 1.1em;">📁 Đường Dẫn Thư Mục Nhạc</h3>
                    <p style="color: #666; margin-bottom: 15px; line-height: 1.6;">
                        Nhập đường dẫn đến thư mục chứa nhạc của bạn. miniZ sẽ ưu tiên phát nhạc từ thư mục này bằng trình phát mặc định của Windows.
                    </p>
                    
                    <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                        <input type="text" id="music-folder-path" placeholder="Ví dụ: F:\My Music hoặc C:\Users\Name\Music" 
                               style="flex: 1; padding: 12px 15px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 1em; font-family: 'Consolas', monospace;">
                        <button onclick="browseMusicFolder()" 
                                style="padding: 12px 20px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; white-space: nowrap;">
                            📂 Chọn Thư Mục
                        </button>
                        <button onclick="saveMusicFolder()" 
                                style="padding: 12px 20px; background: #10b981; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; white-space: nowrap;">
                            💾 Lưu
                        </button>
                    </div>
                    
                    <div id="music-folder-status" style="margin-top: 10px; padding: 10px; border-radius: 6px; display: none;"></div>
                </div>
                
                <div style="background: #fff3cd; padding: 20px; border-radius: 12px; border-left: 4px solid #ffc107; margin-bottom: 20px;">
                    <h3 style="color: #856404; margin-bottom: 10px; font-size: 1em;">💡 Lưu Ý</h3>
                    <ul style="color: #856404; line-height: 1.8; margin-left: 20px;">
                        <li>Sau khi lưu, bạn có thể yêu cầu LLM phát nhạc từ thư mục này</li>
                        <li>miniZ sẽ dùng trình phát mặc định của Windows (Windows Media Player, Groove Music, VLC...)</li>
                        <li>Ví dụ lệnh: "<i>Phát nhạc trong thư mục của tôi</i>" hoặc "<i>Play all songs</i>"</li>
                    </ul>
                </div>
                
                <div style="background: #e8f4f8; padding: 20px; border-radius: 12px; border-left: 4px solid #3b82f6;">
                    <h3 style="color: #1e40af; margin-bottom: 10px; font-size: 1em;">🎵 Định Dạng Hỗ Trợ</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
                        <span style="background: white; padding: 6px 12px; border-radius: 6px; font-size: 0.9em; color: #1e40af; font-weight: 600;">.mp3</span>
                        <span style="background: white; padding: 6px 12px; border-radius: 6px; font-size: 0.9em; color: #1e40af; font-weight: 600;">.wav</span>
                        <span style="background: white; padding: 6px 12px; border-radius: 6px; font-size: 0.9em; color: #1e40af; font-weight: 600;">.flac</span>
                        <span style="background: white; padding: 6px 12px; border-radius: 6px; font-size: 0.9em; color: #1e40af; font-weight: 600;">.m4a</span>
                        <span style="background: white; padding: 6px 12px; border-radius: 6px; font-size: 0.9em; color: #1e40af; font-weight: 600;">.wma</span>
                        <span style="background: white; padding: 6px 12px; border-radius: 6px; font-size: 0.9em; color: #1e40af; font-weight: 600;">.aac</span>
                        <span style="background: white; padding: 6px 12px; border-radius: 6px; font-size: 0.9em; color: #1e40af; font-weight: 600;">.ogg</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- PLAYLIST SECTION -->
        <div id="playlist-section" style="display:none;">
            <div style="background: white; border-radius: 15px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.12);">
                <h2 style="color:#667eea; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; gap: 15px;">
                    <span>🎵 Danh Sách Nhạc YouTube</span>
                    <div style="display:flex; align-items:center; gap:10px;">
                        <input id="playlist-command" placeholder="Gõ từ khóa playlist (vd: nhạc, chill...)" style="padding:8px 12px; border-radius:8px; border:1px solid #e5e7eb; font-size:0.95em; width:280px;" 
                               onkeypress="if(event.key==='Enter') triggerPlayByName(this.value.trim())" />
                        <button onclick="triggerPlayByName(document.getElementById('playlist-command').value.trim())" style="padding:8px 12px; background:#667eea; color:white; border:none; border-radius:8px; cursor:pointer;">Mở</button>
                    </div>
                </h2>

                <div style="display:flex; gap:20px; align-items:flex-start;">
                    <div style="flex:1;">
                        <div id="playlist-list" style="background:#f9fafb; padding:12px; border-radius:8px; min-height:80px; border:1px solid #e5e7eb;">
                            <!-- playlists will be rendered here -->
                        </div>
                        <div style="margin-top:12px; display:flex; gap:10px;">
                            <button onclick="promptAddPlaylist()" style="padding:10px 14px; border-radius:8px; background:linear-gradient(135deg,#10b981,#059669); color:white; border:none; cursor:pointer; font-weight:600;">＋ Thêm Playlist</button>
                            <button onclick="renderPlaylists()" style="padding:10px 14px; border-radius:8px; background:#e5e7eb; border:none; cursor:pointer;">Làm mới</button>
                        </div>
                    </div>
                    <div style="width:320px;">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:white; padding:14px; border-radius:12px;">
                            <div style="font-weight:700; margin-bottom:6px;">Hướng dẫn nhanh</div>
                            <div style="font-size:0.95em; opacity:0.95;">
                                • Nhấn <b>＋ Thêm Playlist</b> để thêm mới (tên + URL)<br>
                                • Gõ <b>từ khóa</b> (không cần chính xác) vào ô và nhấn <b>Mở</b><br>
                                • Ví dụ: gõ "nhạc" sẽ tìm "Nhạc chill", "Nhạc EDM"...<br>
                                • Voice: "mở danh sách [từ khóa]" hoặc "mở playlist [từ khóa]"
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- KNOWLEDGE BASE SECTION -->
        <div id="knowledge-section" style="display:none;">
            <div style="background: white; border-radius: 15px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.12);">
                <h2 style="color:#667eea; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                    <span>📚 Knowledge Base</span>
                    <span style="font-size: 0.5em; color: #9ca3af; font-weight: 400;">Cập nhật dữ liệu cho LLM</span>
                </h2>
                
                <!-- Nhập đường dẫn thư mục -->
                <div style="background: #f9fafb; padding: 20px; border-radius: 12px; border: 2px solid #e5e7eb; margin-bottom: 20px;">
                    <h3 style="color: #333; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
                        📁 Thư Mục Dữ Liệu
                    </h3>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <input type="text" id="knowledge-folder-path" 
                               placeholder="Nhập đường dẫn thư mục (VD: C:\Documents\MyData hoặc D:\Knowledge)" 
                               style="flex: 1; padding: 12px 15px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 1em;">
                        <button onclick="saveKnowledgeFolder()" 
                                style="padding: 12px 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; white-space: nowrap;">
                            💾 Lưu
                        </button>
                        <button onclick="scanKnowledgeFolder()" 
                                style="padding: 12px 25px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; white-space: nowrap;">
                            🔍 Quét Files
                        </button>
                    </div>
                    <p style="color: #666; font-size: 0.9em; margin-top: 10px;">
                        💡 Hỗ trợ: PDF, TXT, Word (.docx), Markdown (.md), JSON, CSV
                    </p>
                </div>
                
                <!-- Trạng thái & thống kê -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px; text-align: center;">
                        <div style="font-size: 2em; font-weight: bold;" id="kb-total-files">0</div>
                        <div style="opacity: 0.9;">Tổng số files</div>
                    </div>
                    <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 12px; text-align: center;">
                        <div style="font-size: 2em; font-weight: bold;" id="kb-indexed-files">0</div>
                        <div style="opacity: 0.9;">Đã index</div>
                    </div>
                    <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 20px; border-radius: 12px; text-align: center;">
                        <div style="font-size: 2em; font-weight: bold;" id="kb-total-size">0 KB</div>
                        <div style="opacity: 0.9;">Dung lượng</div>
                    </div>
                    <div style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); color: white; padding: 20px; border-radius: 12px; text-align: center;">
                        <div style="font-size: 2em; font-weight: bold;" id="kb-last-update">--</div>
                        <div style="opacity: 0.9;">Cập nhật lần cuối</div>
                    </div>
                </div>
                
                <!-- Danh sách files -->
                <div style="background: #f9fafb; padding: 20px; border-radius: 12px; border: 2px solid #e5e7eb;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h3 style="color: #333; display: flex; align-items: center; gap: 8px; margin: 0;">
                            📄 Danh Sách Files
                        </h3>
                        <div style="display: flex; gap: 10px;">
                            <button onclick="indexAllFiles()" 
                                    style="padding: 8px 16px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9em;">
                                🔄 Index Tất Cả
                            </button>
                            <button onclick="clearKnowledgeBase()" 
                                    style="padding: 8px 16px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9em;">
                                🗑️ Xóa Index
                            </button>
                        </div>
                    </div>
                    <div id="knowledge-file-list" style="max-height: 400px; overflow-y: auto;">
                        <p style="color: #666; text-align: center; padding: 40px;">
                            📂 Chưa có thư mục nào được cấu hình.<br>
                            Nhập đường dẫn và nhấn "Quét Files" để bắt đầu.
                        </p>
                    </div>
                </div>
                
                <!-- Hướng dẫn -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px; margin-top: 20px;">
                    <h3 style="margin-bottom: 12px;">📖 Hướng Dẫn Sử Dụng</h3>
                    <div style="font-size: 0.95em; line-height: 1.6;">
                        <p>1. <strong>Nhập đường dẫn</strong> thư mục chứa tài liệu (PDF, TXT, Word, Markdown...)</p>
                        <p>2. <strong>Nhấn "Quét Files"</strong> để liệt kê các files trong thư mục</p>
                        <p>3. <strong>Nhấn "Index Tất Cả"</strong> để LLM học từ nội dung các files</p>
                        <p>4. Sau khi index, LLM có thể trả lời câu hỏi dựa trên dữ liệu của bạn!</p>
                        <p style="margin-top: 10px; opacity: 0.9;">
                            💡 <strong>Mẹo:</strong> Đặt các tài liệu quan trọng vào một thư mục riêng để dễ quản lý.
                        </p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- SETTINGS MODAL -->
        <div id="settingsModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>⚙️ Cấu hình Endpoint</h2>
                    <button class="close-btn" onclick="closeSettingsModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <label for="endpoint-url">Endpoint (JWT Token hoặc URL đầy đủ):</label>
                    <input type="text" id="endpoint-url" placeholder="Nhập JWT token hoặc URL đầy đủ wss://api.xiaozhi.me/mcp/?token=..." />
                    <p style="color:#666;font-size:0.9em;margin-top:-10px;">
                        <strong>Lưu ý:</strong> Có thể nhập JWT token trực tiếp hoặc URL đầy đủ <code>wss://api.xiaozhi.me/mcp/?token=...</code> - hệ thống sẽ tự động xử lý
                    </p>
                    
                    <hr style="margin:25px 0;border:none;border-top:2px solid #e5e7eb;">
                    
                    <label for="gemini-api-key" style="display:flex;align-items:center;gap:10px;">
                        🤖 Gemini API Key 
                        <span style="color:#10b981;font-size:0.85em;font-weight:normal;">(Auto-save)</span>
                    </label>
                    <input 
                        type="text" 
                        id="gemini-api-key" 
                        placeholder="AIzaSyXXXXXXXXXXXXXXXXXX..."
                        oninput="autoSaveGeminiKey()"
                        style="font-family:monospace;font-size:0.9em;"
                    />
                    <p style="color:#666;font-size:0.9em;margin-top:-10px;">
                        <strong>Miễn phí:</strong> Lấy API key tại 
                        <a href="https://aistudio.google.com/apikey" target="_blank" style="color:#667eea;">
                            aistudio.google.com/apikey
                        </a>
                        <br>
                        <span id="gemini-key-status" style="color:#10b981;font-weight:600;"></span>
                    </p>
                    
                    <label for="gemini-model" style="margin-top:15px;display:block;">
                        🎯 Gemini Model
                    </label>
                    <select 
                        id="gemini-model" 
                        onchange="saveGeminiModel()"
                        style="width:100%;padding:10px;border:2px solid #e5e7eb;border-radius:8px;font-size:0.95em;"
                    >
                        <option value="models/gemini-2.0-flash-exp">⚡ Gemini 2.0 Flash (Nhanh nhất, Miễn phí)</option>
                        <option value="models/gemini-2.0-flash-thinking-exp">🧠 Gemini 2.0 Flash Thinking (Suy luận tốt)</option>
                        <option value="models/gemini-exp-1206">🚀 Gemini 2.0 Pro Exp (Chất lượng cao)</option>
                        <option value="models/gemini-1.5-pro">💎 Gemini 1.5 Pro (Ổn định)</option>
                        <option value="models/gemini-1.5-flash">⚡ Gemini 1.5 Flash (Cân bằng)</option>
                    </select>
                    <p style="color:#666;font-size:0.85em;margin-top:5px;">
                        💡 <strong>Flash:</strong> Phản hồi nhanh, tiết kiệm quota | <strong>Pro:</strong> Phân tích sâu, reasoning tốt hơn | <strong>Thinking:</strong> Suy luận phức tạp
                    </p>
                    
                    <hr style="margin:25px 0;border:none;border-top:2px solid #e5e7eb;">
                    
                    <label for="openai-api-key" style="display:flex;align-items:center;gap:10px;">
                        🧠 OpenAI API Key (GPT-4)
                        <span style="color:#10b981;font-size:0.85em;font-weight:normal;">(Auto-save)</span>
                        <span style="color:#ef4444;font-size:0.75em;font-weight:normal;">TRẢ PHÍ</span>
                    </label>
                    <input 
                        type="text" 
                        id="openai-api-key" 
                        placeholder="sk-proj-XXXXXXXXXXXXXXXXXX..."
                        oninput="autoSaveOpenAIKey()"
                        style="font-family:monospace;font-size:0.9em;"
                    />
                    <p style="color:#666;font-size:0.9em;margin-top:-10px;">
                        <strong>Trả phí:</strong> Lấy API key tại 
                        <a href="https://platform.openai.com/api-keys" target="_blank" style="color:#667eea;">
                            platform.openai.com/api-keys
                        </a>
                        <br>
                        <span style="font-size:0.85em;">💰 Giá: $0.01-0.03/1K tokens | 🆓 Free trial: $5 credit</span>
                        <br>
                        <span id="openai-key-status" style="color:#10b981;font-weight:600;"></span>
                    </p>
                    
                    <hr style="margin:25px 0;border:none;border-top:2px solid #e5e7eb;">
                    
                    <label for="serper-api-key" style="display:flex;align-items:center;gap:10px;">
                        🔍 Serper API Key (Google Search)
                        <span style="color:#10b981;font-size:0.85em;font-weight:normal;">(Auto-save)</span>
                        <span style="color:#22c55e;font-size:0.75em;font-weight:normal;">MIỄN PHÍ 2500/tháng</span>
                    </label>
                    <input 
                        type="text" 
                        id="serper-api-key" 
                        placeholder="abcdef1234567890..."
                        oninput="autoSaveSerperKey()"
                        style="font-family:monospace;font-size:0.9em;"
                    />
                    <p style="color:#666;font-size:0.9em;margin-top:-10px;">
                        <strong>Miễn phí:</strong> Đăng ký tại 
                        <a href="https://serper.dev" target="_blank" style="color:#667eea;">
                            serper.dev
                        </a>
                        <br>
                        <span style="font-size:0.85em;">🆓 2500 queries/tháng miễn phí | 🎯 Google Search chính xác hơn DuckDuckGo</span>
                        <br>
                        <span id="serper-key-status" style="color:#10b981;font-weight:600;"></span>
                    </p>
                </div>
                <div class="modal-footer">
                    <button class="modal-btn secondary" onclick="closeSettingsModal()">Hủy</button>
                    <button class="modal-btn info" onclick="copyFullUrl()">📋 Copy URL đầy đủ</button>
                    <button class="modal-btn primary" onclick="saveEndpoint()">💾 Lưu</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let ws;
        
        // Section switching
        function showSection(name) {
            document.querySelectorAll('.menu-item').forEach(item => item.classList.remove('active'));
            event.target.classList.add('active');
            
            document.getElementById('dashboard-section').style.display = name === 'dashboard' ? 'block' : 'none';
            document.getElementById('tools-section').style.display = name === 'tools' ? 'block' : 'none';
            document.getElementById('music-section').style.display = name === 'music' ? 'block' : 'none';
            document.getElementById('music-settings-section').style.display = name === 'music-settings' ? 'block' : 'none';
            document.getElementById('conversation-section').style.display = name === 'conversation' ? 'block' : 'none';
            document.getElementById('playlist-section').style.display = name === 'playlist' ? 'block' : 'none';
            document.getElementById('knowledge-section').style.display = name === 'knowledge' ? 'block' : 'none';
            
            // Load conversation when opening conversation section
            if (name === 'conversation') {
                loadConversationHistory();
            }
            
            // Load music library when opening music section
            if (name === 'music') {
                loadMusicSourcePreference();
                updateMusicStatus();
            }
            if (name === 'music-settings') {
                loadMusicFolderSettings();
            }
            
            // Load playlist when opening playlist section
            if (name === 'playlist') {
                // use initPlaylists() (render existing playlists) - loadPlaylistSection was removed
                initPlaylists();
            }
            
            // Load knowledge base when opening knowledge section
            if (name === 'knowledge') {
                loadKnowledgeBase();
            }
        }
        
        // Tab switching
        function switchTab(index) {
            document.querySelectorAll('.tab-btn').forEach((btn, i) => btn.classList.toggle('active', i === index));
            document.querySelectorAll('.tab-content').forEach((content, i) => content.classList.toggle('active', i === index));
        }
        
        // Quick actions - 20 tools
        function setVolumePrompt() {
            const level = prompt('Nhập âm lượng (0-100):', '50');
            if (level === null) return;
            const levelNum = parseInt(level);
            if (isNaN(levelNum) || levelNum < 0 || levelNum > 100) {
                addLog('❌ Âm lượng phải từ 0-100', 'error');
                return;
            }
            setVolumeQuick(levelNum);
        }
        function setVolumeQuick(level) { 
            if (level >= 0 && level <= 100) {
                callTool('set_volume', {level});
            } else {
                addLog('❌ Âm lượng phải từ 0-100', 'error');
            }
        }
        function getVolumeInfo() {
            callTool('get_volume', {});
        }
        function screenshot() { callAPI('/api/screenshot', {}); }
        function notification() { callAPI('/api/notification', {title: 'Xiaozhi', message: 'Test notification'}); }
        function setBrightness() { 
            const level = prompt('Nhập độ sáng (0-100):', '50');
            if (level === null) return;
            const levelNum = parseInt(level);
            if (isNaN(levelNum) || levelNum < 0 || levelNum > 100) {
                addLog('❌ Độ sáng phải từ 0-100', 'error');
                return;
            }
            callTool('set_brightness', {level: levelNum});
        }
        function openApp() {
            const app = prompt('Nhập tên app (notepad/calc/paint/cmd/explorer):', 'notepad');
            if (app && app.trim()) callTool('open_application', {app_name: app.trim()});
        }
        function listProcesses() { callTool('list_running_processes', {limit: 10}); }
        function killProcess() {
            const id = prompt('Nhập PID hoặc tên tiến trình:', 'chrome');
            if (id && id.trim()) callTool('kill_process', {identifier: id.trim()});
        }
        function createFile() {
            const path = prompt('Đường dẫn file:', 'C:/test.txt');
            if (!path || !path.trim()) return;
            const content = prompt('Nội dung:', 'Hello World');
            if (content !== null) callTool('create_file', {path: path.trim(), content});
        }
        function readFile() {
            const path = prompt('Đường dẫn file:', 'C:/test.txt');
            if (path && path.trim()) callTool('read_file', {path: path.trim()});
        }
        function listFiles() {
            const dir = prompt('Thư mục:', 'C:/Users');
            if (dir && dir.trim()) callTool('list_files', {directory: dir.trim()});
        }
        function diskUsage() { callTool('get_disk_usage', {}); }
        function networkInfo() { callTool('get_network_info', {}); }
        function batteryStatus() { callTool('get_battery_status', {}); }
        function searchWeb() {
            const query = prompt('Từ khóa tìm kiếm:', '');
            if (query && query.trim()) callTool('search_web', {query: query.trim()});
        }
        function calculator() {
            const expr = prompt('Biểu thức toán học:', '2+2*3');
            if (expr && expr.trim()) callAPI('/api/calculator', {expression: expr.trim()});
        }
        function getClipboard() { callTool('get_clipboard', {}); }
        function setClipboard() {
            const text = prompt('Nội dung cần copy:', '');
            if (text !== null && text.trim()) callTool('set_clipboard', {text: text.trim()});
        }
        function playSound() {
            const freq = prompt('Tần số Hz (200-2000):', '1000');
            if (freq === null) return;
            const dur = prompt('Thời gian ms (100-3000):', '500');
            if (dur === null) return;
            const freqNum = parseInt(freq);
            const durNum = parseInt(dur);
            if (isNaN(freqNum) || freqNum < 200 || freqNum > 2000) {
                addLog('❌ Tần số phải từ 200-2000 Hz', 'error');
                return;
            }
            if (isNaN(durNum) || durNum < 100 || durNum > 3000) {
                addLog('❌ Thời gian phải từ 100-3000 ms', 'error');
                return;
            }
            callTool('play_sound', {frequency: freqNum, duration: durNum});
        }
        
        // NEW TOOL FUNCTIONS
        function lockComputer() {
            if (confirm('Bạn có chắc muốn khóa máy tính?')) {
                callTool('lock_computer', {});
            }
        }
        function shutdownSchedule() {
            const action = prompt('Hành động (shutdown/restart/cancel):', 'shutdown');
            if (!action || !action.trim()) return;
            const actionLower = action.trim().toLowerCase();
            if (!['shutdown', 'restart', 'cancel'].includes(actionLower)) {
                addLog('❌ Hành động không hợp lệ. Dùng: shutdown, restart, hoặc cancel', 'error');
                return;
            }
            const delay = prompt('Trì hoãn (giây):', '60');
            if (delay === null) return;
            const delayNum = parseInt(delay) || 0;
            if (delayNum < 0) {
                addLog('❌ Thời gian trì hoãn phải >= 0', 'error');
                return;
            }
            callTool('shutdown_schedule', {action: actionLower, delay: delayNum});
        }
        function showDesktop() {
            callTool('show_desktop', {});
        }
        function undoOperation() {
            callTool('undo_operation', {});
        }
        function setTheme() {
            const dark = confirm('Chọn OK cho theme TỐI, Cancel cho theme SÁNG');
            callTool('set_theme', {dark_mode: dark});
        }
        function changeWallpaper() {
            const keyword = prompt('Từ khóa hình nền (hoặc để trống để chọn ngẫu nhiên):', '');
            callTool('change_wallpaper', {keyword: keyword || ''});
        }
        function getDesktopPath() {
            callTool('get_desktop_path', {});
        }
        function pasteContent() {
            const content = prompt('Nhập nội dung cần dán (hoặc để trống để dán clipboard hiện tại):', '');
            callTool('paste_content', {content: content || ''});
        }
        function pressEnter() {
            callTool('press_enter', {});
        }
        function findInDocument() {
            const searchText = prompt('Nhập nội dung tìm kiếm:', '');
            if (searchText && searchText.trim()) {
                callTool('find_in_document', {search_text: searchText.trim()});
            }
        }
        
        // AI ASSISTANT
        function saveGeminiModel() {
            const select = document.getElementById('gemini-model');
            if (!select) return;
            const model = select.value;
            localStorage.setItem('gemini_model', model);
            
            // Determine model name for display
            let modelName = 'Unknown';
            if (model.includes('flash-thinking')) modelName = 'Thinking 🧠';
            else if (model.includes('flash')) modelName = 'Flash ⚡';
            else if (model.includes('exp-1206')) modelName = 'Pro Exp 🚀';
            else if (model.includes('1.5-pro')) modelName = '1.5 Pro 💎';
            else if (model.includes('pro')) modelName = 'Pro 🚀';
            
            addLog(`✅ Đã lưu Gemini model: ${modelName}`, 'success');
        }
        
        function loadGeminiModel() {
            const saved = localStorage.getItem('gemini_model') || 'models/gemini-2.0-flash-exp';
            const select = document.getElementById('gemini-model');
            if (select) {
                // Check if the saved value exists in options
                const options = Array.from(select.options).map(o => o.value);
                if (options.includes(saved)) {
                    select.value = saved;
                } else {
                    // Default to first option if saved value is invalid
                    select.value = 'models/gemini-2.0-flash-exp';
                    localStorage.setItem('gemini_model', 'models/gemini-2.0-flash-exp');
                }
            }
        }
        
        function getGeminiModelName(model) {
            if (model.includes('flash-thinking')) return 'Thinking 🧠';
            if (model.includes('2.0-flash')) return '2.0 Flash ⚡';
            if (model.includes('1.5-flash')) return '1.5 Flash ⚡';
            if (model.includes('exp-1206')) return '2.0 Pro 🚀';
            if (model.includes('1.5-pro')) return '1.5 Pro 💎';
            return 'Gemini';
        }
        
        function askGemini() {
            const prompt = window.prompt('Hỏi Gemini AI (MIỄN PHÍ - ví dụ: What is Python?):', '');
            if (prompt && prompt.trim()) {
                const model = localStorage.getItem('gemini_model') || 'models/gemini-2.0-flash-exp';
                const modelName = getGeminiModelName(model);
                addLog(`🤖 Hỏi Gemini ${modelName}: "${prompt}"`, 'info');
                
                // Use generic /api/call_tool endpoint
                fetch('/api/call_tool', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({tool: 'ask_gemini', args: {prompt: prompt.trim(), model: model}})
                })
                .then(res => res.json())
                .then(result => {
                    if(result.success) {
                        addLog(`✅ Gemini: ${result.response_text.substring(0, 200)}...`, 'success');
                    } else {
                        addLog(`❌ Gemini error: ${result.error}`, 'error');
                    }
                })
                .catch(err => addLog(`❌ Error: ${err.message}`, 'error'));
            }
        }
        
        function askGPT4() {
            const prompt = window.prompt('Hỏi GPT-4 (TRẢ PHÍ - chất lượng cao nhất):', '');
            if (prompt && prompt.trim()) {
                addLog(`🧠 Hỏi GPT-4: "${prompt}"`, 'info');
                
                // Use generic /api/call_tool endpoint
                fetch('/api/call_tool', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({tool: 'ask_gpt4', args: {prompt: prompt.trim()}})
                })
                .then(res => res.json())
                .then(result => {
                    if(result.success) {
                        const usage = result.usage ? ` (Tokens: ${result.usage.total_tokens})` : '';
                        addLog(`✅ GPT-4: ${result.response_text.substring(0, 200)}...${usage}`, 'success');
                    } else {
                        addLog(`❌ GPT-4 error: ${result.error}`, 'error');
                    }
                })
                .catch(err => addLog(`❌ Error: ${err.message}`, 'error'));
            }
        }

        // API caller
        async function callAPI(endpoint, data) {
            try {
                addLog(`🔧 Calling ${endpoint}...`, 'info');
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                addLog(`✅ ${JSON.stringify(result).substring(0, 100)}`, 'success');
                return result;
            } catch (error) {
                addLog(`❌ Error: ${error.message}`, 'error');
                return {success: false, error: error.message};
            }
        }
        
        async function callTool(name, params) {
            try {
                addLog(`🛠️ Tool: ${name}`, 'info');
                // Gọi API endpoint tương ứng với tool
                const endpoint = `/api/tool/${name}`;
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(params)
                });
                const result = await response.json();
                addLog(`✅ ${name}: ${JSON.stringify(result).substring(0, 150)}`, 'success');
                return result;
            } catch (error) {
                addLog(`❌ Tool error: ${error.message}`, 'error');
                return {success: false, error: error.message};
            }
        }
        
        async function getResources() {
            try {
                // Sử dụng cache nếu còn hiệu lực
                const now = Date.now();
                if (resourceCache && (now - lastResourceFetch) < RESOURCE_CACHE_TIME) {
                    return;
                }
                
                const response = await fetch('/api/resources');
                const data = await response.json();
                if (data.success) {
                    const cpuPercent = data.data.cpu_percent;
                    document.getElementById('cpu').textContent = cpuPercent + '%';
                    document.getElementById('ram').textContent = data.data.memory_percent + '%';
                    document.getElementById('disk').textContent = data.data.disk_percent + '%';
                    
                    // Update RunCat animation speed based on CPU usage
                    updateRunCatSpeed(cpuPercent);
                    
                    // Cập nhật cache
                    resourceCache = data;
                    lastResourceFetch = now;
                } else {
                    addLog(`❌ Lỗi lấy tài nguyên: ${data.error}`, 'error');
                }
            } catch (error) {
                addLog(`❌ ${error.message}`, 'error');
            }
        }
        
        // Update RunCat animation speed based on CPU usage (like RunCat365)
        function updateRunCatSpeed(cpuPercent) {
            // Calculate frame duration: 100ms (very fast) to 800ms (very slow)
            // High CPU = fast running, Low CPU = slow walking
            const minSpeed = 100;  // Fast run (10 fps)
            const maxSpeed = 800;  // Slow walk (1.25 fps)
            
            // CPU 0% = 800ms, CPU 100% = 100ms
            runcatSpeed = maxSpeed - (cpuPercent / 100) * (maxSpeed - minSpeed);
        }
        
        // Debounce helper
        function debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
        
        async function calculate() {
            try {
                const expr = document.getElementById('calc-expr').value.trim();
                if (!expr) {
                    document.getElementById('calc-result').textContent = 'Vui lòng nhập biểu thức';
                    return;
                }
                const response = await fetch('/api/calculator', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({expression: expr})
                });
                const data = await response.json();
                document.getElementById('calc-result').textContent = data.success ? data.result : data.error;
            } catch (error) {
                document.getElementById('calc-result').textContent = 'Lỗi: ' + error.message;
            }
        }
        
        async function getCurrentTime() {
            try {
                const response = await fetch('/api/time');
                const data = await response.json();
                if (data.data) {
                    document.getElementById('time-result').textContent = data.data.datetime;
                }
            } catch (error) {
                document.getElementById('time-result').textContent = 'Lỗi: ' + error.message;
            }
        }
        
        // Modal functions
        function openSettingsModal() {
            document.getElementById('settingsModal').style.display = 'block';
            loadCurrentEndpoint();
            loadGeminiModel();
        }
        
        function closeSettingsModal() {
            document.getElementById('settingsModal').style.display = 'none';
        }
        
        // Click outside modal to close
        window.onclick = function(event) {
            const modal = document.getElementById('settingsModal');
            if (event.target === modal) {
                closeSettingsModal();
            }
        }
        
        async function loadCurrentEndpoint() {
            try {
                const response = await fetch('/api/endpoints');
                const data = await response.json();
                
                // Tìm thiết bị đang active (Thiết bị 3 - index 2)
                const activeDevice = data.endpoints[2]; // Thiết bị 3
                
                if (activeDevice && activeDevice.token) {
                    document.getElementById('endpoint-url').value = activeDevice.token;
                }
                
                // Load Gemini API key
                if (data.gemini_api_key) {
                    document.getElementById('gemini-api-key').value = data.gemini_api_key;
                    updateGeminiKeyStatus('✓ API key đã cấu hình', '#10b981');
                }
                
                // Load OpenAI API key
                if (data.openai_api_key) {
                    document.getElementById('openai-api-key').value = data.openai_api_key;
                    updateOpenAIKeyStatus('✓ API key đã cấu hình', '#10b981');
                }
                
                // Load Serper API key (Google Search)
                if (data.serper_api_key) {
                    document.getElementById('serper-api-key').value = data.serper_api_key;
                    updateSerperKeyStatus('✓ Google Search sẵn sàng', '#10b981');
                }
                
                // Cập nhật thông tin hiện tại trong config section
                if (document.getElementById('current-device-name')) {
                    document.getElementById('current-device-name').textContent = activeDevice?.name || 'Chưa cấu hình';
                }
                if (document.getElementById('current-device-token')) {
                    const token = activeDevice?.token || 'Chưa có token';
                    document.getElementById('current-device-token').textContent = 
                        token.length > 50 ? token.substring(0, 50) + '...' : token;
                }
            } catch (error) {
                addLog('❌ Lỗi tải endpoint: ' + error.message, 'error');
            }
        }
        
        // Auto-save Gemini API key
        let geminiSaveTimeout;
        async function autoSaveGeminiKey() {
            clearTimeout(geminiSaveTimeout);
            
            geminiSaveTimeout = setTimeout(async () => {
                const apiKey = document.getElementById('gemini-api-key').value.trim();
                
                if (!apiKey) {
                    updateGeminiKeyStatus('', '');
                    return;
                }
                
                try {
                    updateGeminiKeyStatus('💾 Đang lưu...', '#f59e0b');
                    
                    const response = await fetch('/api/gemini-key', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({api_key: apiKey})
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        updateGeminiKeyStatus('✓ Đã lưu tự động', '#10b981');
                        setTimeout(() => updateGeminiKeyStatus('✓ API key đã cấu hình', '#10b981'), 2000);
                    } else {
                        updateGeminiKeyStatus('❌ Lỗi: ' + result.error, '#ef4444');
                    }
                } catch (error) {
                    updateGeminiKeyStatus('❌ Lỗi kết nối', '#ef4444');
                }
            }, 1000); // Auto-save sau 1 giây không gõ
        }
        
        function updateGeminiKeyStatus(message, color) {
            const statusEl = document.getElementById('gemini-key-status');
            if (statusEl) {
                statusEl.textContent = message;
                statusEl.style.color = color;
            }
        }
        
        // Auto-save OpenAI API key
        let openaiSaveTimeout;
        async function autoSaveOpenAIKey() {
            clearTimeout(openaiSaveTimeout);
            
            openaiSaveTimeout = setTimeout(async () => {
                const apiKey = document.getElementById('openai-api-key').value.trim();
                
                if (!apiKey) {
                    updateOpenAIKeyStatus('', '');
                    return;
                }
                
                try {
                    updateOpenAIKeyStatus('💾 Đang lưu...', '#f59e0b');
                    
                    const response = await fetch('/api/openai-key', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({api_key: apiKey})
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        updateOpenAIKeyStatus('✓ Đã lưu tự động', '#10b981');
                        setTimeout(() => updateOpenAIKeyStatus('✓ API key đã cấu hình', '#10b981'), 2000);
                    } else {
                        updateOpenAIKeyStatus('❌ Lỗi: ' + result.error, '#ef4444');
                    }
                } catch (error) {
                    updateOpenAIKeyStatus('❌ Lỗi kết nối', '#ef4444');
                }
            }, 1000);
        }
        
        function updateOpenAIKeyStatus(message, color) {
            const statusEl = document.getElementById('openai-key-status');
            if (statusEl) {
                statusEl.textContent = message;
                statusEl.style.color = color;
            }
        }
        
        // Auto-save Serper API key (Google Search)
        let serperSaveTimeout;
        async function autoSaveSerperKey() {
            clearTimeout(serperSaveTimeout);
            
            serperSaveTimeout = setTimeout(async () => {
                const apiKey = document.getElementById('serper-api-key').value.trim();
                
                if (!apiKey) {
                    updateSerperKeyStatus('', '');
                    return;
                }
                
                try {
                    updateSerperKeyStatus('💾 Đang lưu...', '#f59e0b');
                    
                    const response = await fetch('/api/serper-key', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({api_key: apiKey})
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        updateSerperKeyStatus('✓ Đã lưu - Google Search sẵn sàng!', '#10b981');
                        setTimeout(() => updateSerperKeyStatus('✓ API key đã cấu hình', '#10b981'), 2000);
                    } else {
                        updateSerperKeyStatus('❌ Lỗi: ' + result.error, '#ef4444');
                    }
                } catch (error) {
                    updateSerperKeyStatus('❌ Lỗi kết nối', '#ef4444');
                }
            }, 1000);
        }
        
        function updateSerperKeyStatus(message, color) {
            const statusEl = document.getElementById('serper-key-status');
            if (statusEl) {
                statusEl.textContent = message;
                statusEl.style.color = color;
            }
        }
        
        async function saveEndpoint() {
            let input = document.getElementById('endpoint-url').value.trim();
            
            if (!input) {
                addLog('❌ Vui lòng nhập JWT token hoặc URL đầy đủ!', 'error');
                return;
            }
            
            let token = input;
            
            // Nếu user nhập URL đầy đủ, extract token từ URL
            if (input.startsWith('wss://') || input.startsWith('http')) {
                try {
                    const url = new URL(input);
                    const tokenParam = url.searchParams.get('token');
                    if (tokenParam) {
                        token = tokenParam;
                        addLog('✅ Đã tự động extract token từ URL', 'info');
                    } else {
                        addLog('❌ URL không chứa token parameter!', 'error');
                        return;
                    }
                } catch (e) {
                    addLog('❌ URL không hợp lệ!', 'error');
                    return;
                }
            }
            
            try {
                addLog('⏳ Đang lưu endpoint...', 'info');
                
                // Lấy danh sách thiết bị hiện tại
                const response = await fetch('/api/endpoints');
                const data = await response.json();
                
                // Cập nhật token cho Thiết bị 3 (index 2)
                const devices = data.endpoints.map((device, index) => {
                    if (index === 2) { // Thiết bị 3
                        return {
                            name: 'Thiết bị 3',
                            token: token,
                            enabled: true
                        };
                    }
                    return device;
                });
                
                // Lưu cấu hình
                const saveResponse = await fetch('/api/endpoints/save', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({devices: devices})
                });
                
                const saveData = await saveResponse.json();
                
                if (saveData.success) {
                    addLog('✅ Đã lưu endpoint thành công!', 'success');
                    
                    // Chuyển sang thiết bị 3
                    const switchResponse = await fetch('/api/endpoints/switch/2', {method: 'POST'});
                    const switchData = await switchResponse.json();
                    
                    if (switchData.success) {
                        addLog('✅ ' + switchData.message, 'success');
                    }
                    
                    closeSettingsModal();
                    
                    // Reload trang sau 2 giây để kết nối lại
                    setTimeout(() => {
                        location.reload();
                    }, 2000);
                } else {
                    addLog('❌ Lỗi: ' + saveData.error, 'error');
                }
            } catch (error) {
                addLog('❌ Lỗi lưu endpoint: ' + error.message, 'error');
            }
        }
        
        function copyFullUrl() {
            const input = document.getElementById('endpoint-url').value.trim();
            if (!input) {
                addLog('❌ Không có dữ liệu để copy!', 'error');
                return;
            }
            
            let token = input;
            
            // Nếu user đã nhập URL đầy đủ, extract token
            if (input.startsWith('wss://') || input.startsWith('http')) {
                try {
                    const url = new URL(input);
                    const tokenParam = url.searchParams.get('token');
                    if (tokenParam) {
                        token = tokenParam;
                    }
                } catch (e) {
                    addLog('❌ URL không hợp lệ!', 'error');
                    return;
                }
            }
            
            // Tạo URL đầy đủ
            const fullUrl = `wss://api.xiaozhi.me/mcp/?token=${token}`;
            
            // Copy vào clipboard
            navigator.clipboard.writeText(fullUrl).then(() => {
                addLog('✅ Đã copy URL đầy đủ vào clipboard!', 'success');
            }).catch(err => {
                addLog('❌ Lỗi copy: ' + err.message, 'error');
            });
        }
        
        // Legacy functions (kept for compatibility, but hidden from UI)
        async function loadDevices() {
            try {
                const response = await fetch('/api/endpoints');
                const data = await response.json();
                
                // Update current endpoint info in config section
                const activeDevice = data.endpoints[2]; // Thiết bị 3
                if (document.getElementById('current-device-name')) {
                    document.getElementById('current-device-name').textContent = activeDevice?.name || 'Chưa cấu hình';
                }
                if (document.getElementById('current-device-token')) {
                    const token = activeDevice?.token || 'Chưa có token';
                    document.getElementById('current-device-token').textContent = 
                        token.length > 50 ? token.substring(0, 50) + '...' : token;
                }
            } catch (error) {
                addLog('❌ Lỗi tải danh sách thiết bị: ' + error.message, 'error');
            }
        }

        function addLog(message, type = 'info') {
            const log = document.getElementById('log');
            if (!log) return;
            const entry = document.createElement('div');
            entry.className = `log-entry log-${type}`;
            const time = new Date().toLocaleTimeString();
            entry.innerHTML = `<span class="log-time">${time}</span> ${message}`;
            log.insertBefore(entry, log.firstChild);
            
            // Giới hạn 50 logs thay vì 100 để giảm DOM size
            if (log.children.length > 50) {
                // Xóa nhiều logs cùng lúc để tránh reflow nhiều lần
                while (log.children.length > 50) {
                    log.removeChild(log.lastChild);
                }
            }
        }
        
        // WebSocket với reconnect optimization
        let wsReconnectAttempts = 0;
        const MAX_RECONNECT_DELAY = 30000; // Max 30s
        
        function connectWS() {
            ws = new WebSocket(`ws://${window.location.host}/ws`);
            ws.onopen = () => {
                addLog('✅ WebSocket connected', 'success');
                wsReconnectAttempts = 0; // Reset counter khi connect thành công
            };
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'xiaozhi_status') {
                    const badge = document.getElementById('xiaozhi-status');
                    const text = document.getElementById('xiaozhi-text');
                    if (data.connected) {
                        badge.className = 'status-badge online';
                        text.textContent = 'Connected';
                    } else {
                        badge.className = 'status-badge offline';
                        text.textContent = 'Disconnected';
                    }
                } else if (data.type === 'xiaozhi_activity') {
                    if (data.method !== 'ping') {
                        addLog(`📡 Xiaozhi: ${data.method}`, 'info');
                    }
                }
            };
            ws.onclose = () => {
                addLog('❌ WebSocket disconnected', 'error');
                // Exponential backoff cho reconnect
                wsReconnectAttempts++;
                const delay = Math.min(1000 * Math.pow(2, wsReconnectAttempts), MAX_RECONNECT_DELAY);
                setTimeout(connectWS, delay);
            };
        }
        
        // Caching và optimization
        let resourceCache = null;
        let lastResourceFetch = 0;
        const RESOURCE_CACHE_TIME = 3000; // Cache 3 giây
        
        // Playlist list functions (sử dụng API backend thay vì localStorage)
        async function getPlaylists() {
            try {
                const response = await fetch('/api/youtube_playlists');
                const data = await response.json();
                return data.success ? data.playlists : [];
            } catch (e) {
                console.error('Failed to load playlists from API', e);
                return [];
            }
        }

        async function renderPlaylists() {
            const list = await getPlaylists();
            const container = document.getElementById('playlist-list');
            if (!container) return;
            container.innerHTML = '';

            if (list.length === 0) {
                container.innerHTML = '<div style="color:#666;padding:12px;">Chưa có playlist nào. Nhấn "＋ Thêm Playlist" để thêm.</div>';
                return;
            }

            list.forEach((item, idx) => {
                const row = document.createElement('div');
                row.style.display = 'flex';
                row.style.alignItems = 'center';
                row.style.justifyContent = 'space-between';
                row.style.padding = '8px';
                row.style.borderBottom = '1px solid #eee';

                const left = document.createElement('div');
                left.style.display = 'flex';
                left.style.flexDirection = 'column';
                left.style.gap = '4px';

                const name = document.createElement('div');
                name.textContent = item.name;
                name.style.fontWeight = '700';
                name.style.color = '#333';

                const url = document.createElement('div');
                url.textContent = item.url;
                url.style.fontSize = '0.85em';
                url.style.color = '#666';

                left.appendChild(name);
                left.appendChild(url);

                const actions = document.createElement('div');
                actions.style.display = 'flex';
                actions.style.gap = '8px';

                const openBtn = document.createElement('button');
                openBtn.textContent = '▶';
                openBtn.title = 'Mở playlist';
                openBtn.style.padding = '6px 10px';
                openBtn.style.borderRadius = '6px';
                openBtn.style.border = 'none';
                openBtn.style.background = '#10b981';
                openBtn.style.color = 'white';
                openBtn.style.cursor = 'pointer';
                openBtn.onclick = () => openPlaylistByName(item.name);

                const delBtn = document.createElement('button');
                delBtn.textContent = '🗑';
                delBtn.title = 'Xóa playlist';
                delBtn.style.padding = '6px 10px';
                delBtn.style.borderRadius = '6px';
                delBtn.style.border = 'none';
                delBtn.style.background = '#ef4444';
                delBtn.style.color = 'white';
                delBtn.style.cursor = 'pointer';
                delBtn.onclick = () => { if (confirm('Xóa playlist "' + item.name + '"?')) { removePlaylistByName(item.name); } };

                actions.appendChild(openBtn);
                actions.appendChild(delBtn);

                row.appendChild(left);
                row.appendChild(actions);

                container.appendChild(row);
            });
        }

        function promptAddPlaylist() {
            const name = prompt('Nhập tên playlist (ví dụ: "Nhạc chill"):');
            if (!name) return;
            const url = prompt('Dán link playlist YouTube (hoặc video trong playlist):');
            if (!url) return;
            addPlaylist(name.trim(), url.trim());
        }

        async function addPlaylist(name, url) {
            if (!name || !url) {
                addLog('❌ Tên và URL không được để trống', 'error');
                return;
            }
            try {
                const response = await fetch('/api/youtube_playlists/add', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, url})
                });
                const data = await response.json();
                if (data.success) {
                    await renderPlaylists();
                    addLog('✅ Đã thêm playlist: ' + name, 'success');
                } else {
                    addLog('❌ ' + (data.error || 'Không thể thêm playlist'), 'error');
                }
            } catch (e) {
                console.error('Failed to add playlist', e);
                addLog('❌ Lỗi khi thêm playlist', 'error');
            }
        }

        async function removePlaylistByName(name) {
            try {
                const response = await fetch('/api/youtube_playlists/remove', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name})
                });
                const data = await response.json();
                if (data.success) {
                    await renderPlaylists();
                    addLog('🗑 Đã xóa playlist: ' + name, 'info');
                } else {
                    addLog('❌ ' + (data.error || 'Không thể xóa playlist'), 'error');
                }
            } catch (e) {
                console.error('Failed to remove playlist', e);
                addLog('❌ Lỗi khi xóa playlist', 'error');
            }
        }

        async function openPlaylistByName(name) {
            const list = await getPlaylists();
            const item = list.find(p => p.name === name);
            if (item) {
                window.open(item.url, '_blank');
                addLog('▶ Mở playlist: ' + name, 'info');
            }
        }

        // Expose function for voice/AI integration: open by keyword search (fuzzy matching)
        async function triggerPlayByName(keyword) {
            if (!keyword || keyword.trim() === '') return false;
            
            keyword = keyword.trim().toLowerCase();
            const list = await getPlaylists();
            
            if (list.length === 0) {
                addLog('⚠ Danh sách playlist trống. Hãy thêm playlist trước!', 'error');
                return false;
            }
            
            // Bước 1: Tìm chính xác (exact match)
            let found = list.find(item => item.name.toLowerCase() === keyword);
            
            // Bước 2: Tìm bắt đầu bằng từ khóa (starts with)
            if (!found) {
                found = list.find(item => item.name.toLowerCase().startsWith(keyword));
            }
            
            // Bước 3: Tìm chứa từ khóa (contains)
            if (!found) {
                found = list.find(item => item.name.toLowerCase().includes(keyword));
            }
            
            // Bước 4: Tìm theo từng từ trong tên playlist
            if (!found) {
                found = list.find(item => {
                    const words = item.name.toLowerCase().split(/\\s+/);
                    return words.some(word => word.includes(keyword) || keyword.includes(word));
                });
            }
            
            if (found) {
                window.open(found.url, '_blank');
                addLog('🔊 Phát playlist: "' + found.name + '" (từ khóa: "' + keyword + '")', 'success');
                return true;
            } else {
                // Hiển thị gợi ý các playlist có sẵn
                const suggestions = list.map(item => item.name).slice(0, 5).join(', ');
                addLog('⚠ Không tìm thấy playlist với từ khóa: "' + keyword + '"', 'error');
                addLog('💡 Gợi ý: ' + suggestions, 'info');
                return false;
            }
        }
        
        // Hàm mở playlist nhanh (alias) - dễ nhớ hơn cho voice command
        function moPlaylist(keyword) {
            return triggerPlayByName(keyword);
        }
        
        function danhSachNhac(keyword) {
            return triggerPlayByName(keyword);
        }

        // Initialize playlist list on load
        function initPlaylists() {
            renderPlaylists();
        }
        
        // ============================================================
        // KNOWLEDGE BASE FUNCTIONS
        // ============================================================
        
        async function loadKnowledgeBase() {
            try {
                const response = await fetch('/api/knowledge/status');
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('knowledge-folder-path').value = data.folder_path || '';
                    document.getElementById('kb-total-files').textContent = data.total_files || 0;
                    document.getElementById('kb-indexed-files').textContent = data.indexed_files || 0;
                    document.getElementById('kb-total-size').textContent = formatFileSize(data.total_size || 0);
                    document.getElementById('kb-last-update').textContent = data.last_update || '--';
                    
                    if (data.files && data.files.length > 0) {
                        renderKnowledgeFiles(data.files);
                    }
                }
            } catch (error) {
                console.error('Error loading knowledge base:', error);
            }
        }
        
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
        }
        
        function renderKnowledgeFiles(files) {
            const container = document.getElementById('knowledge-file-list');
            if (!files || files.length === 0) {
                container.innerHTML = '<p style="color: #666; text-align: center; padding: 40px;">📂 Không tìm thấy file nào.</p>';
                return;
            }
            
            const fileIcons = {
                'pdf': '📕',
                'txt': '📄',
                'docx': '📘',
                'doc': '📘',
                'md': '📝',
                'json': '📋',
                'csv': '📊',
                'xlsx': '📗',
                'xls': '📗'
            };
            
            let html = '<div style="display: flex; flex-direction: column; gap: 8px;">';
            files.forEach((file, index) => {
                const ext = file.name.split('.').pop().toLowerCase();
                const icon = fileIcons[ext] || '📄';
                const indexed = file.indexed ? '✅' : '⏳';
                const escapedPath = btoa(unescape(encodeURIComponent(file.path))); // Base64 encode để tránh lỗi escape
                
                html += `
                    <div style="display: flex; align-items: center; padding: 12px; background: white; border-radius: 8px; border: 1px solid #e5e7eb; gap: 12px;">
                        <span style="font-size: 1.5em;">${icon}</span>
                        <div style="flex: 1;">
                            <div style="font-weight: 600; color: #333;">${file.name}</div>
                            <div style="font-size: 0.85em; color: #666;">${formatFileSize(file.size)} • ${file.modified || ''}</div>
                        </div>
                        <span title="${file.indexed ? 'Đã index' : 'Chưa index'}">${indexed}</span>
                        <button onclick="indexSingleFileB64('${escapedPath}')" 
                                style="padding: 6px 12px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.85em;">
                            Index
                        </button>
                    </div>
                `;
            });
            html += '</div>';
            container.innerHTML = html;
        }
        
        async function saveKnowledgeFolder() {
            const folderPath = document.getElementById('knowledge-folder-path').value.trim();
            console.log('[Knowledge] saveKnowledgeFolder called, path:', folderPath);
            if (!folderPath) {
                addLog('❌ Vui lòng nhập đường dẫn thư mục', 'error');
                alert('Vui lòng nhập đường dẫn thư mục!');
                return;
            }
            
            try {
                addLog('💾 Đang lưu cấu hình thư mục...', 'info');
                console.log('[Knowledge] Calling API /api/knowledge/set_folder');
                const response = await fetch('/api/knowledge/set_folder', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ folder_path: folderPath })
                });
                console.log('[Knowledge] Response status:', response.status);
                const data = await response.json();
                console.log('[Knowledge] Response data:', data);
                
                if (data.success) {
                    addLog('✅ ' + data.message, 'success');
                    alert('✅ ' + data.message);
                    loadKnowledgeBase();
                } else {
                    addLog('❌ ' + (data.error || 'Lỗi không xác định'), 'error');
                    alert('❌ ' + (data.error || 'Lỗi không xác định'));
                }
            } catch (error) {
                console.error('[Knowledge] Error:', error);
                addLog('❌ Lỗi: ' + error.message, 'error');
                alert('❌ Lỗi: ' + error.message);
            }
        }
        
        async function scanKnowledgeFolder() {
            const folderPath = document.getElementById('knowledge-folder-path').value.trim();
            console.log('[Knowledge] scanKnowledgeFolder called, path:', folderPath);
            if (!folderPath) {
                addLog('❌ Vui lòng nhập đường dẫn thư mục trước', 'error');
                alert('Vui lòng nhập đường dẫn thư mục trước!');
                return;
            }
            
            try {
                addLog('🔍 Đang quét thư mục...', 'info');
                console.log('[Knowledge] Calling API /api/knowledge/scan');
                const response = await fetch('/api/knowledge/scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ folder_path: folderPath })
                });
                console.log('[Knowledge] Response status:', response.status);
                const data = await response.json();
                console.log('[Knowledge] Response data:', data);
                
                if (data.success) {
                    addLog('✅ Tìm thấy ' + data.total_files + ' files', 'success');
                    document.getElementById('kb-total-files').textContent = data.total_files;
                    document.getElementById('kb-total-size').textContent = formatFileSize(data.total_size);
                    renderKnowledgeFiles(data.files);
                } else {
                    addLog('❌ ' + (data.error || 'Lỗi không xác định'), 'error');
                    alert('❌ ' + (data.error || 'Lỗi không xác định'));
                }
            } catch (error) {
                console.error('[Knowledge] Scan error:', error);
                addLog('❌ Lỗi: ' + error.message, 'error');
                alert('❌ Lỗi: ' + error.message);
            }
        }
        
        async function indexAllFiles() {
            try {
                addLog('🔄 Đang index tất cả files...', 'info');
                const response = await fetch('/api/knowledge/index_all', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                const data = await response.json();
                
                if (data.success) {
                    addLog('✅ ' + data.message, 'success');
                    document.getElementById('kb-indexed-files').textContent = data.indexed_count;
                    document.getElementById('kb-last-update').textContent = data.last_update || 'Vừa xong';
                    loadKnowledgeBase();
                } else {
                    addLog('❌ ' + (data.error || 'Lỗi không xác định'), 'error');
                }
            } catch (error) {
                addLog('❌ Lỗi: ' + error.message, 'error');
            }
        }
        
        // Decode Base64 path và gọi indexSingleFile
        async function indexSingleFileB64(base64Path) {
            try {
                const filePath = decodeURIComponent(escape(atob(base64Path)));
                await indexSingleFile(filePath);
            } catch (error) {
                addLog('❌ Lỗi decode path: ' + error.message, 'error');
            }
        }
        
        async function indexSingleFile(filePath) {
            try {
                addLog('🔄 Đang index file: ' + filePath.split(/[\\/]/).pop(), 'info');
                const response = await fetch('/api/knowledge/index_file', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ file_path: filePath })
                });
                const data = await response.json();
                
                if (data.success) {
                    addLog('✅ ' + data.message, 'success');
                    loadKnowledgeBase();
                } else {
                    addLog('❌ ' + (data.error || 'Lỗi không xác định'), 'error');
                }
            } catch (error) {
                addLog('❌ Lỗi: ' + error.message, 'error');
            }
        }
        
        async function clearKnowledgeBase() {
            if (!confirm('Bạn có chắc muốn xóa toàn bộ index? Dữ liệu gốc không bị ảnh hưởng.')) {
                return;
            }
            
            try {
                addLog('🗑️ Đang xóa index...', 'info');
                const response = await fetch('/api/knowledge/clear', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                const data = await response.json();
                
                if (data.success) {
                    addLog('✅ ' + data.message, 'success');
                    document.getElementById('kb-indexed-files').textContent = '0';
                    loadKnowledgeBase();
                } else {
                    addLog('❌ ' + (data.error || 'Lỗi không xác định'), 'error');
                }
            } catch (error) {
                addLog('❌ Lỗi: ' + error.message, 'error');
            }
        }
        
        // ============================================================
        // CONVERSATION HISTORY FUNCTIONS (WeChat Style)
        // ============================================================
        
        async function loadConversationHistory() {
            try {
                addLog('📚 Đang tải lịch sử hội thoại...', 'info');
                const response = await fetch('/api/conversation/history');
                const data = await response.json();
                
                if (data.success) {
                    displayConversationHistory(data.messages);
                    document.getElementById('total-messages').textContent = data.total_messages;
                    
                    if (data.messages && data.messages.length > 0) {
                        const lastMsg = data.messages[data.messages.length - 1];
                        document.getElementById('last-update').textContent = 'Cập nhật: ' + lastMsg.timestamp;
                    }
                    
                    addLog('✅ Đã tải ' + data.total_messages + ' tin nhắn', 'success');
                } else {
                    addLog('❌ Lỗi tải lịch sử: ' + (data.error || 'Unknown'), 'error');
                }
            } catch (e) {
                console.error('Failed to load conversation history', e);
                addLog('❌ Không thể kết nối đến server', 'error');
            }
        }
        
        function displayConversationHistory(messages) {
            const container = document.getElementById('chat-container');
            container.innerHTML = '';
            
            if (messages.length === 0) {
                container.innerHTML = '<div style="text-align:center; color:#999; padding:40px; font-size:1.1em;">Chưa có tin nhắn nào 💬</div>';
                return;
            }
            
            messages.forEach(msg => {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'chat-message ' + msg.role;
                
                // Avatar
                const avatar = document.createElement('div');
                avatar.className = 'chat-avatar ' + msg.role;
                const roleIcons = {
                    user: '👤',
                    assistant: '🤖',
                    system: '⚙️',
                    tool: '🔧'
                };
                avatar.textContent = roleIcons[msg.role] || '💬';
                
                // Bubble
                const bubble = document.createElement('div');
                bubble.className = 'chat-bubble';
                
                // Content
                const content = document.createElement('div');
                content.className = 'chat-content';
                content.textContent = msg.content;
                bubble.appendChild(content);
                
                // Metadata
                if (msg.metadata && Object.keys(msg.metadata).length > 0) {
                    const metadata = document.createElement('div');
                    metadata.className = 'chat-metadata';
                    
                    // Show relevant metadata
                    if (msg.metadata.source) {
                        const sourceTag = document.createElement('span');
                        sourceTag.className = 'chat-metadata-item';
                        const sourceIcons = {
                            mcp: '🔌 MCP',
                            web_ui: '🌐 Web UI',
                            websocket: '📡 WebSocket'
                        };
                        sourceTag.textContent = sourceIcons[msg.metadata.source] || msg.metadata.source;
                        metadata.appendChild(sourceTag);
                    }
                    
                    if (msg.metadata.method) {
                        const methodTag = document.createElement('span');
                        methodTag.className = 'chat-metadata-item';
                        methodTag.textContent = '📋 ' + msg.metadata.method;
                        metadata.appendChild(methodTag);
                    }
                    
                    if (msg.metadata.model) {
                        const modelTag = document.createElement('span');
                        modelTag.className = 'chat-metadata-item';
                        modelTag.textContent = '🧠 ' + msg.metadata.model;
                        metadata.appendChild(modelTag);
                    }
                    
                    if (msg.metadata.success !== undefined) {
                        const statusTag = document.createElement('span');
                        statusTag.className = 'chat-metadata-item';
                        statusTag.textContent = msg.metadata.success ? '✅ Success' : '❌ Failed';
                        metadata.appendChild(statusTag);
                    }
                    
                    bubble.appendChild(metadata);
                }
                
                // Timestamp
                const timestamp = document.createElement('div');
                timestamp.className = 'chat-timestamp';
                timestamp.textContent = msg.timestamp;
                bubble.appendChild(timestamp);
                
                messageDiv.appendChild(avatar);
                messageDiv.appendChild(bubble);
                container.appendChild(messageDiv);
            });
            
            // Auto scroll to bottom
            container.scrollTop = container.scrollHeight;
        }
        
        async function exportConversation() {
            try {
                addLog('💾 Đang xuất lịch sử...', 'info');
                const response = await fetch('/api/conversation/export', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({})
                });
                const data = await response.json();
                
                if (data.success) {
                    addLog('✅ Đã xuất file: ' + data.path, 'success');
                    alert('✅ Đã xuất lịch sử hội thoại!\\n\\nĐường dẫn: ' + data.path + '\\n\\nTổng: ' + data.message);
                } else {
                    addLog('❌ Lỗi xuất file: ' + (data.error || 'Unknown'), 'error');
                }
            } catch (e) {
                console.error('Failed to export conversation', e);
                addLog('❌ Không thể xuất file', 'error');
            }
        }
        
        async function clearConversationHistory() {
            if (!confirm('⚠️ Bạn có chắc muốn XÓA TẤT CẢ lịch sử hội thoại?\\n\\nHành động này KHÔNG THỂ HOÀN TÁC!')) {
                return;
            }
            
            try {
                addLog('🗑️ Đang xóa lịch sử...', 'info');
                const response = await fetch('/api/conversation/clear', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('chat-container').innerHTML = '<div style="text-align:center; color:#999; padding:40px; font-size:1.1em;">Chưa có tin nhắn nào 💬</div>';
                    document.getElementById('total-messages').textContent = '0';
                    document.getElementById('last-update').textContent = 'Chưa có dữ liệu';
                    addLog('✅ Đã xóa toàn bộ lịch sử', 'success');
                } else {
                    addLog('❌ Lỗi xóa lịch sử: ' + (data.error || 'Unknown'), 'error');
                }
            } catch (e) {
                console.error('Failed to clear conversation', e);
                addLog('❌ Không thể xóa lịch sử', 'error');
            }
        }
        
        // ===== MUSIC PLAYER FUNCTIONS =====
        let currentPlaylist = [];
        let allMusicFiles = []; // Store all files for filtering
        let currentTrackIndex = -1;
        let isPlaying = false;
        let isShuffleOn = false;
        let repeatMode = 0; // 0: off, 1: repeat all, 2: repeat one
        let currentMusicSource = 'library'; // 'library' or 'user'
        let vlcStatusInterval = null; // VLC status polling interval
        
        // ===== VLC STATUS POLLING - Real-time sync with python-vlc =====
        async function pollVlcStatus() {
            try {
                const response = await fetch('/api/vlc_status');
                const status = await response.json();
                
                if (status.state && status.state !== 'not_initialized') {
                    // Update play state
                    isPlaying = status.is_playing;
                    document.getElementById('play-btn').textContent = isPlaying ? '⏸️' : '▶️';
                    
                    // Update progress slider (only if not dragging)
                    if (status.position !== undefined && !isDraggingProgress) {
                        const percent = (status.position * 100).toFixed(1);
                        const slider = document.getElementById('progress-slider');
                        if (slider) {
                            slider.value = percent;
                            slider.style.background = `linear-gradient(to right, #667eea 0%, #667eea ${percent}%, #374151 ${percent}%, #374151 100%)`;
                        }
                    }
                    
                    // Update time display
                    if (status.current_time_formatted) {
                        document.getElementById('current-time').textContent = status.current_time_formatted;
                    }
                    if (status.duration_formatted) {
                        document.getElementById('total-time').textContent = status.duration_formatted;
                    }
                    
                    // Update volume (sync from VLC)
                    if (status.volume !== undefined) {
                        const slider = document.getElementById('volume-slider');
                        if (document.activeElement !== slider) { // Don't update while user is dragging
                            slider.value = status.volume;
                            document.getElementById('volume-value').textContent = status.volume + '%';
                            slider.style.background = `linear-gradient(to right, #667eea 0%, #667eea ${status.volume}%, #374151 ${status.volume}%, #374151 100%)`;
                        }
                    }
                    
                    // Update current track name
                    if (status.current_track) {
                        document.getElementById('current-track').textContent = '🎵 ' + status.current_track;
                        document.getElementById('track-info').textContent = 
                            `${status.playlist_index + 1}/${status.playlist_count} bài • VLC Player`;
                    }
                    
                    // Sync shuffle/repeat state from VLC
                    if (status.shuffle !== undefined) {
                        isShuffleOn = status.shuffle;
                        const shuffleBtn = document.getElementById('shuffle-btn');
                        if (shuffleBtn) {
                            shuffleBtn.style.opacity = isShuffleOn ? '1' : '0.6';
                            shuffleBtn.style.transform = isShuffleOn ? 'scale(1.1)' : 'scale(1)';
                        }
                    }
                    if (status.repeat_mode !== undefined) {
                        repeatMode = status.repeat_mode;
                        const repeatBtn = document.getElementById('repeat-btn');
                        if (repeatBtn) {
                            repeatBtn.textContent = repeatMode === 2 ? '🔂' : '🔁';
                            repeatBtn.style.opacity = repeatMode > 0 ? '1' : '0.6';
                        }
                    }
                }
            } catch (e) {
                // Silent fail - VLC may not be playing
            }
        }
        
        function startVlcPolling() {
            if (vlcStatusInterval) clearInterval(vlcStatusInterval);
            vlcStatusInterval = setInterval(pollVlcStatus, 1000); // Poll every 1 second
        }
        
        function stopVlcPolling() {
            if (vlcStatusInterval) {
                clearInterval(vlcStatusInterval);
                vlcStatusInterval = null;
            }
        }
        
        // Click on progress bar to seek
        async function seekToPosition(event) {
            const progressBar = event.currentTarget;
            const rect = progressBar.getBoundingClientRect();
            const position = (event.clientX - rect.left) / rect.width;
            
            try {
                await fetch('/api/vlc_seek', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({position: position})
                });
            } catch (e) {
                console.error('Seek failed', e);
            }
        }
        
        // Music Source Selector Functions
        function setMusicSource(source) {
            currentMusicSource = source;
            localStorage.setItem('musicSource', source);
            
            // Update button styles
            const libraryBtn = document.getElementById('source-library-btn');
            const userBtn = document.getElementById('source-user-btn');
            
            if (source === 'library') {
                libraryBtn.style.background = '#667eea';
                libraryBtn.style.color = 'white';
                userBtn.style.background = 'transparent';
                userBtn.style.color = '#667eea';
                document.getElementById('source-path-display').textContent = 'music_library/';
            } else {
                libraryBtn.style.background = 'transparent';
                libraryBtn.style.color = '#667eea';
                userBtn.style.background = '#667eea';
                userBtn.style.color = 'white';
                const userPath = localStorage.getItem('musicFolderPath') || 'Chưa cấu hình';
                document.getElementById('source-path-display').textContent = userPath;
            }
            
            // Reload music library from new source
            loadMusicLibrary();
            addLog(`🎯 Đã chuyển nguồn phát: ${source === 'library' ? 'Music Library' : 'Thư mục cá nhân'}`, 'success');
        }
        
        function loadMusicSourcePreference() {
            const saved = localStorage.getItem('musicSource') || 'library';
            setMusicSource(saved);
        }
        
        // Search/Filter Music Library
        function filterMusicLibrary(query) {
            if (!query || query.trim() === '') {
                renderMusicLibrary(allMusicFiles);
                return;
            }
            
            const lowerQuery = query.toLowerCase();
            const filtered = allMusicFiles.filter(file => 
                file.filename.toLowerCase().includes(lowerQuery) ||
                (file.path && file.path.toLowerCase().includes(lowerQuery))
            );
            renderMusicLibrary(filtered);
        }
        
        async function loadMusicLibrary() {
            try {
                // Determine which source to load from
                // IMPORTANT: auto_play=false để không tự phát khi load danh sách
                const args = currentMusicSource === 'user' 
                    ? { folder: localStorage.getItem('musicFolderPath') || '', auto_play: false }
                    : { auto_play: false };
                
                const response = await fetch('/api/call_tool', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({tool: 'list_music', args: args})
                });
                const data = await response.json();
                
                if (data.success && data.files) {
                    allMusicFiles = data.files;
                    currentPlaylist = data.files;
                    renderMusicLibrary(data.files);
                } else {
                    document.getElementById('music-library').innerHTML = '<p style="text-align:center; color:#999; padding:40px;">❌ Không tìm thấy nhạc trong thư viện</p>';
                }
            } catch (e) {
                console.error('Failed to load music library', e);
                document.getElementById('music-library').innerHTML = '<p style="text-align:center; color:#f44336; padding:40px;">❌ Lỗi tải danh sách nhạc</p>';
            }
        }
        
        function renderMusicLibrary(files) {
            const html = files.map((file, index) => {
                const originalIndex = allMusicFiles.findIndex(f => f.filename === file.filename);
                return `
                <div class="music-item ${originalIndex === currentTrackIndex && isPlaying ? 'playing' : ''}" 
                     onclick="selectTrack(${originalIndex})" 
                     ondblclick="playTrackNow(${originalIndex})" 
                     style="cursor:pointer; display: flex; align-items: center; padding: 12px; border-radius: 8px; margin-bottom: 8px; background: ${originalIndex === currentTrackIndex ? 'linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%)' : '#f9fafb'}; transition: all 0.2s; border-left: 3px solid ${originalIndex === currentTrackIndex ? '#667eea' : 'transparent'};">
                    <div class="icon" style="font-size: 1.5em; margin-right: 12px;">${originalIndex === currentTrackIndex && isPlaying ? '🔊' : '🎵'}</div>
                    <div class="info" style="flex: 1;">
                        <div class="name" style="font-weight: 600; color: #333; margin-bottom: 3px;">${file.filename}</div>
                        <div class="details" style="font-size: 0.85em; color: #6b7280;">${file.path} • ${file.size_mb} MB</div>
                    </div>
                    ${originalIndex === currentTrackIndex && isPlaying ? '<span style="color:#667eea; font-size:20px; animation: pulse 1s infinite;">▶️</span>' : ''}
                </div>
            `}).join('');
            
            document.getElementById('music-library').innerHTML = html || '<p style="text-align:center; color:#999; padding:40px;">Không có bài hát nào</p>';
        }
        
        // Toggle Shuffle
        async function toggleShuffle() {
            try {
                const response = await fetch('/api/vlc_shuffle', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({})
                });
                const data = await response.json();
                
                if (data.success) {
                    isShuffleOn = data.shuffle;
                    const btn = document.getElementById('shuffle-btn');
                    btn.style.opacity = isShuffleOn ? '1' : '0.6';
                    btn.style.transform = isShuffleOn ? 'scale(1.1)' : 'scale(1)';
                    addLog(isShuffleOn ? '🔀 Bật phát ngẫu nhiên' : '🔀 Tắt phát ngẫu nhiên', 'success');
                }
            } catch (e) {
                console.error('Toggle shuffle failed', e);
            }
        }
        
        // Toggle Repeat
        async function toggleRepeat() {
            try {
                const response = await fetch('/api/vlc_repeat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({})
                });
                const data = await response.json();
                
                if (data.success) {
                    repeatMode = data.repeat_mode;
                    const btn = document.getElementById('repeat-btn');
                    
                    switch(repeatMode) {
                        case 0:
                            btn.textContent = '🔁';
                            btn.style.opacity = '0.6';
                            addLog('🔁 Tắt lặp lại', 'success');
                            break;
                        case 1:
                            btn.textContent = '🔁';
                            btn.style.opacity = '1';
                            addLog('🔁 Lặp lại tất cả', 'success');
                            break;
                        case 2:
                            btn.textContent = '🔂';
                            btn.style.opacity = '1';
                            addLog('🔂 Lặp lại một bài', 'success');
                            break;
                    }
                }
            } catch (e) {
                console.error('Toggle repeat failed', e);
            }
        }
        
        // Volume Control
        function setPlayerVolume(value) {
            document.getElementById('volume-value').textContent = value + '%';
            
            // Update slider gradient
            const slider = document.getElementById('volume-slider');
            slider.style.background = `linear-gradient(to right, #667eea 0%, #667eea ${value}%, #374151 ${value}%, #374151 100%)`;
            
            // Update icon
            const icon = document.getElementById('volume-icon');
            if (value == 0) {
                icon.textContent = '🔇';
            } else if (value < 30) {
                icon.textContent = '🔈';
            } else if (value < 70) {
                icon.textContent = '🔉';
            } else {
                icon.textContent = '🔊';
            }
            
            // Call VLC API directly to set volume
            fetch('/api/vlc_volume', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({level: parseInt(value)})
            }).catch(e => console.error('Volume set failed', e));
        }
        
        let lastVolume = 80;
        function toggleMute() {
            const slider = document.getElementById('volume-slider');
            if (parseInt(slider.value) > 0) {
                lastVolume = slider.value;
                slider.value = 0;
                setPlayerVolume(0);
            } else {
                slider.value = lastVolume;
                setPlayerVolume(lastVolume);
            }
        }
        
        // Chọn bài (click đơn) - chỉ highlight, delay để không chặn double-click
        let selectedTrackIndex = -1;
        let clickTimer = null;
        
        function selectTrack(index) {
            // Clear timer nếu có (tránh xung đột với double-click)
            if (clickTimer) {
                clearTimeout(clickTimer);
                clickTimer = null;
                return; // Đây là double-click, bỏ qua
            }
            
            // Delay 200ms để chờ xem có double-click không
            clickTimer = setTimeout(() => {
                selectedTrackIndex = index;
                // Highlight bài được chọn
                document.querySelectorAll('.music-item').forEach((item, i) => {
                    const itemIndex = parseInt(item.getAttribute('data-index') || i);
                    if (itemIndex === index) {
                        item.style.borderColor = '#667eea';
                        item.style.background = 'linear-gradient(135deg, rgba(102,126,234,0.15) 0%, rgba(118,75,162,0.15) 100%)';
                    }
                });
                clickTimer = null;
            }, 200);
        }
        
        // Double-click để phát ngay
        async function playTrackNow(index) {
            // Clear single-click timer
            if (clickTimer) {
                clearTimeout(clickTimer);
                clickTimer = null;
            }
            // Phát nhạc ngay
            await playTrack(index);
        }
        
        // Cập nhật visualizer state
        function updateVisualizer(playing) {
            const visualizer = document.getElementById('audio-visualizer');
            if (visualizer) {
                if (playing) {
                    visualizer.style.display = 'flex';
                    visualizer.classList.remove('paused');
                } else {
                    visualizer.classList.add('paused');
                }
            }
        }
        
        async function playTrack(index) {
            if (!allMusicFiles[index]) {
                console.error('Track not found at index:', index);
                addLog('❌ Không tìm thấy bài hát', 'error');
                return;
            }
            
            try {
                const track = allMusicFiles[index];
                console.log('🎵 Playing track:', track.filename);
                addLog(`⏳ Đang tải: ${track.filename}...`, 'info');
                
                // Gọi API trực tiếp để phát nhạc
                const response = await fetch('/api/vlc_play_file', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({filename: track.filename})
                });
                const data = await response.json();
                console.log('Play response:', data);
                
                if (data.success) {
                    currentTrackIndex = index;
                    isPlaying = true;
                    updateNowPlaying();
                    updateVisualizer(true);
                    renderMusicLibrary(currentPlaylist);
                    document.getElementById('play-btn').textContent = '⏸️';
                    addLog(`🎵 Đang phát: ${track.filename}`, 'success');
                    
                    // Start VLC polling for real-time sync
                    startVlcPolling();
                } else {
                    console.error('Play failed:', data);
                    addLog('❌ ' + (data.error || 'Không thể phát nhạc'), 'error');
                }
            } catch (e) {
                console.error('Failed to play track', e);
                addLog('❌ Lỗi kết nối', 'error');
            }
        }
        
        async function musicPlayPause() {
            try {
                // Gọi VLC API trực tiếp - không qua tool registry
                const response = await fetch('/api/vlc_play_pause', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                const data = await response.json();
                
                if (data.success) {
                    isPlaying = data.is_playing;
                    document.getElementById('play-btn').textContent = isPlaying ? '⏸️' : '▶️';
                    updateVisualizer(isPlaying);
                    renderMusicLibrary(currentPlaylist);
                    addLog(data.message, 'success');
                } else {
                    addLog('❌ ' + (data.error || 'Lỗi play/pause'), 'error');
                }
            } catch (e) {
                console.error('Play/Pause failed', e);
                addLog('❌ Lỗi kết nối VLC', 'error');
            }
        }
        
        async function musicNext() {
            try {
                const response = await fetch('/api/vlc_next', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                const data = await response.json();
                
                if (data.success) {
                    currentTrackIndex = (currentTrackIndex + 1) % currentPlaylist.length;
                    updateNowPlaying();
                    renderMusicLibrary(currentPlaylist);
                    addLog(data.message || '⏭️ Bài tiếp theo', 'success');
                } else {
                    addLog('❌ ' + (data.error || 'Không có bài tiếp'), 'error');
                }
            } catch (e) {
                console.error('Next track failed', e);
                addLog('❌ Lỗi chuyển bài', 'error');
            }
        }
        
        async function musicPrevious() {
            try {
                const response = await fetch('/api/vlc_previous', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                const data = await response.json();
                
                if (data.success) {
                    currentTrackIndex = (currentTrackIndex - 1 + currentPlaylist.length) % currentPlaylist.length;
                    updateNowPlaying();
                    renderMusicLibrary(currentPlaylist);
                    addLog(data.message || '⏮️ Bài trước', 'success');
                } else {
                    addLog('❌ ' + (data.error || 'Không có bài trước'), 'error');
                }
            } catch (e) {
                console.error('Previous track failed', e);
                addLog('❌ Lỗi chuyển bài', 'error');
            }
        }
        
        async function musicStop() {
            try {
                const response = await fetch('/api/vlc_stop', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                const data = await response.json();
                
                if (data.success) {
                    isPlaying = false;
                    currentTrackIndex = -1;
                    document.getElementById('current-track').textContent = '🎵 Đã dừng phát';
                    document.getElementById('track-info').textContent = 'Chọn bài hát để phát';
                    document.getElementById('track-album').textContent = '';
                    document.getElementById('album-art').innerHTML = '🎵';
                    document.getElementById('play-btn').textContent = '▶️';
                    const slider = document.getElementById('progress-slider');
                    if (slider) {
                        slider.value = 0;
                        slider.style.background = 'linear-gradient(to right, #667eea 0%, #667eea 0%, #374151 0%, #374151 100%)';
                    }
                    document.getElementById('current-time').textContent = '0:00';
                    document.getElementById('total-time').textContent = '0:00';
                    addLog(data.message || '⏹️ Đã dừng nhạc', 'success');
                } else {
                    addLog('❌ ' + (data.error || 'Lỗi dừng nhạc'), 'error');
                    renderMusicLibrary(currentPlaylist);
                    addLog('⏹️ Đã dừng phát nhạc', 'success');
                }
            } catch (e) {
                console.error('Stop failed', e);
            }
        }
        
        function updateNowPlaying() {
            if (currentTrackIndex >= 0 && allMusicFiles[currentTrackIndex]) {
                const track = allMusicFiles[currentTrackIndex];
                document.getElementById('current-track').textContent = track.filename.replace(/\\.[^/.]+$/, ''); // Remove extension
                document.getElementById('track-info').textContent = `${track.path}`;
                document.getElementById('track-album').textContent = `${track.size_mb} MB • Bài ${currentTrackIndex + 1}/${allMusicFiles.length}`;
                
                // Update album art with music note animation
                const albumArt = document.getElementById('album-art');
                if (albumArt) {
                    albumArt.innerHTML = isPlaying ? '<div style="animation: spin 3s linear infinite;">🎵</div>' : '🎵';
                }
            }
        }
        
        async function updateMusicStatus() {
            try {
                const response = await fetch('/api/call_tool', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({tool: 'get_music_status', args: {}})
                });
                const data = await response.json();
                
                if (data.success) {
                    // Sync playing state
                    const wasPlaying = isPlaying;
                    isPlaying = data.is_playing === 1 || data.is_playing === true;
                    
                    // Update play button
                    const playBtn = document.getElementById('play-btn');
                    if (playBtn) {
                        playBtn.textContent = isPlaying ? '⏸️' : '▶️';
                    }
                    
                    // Update progress bar and time
                    if (data.current_time !== undefined && data.duration !== undefined) {
                        const currentSec = parseFloat(data.current_time) || 0;
                        const totalSec = parseFloat(data.duration) || 0;
                        
                        if (totalSec > 0) {
                            // Update progress slider (only if not dragging)
                            const percentage = (currentSec / totalSec) * 100;
                            const slider = document.getElementById('progress-slider');
                            if (slider && !isDraggingProgress) {
                                slider.value = Math.min(100, Math.max(0, percentage));
                                slider.style.background = `linear-gradient(to right, #667eea 0%, #667eea ${percentage}%, #374151 ${percentage}%, #374151 100%)`;
                            }
                            
                            // Update time displays
                            const currentTimeEl = document.getElementById('current-time');
                            const totalTimeEl = document.getElementById('total-time');
                            if (currentTimeEl) currentTimeEl.textContent = formatTime(currentSec);
                            if (totalTimeEl) totalTimeEl.textContent = formatTime(totalSec);
                        }
                    }
                    
                    // Update library UI if play state changed
                    if (wasPlaying !== isPlaying && currentPlaylist.length > 0) {
                        renderMusicLibrary(currentPlaylist);
                    }
                }
            } catch (e) {
                console.error('Update music status error:', e);
            }
        }
        
        function formatTime(seconds) {
            if (!seconds || seconds < 0) return '0:00';
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return mins + ':' + (secs < 10 ? '0' : '') + secs;
        }
        
        // Progress bar dragging state
        let isDraggingProgress = false;
        
        // Called while dragging (preview only, no seek)
        function onProgressDrag(value) {
            isDraggingProgress = true;
            // Update slider visual immediately
            const slider = document.getElementById('progress-slider');
            slider.style.background = `linear-gradient(to right, #667eea 0%, #667eea ${value}%, #374151 ${value}%, #374151 100%)`;
        }
        
        // Called when drag ends (actual seek)
        async function onProgressSeek(value) {
            isDraggingProgress = false;
            const percentage = parseFloat(value);
            
            try {
                const response = await fetch('/api/call_tool', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({tool: 'seek_music', args: {percentage: percentage}})
                });
                const data = await response.json();
                
                if (data.success) {
                    await updateMusicStatus();
                }
            } catch (e) {
                console.error('Seek failed', e);
            }
        }
        
        async function seekTrack(event) {
            const progressBar = event.currentTarget;
            const rect = progressBar.getBoundingClientRect();
            const clickX = event.clientX - rect.left;
            const percentage = (clickX / rect.width) * 100;
            
            try {
                // Gọi tool để seek (cần implement trong backend)
                const response = await fetch('/api/call_tool', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({tool: 'seek_music', args: {percentage: percentage}})
                });
                const data = await response.json();
                
                if (data.success) {
                    // Cập nhật progress bar ngay lập tức
                    document.getElementById('progress-fill').style.width = percentage + '%';
                    await updateMusicStatus();
                }
            } catch (e) {
                console.error('Seek failed', e);
            }
        }
        
        connectWS();
        // Giảm polling từ 5s xuống 10s để giảm tải
        setInterval(getResources, 10000);
        getResources();
        
        // Start VLC status polling for real-time sync
        startVlcPolling();
        
        // Initial VLC status check
        setTimeout(pollVlcStatus, 500);
        
        // RunCat Animation - Multiple frames like RunCat365
        let runcatFrame = 0;
        let runcatSpeed = 500; // Default 500ms per frame
        const runcatFrames = ['🐱', '🐈', '😺', '😸', '😹'];
        
        function animateRunCat() {
            const runcat = document.getElementById('runcat');
            if (!runcat) return;
            
            runcatFrame = (runcatFrame + 1) % runcatFrames.length;
            runcat.textContent = runcatFrames[runcatFrame];
            
            // Apply transform for running effect
            const offset = runcatFrame % 2 === 0 ? -3 : -1;
            const flip = runcatFrame >= 2 && runcatFrame <= 3 ? -1 : 1;
            runcat.style.transform = `translateY(${offset}px) scaleX(${flip})`;
            
            setTimeout(animateRunCat, runcatSpeed);
        }
        
        // Start RunCat animation
        setTimeout(animateRunCat, 100);
        
        // Auto-update music status every 1 second when music section is active
        setInterval(() => {
            const musicSection = document.getElementById('music-section');
            if (musicSection && musicSection.style.display !== 'none') {
                updateMusicStatus();
            }
        }, 1000);
        
        // Music Settings Functions
        function loadMusicFolderSettings() {
            const savedPath = localStorage.getItem('musicFolderPath');
            if (savedPath) {
                document.getElementById('music-folder-path').value = savedPath;
            }
        }
        
        function browseMusicFolder() {
            // Web không thể browse folder trực tiếp, hướng dẫn user
            alert('💡 Hướng dẫn:\\n\\n1. Mở File Explorer (Windows + E)\\n2. Đi đến thư mục nhạc của bạn\\n3. Click vào thanh địa chỉ và copy đường dẫn (Ctrl+C)\\n4. Paste vào ô bên trái (Ctrl+V)\\n5. Click "💾 Lưu"\\n\\nVí dụ: C:\\\\\\\\Users\\\\\\\\YourName\\\\\\\\Music');
        }
        
        async function saveMusicFolder() {
            const folderPath = document.getElementById('music-folder-path').value.trim();
            const statusEl = document.getElementById('music-folder-status');
            
            if (!folderPath) {
                statusEl.style.display = 'block';
                statusEl.style.background = '#fee2e2';
                statusEl.style.color = '#991b1b';
                statusEl.innerHTML = '❌ Vui lòng nhập đường dẫn thư mục!';
                return;
            }
            
            try {
                // Lưu vào localStorage
                localStorage.setItem('musicFolderPath', folderPath);
                
                // Gọi tool để lưu config
                const response = await fetch('/api/call_tool', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        tool: 'save_music_folder_config',
                        args: {folder_path: folderPath}
                    })
                });
                const data = await response.json();
                
                if (data.success) {
                    statusEl.style.display = 'block';
                    statusEl.style.background = '#d1fae5';
                    statusEl.style.color = '#065f46';
                    statusEl.innerHTML = '✅ Đã lưu cài đặt thành công! LLM sẽ ưu tiên phát nhạc từ thư mục này.';
                    addLog(`⚙️ Đã cấu hình thư mục nhạc: ${folderPath}`, 'success');
                } else {
                    throw new Error(data.error || 'Unknown error');
                }
            } catch (e) {
                statusEl.style.display = 'block';
                statusEl.style.background = '#fee2e2';
                statusEl.style.color = '#991b1b';
                statusEl.innerHTML = `❌ Lỗi: ${e.message}`;
                console.error('Save music folder error:', e);
            }
        }
        
        // Load music folder settings when opening the section
        document.addEventListener('DOMContentLoaded', () => {
            loadMusicFolderSettings();
        });
        
    // Initialize playlists on page load
    initPlaylists();
    </script>
    
    <!-- MINIZ FOOTER - Compact Corner -->
    <div class="footer-miniz">
        <div class="footer-logo-compact">
            <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='48' fill='%23667eea'/%3E%3Cpath d='M30 40 L50 25 L70 40 M50 25 L50 75 M35 55 L50 50 L65 55 M35 70 L50 65 L65 70' stroke='white' stroke-width='3' fill='none'/%3E%3Ctext x='50' y='88' text-anchor='middle' fill='white' font-size='14' font-weight='bold' font-family='Arial'%3EminiZ%3C/text%3E%3C/svg%3E" alt="miniZ Logo">
            <span class="footer-brand-compact">miniZ</span>
        </div>
        <div class="footer-separator"></div>
        <a href="https://youtube.com/@minizjp?si=LRg5piGHmxYtsFJU" target="_blank" class="footer-youtube-compact" title="Kênh YouTube miniZ">
            <svg viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
            YouTube
        </a>
    </div>
</body>
</html>
    """
    return html

# API Endpoints
@app.post("/api/volume")
async def api_volume(request: VolumeRequest):
    result = await set_volume(request.level)
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/screenshot")
async def api_screenshot():
    result = await take_screenshot()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/notification")
async def api_notification(request: NotificationRequest):
    result = await show_notification(request.title, request.message)
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.get("/api/resources")
async def api_resources():
    result = await get_system_resources()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.get("/api/vlc_status")
async def api_vlc_status():
    """VLC Player status endpoint for Web UI real-time sync"""
    try:
        status = vlc_player.get_full_status()
        return status
    except Exception as e:
        return {"success": False, "error": str(e), "state": "error"}

@app.post("/api/vlc_seek")
async def api_vlc_seek(data: dict):
    """Seek VLC player to specific position (0.0 - 1.0)"""
    try:
        position = float(data.get("position", 0))
        vlc_player.set_position(position)
        return {"success": True, "position": position}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/vlc_volume")
async def api_vlc_volume(data: dict):
    """Set VLC player volume (0-100)"""
    try:
        level = int(data.get("level", 80))
        vlc_player.set_volume(level)
        return {"success": True, "volume": level}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/vlc_shuffle")
async def api_vlc_shuffle(data: dict):
    """Toggle or set shuffle mode"""
    try:
        enabled = data.get("enabled")
        if enabled is None:
            # Toggle
            enabled = not vlc_player.get_shuffle()
        vlc_player.set_shuffle(enabled)
        return {"success": True, "shuffle": enabled}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/vlc_repeat")
async def api_vlc_repeat(data: dict):
    """Set repeat mode: 0=off, 1=all, 2=one"""
    try:
        mode = data.get("mode")
        if mode is None:
            # Cycle through modes
            current = vlc_player.get_repeat_mode()
            mode = (current + 1) % 3
        vlc_player.set_repeat_mode(mode)
        return {"success": True, "repeat_mode": mode}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/vlc_play_file")
async def api_vlc_play_file(data: dict):
    """Phát file nhạc trực tiếp qua VLC - cho Web UI double-click"""
    try:
        filename = data.get("filename", "")
        if not filename:
            return {"success": False, "error": "Thiếu filename"}
        
        print(f"🎵 [API] vlc_play_file: {filename}")
        
        # Gọi hàm play_music
        result = await play_music(filename=filename, create_playlist=True)
        print(f"🎵 [API] play_music result: {result}")
        return result
    except Exception as e:
        print(f"❌ [API] vlc_play_file error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/vlc_play_pause")
async def api_vlc_play_pause():
    """Toggle VLC play/pause"""
    try:
        if vlc_player and vlc_player._player:
            vlc_player.pause()
            is_playing = vlc_player.is_playing()
            return {"success": True, "is_playing": is_playing, "message": "▶️ Đang phát" if is_playing else "⏸️ Đã tạm dừng"}
        return {"success": False, "error": "VLC chưa khởi tạo hoặc chưa phát nhạc"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/vlc_stop")
async def api_vlc_stop():
    """Stop VLC player"""
    try:
        if vlc_player and vlc_player._player:
            vlc_player.stop()
            return {"success": True, "message": "⏹️ Đã dừng nhạc"}
        return {"success": False, "error": "VLC chưa khởi tạo hoặc chưa phát nhạc"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/vlc_next")
async def api_vlc_next():
    """Next track in VLC - Tự động phát bài tiếp theo"""
    try:
        if vlc_player and vlc_player._list_player:
            # Chuyển bài tiếp theo
            vlc_player._list_player.next()
            import time
            time.sleep(0.5)  # Đợi VLC xử lý
            # LUÔN gọi play() để đảm bảo phát
            vlc_player._list_player.play()
            time.sleep(0.2)
            status = vlc_player.get_full_status()
            print(f"⏭️ [API] Next → {status.get('current_song', 'Unknown')}")
            return {
                "success": True, 
                "message": f"⏭️ Bài tiếp: {status.get('current_song', 'Unknown')}",
                "current_song": status.get('current_song'),
                "is_playing": True
            }
        return {"success": False, "error": "VLC chưa khởi tạo hoặc chưa có playlist"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/vlc_previous")
async def api_vlc_previous():
    """Previous track in VLC - Tự động phát bài trước"""
    try:
        if vlc_player and vlc_player._list_player:
            # Chuyển bài trước
            vlc_player._list_player.previous()
            import time
            time.sleep(0.5)  # Đợi VLC xử lý
            # LUÔN gọi play() để đảm bảo phát
            vlc_player._list_player.play()
            time.sleep(0.2)
            status = vlc_player.get_full_status()
            print(f"⏮️ [API] Previous → {status.get('current_song', 'Unknown')}")
            return {
                "success": True, 
                "message": f"⏮️ Bài trước: {status.get('current_song', 'Unknown')}",
                "current_song": status.get('current_song'),
                "is_playing": True
            }
        return {"success": False, "error": "VLC chưa khởi tạo hoặc chưa có playlist"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/time")
async def api_time():
    result = await get_current_time()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return {"data": result}

@app.post("/api/calculator")
async def api_calculator(request: CalculatorRequest):
    result = await calculator(request.expression)
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result


# ===== GENERIC TOOL CALLER =====

@app.post("/api/call_tool")
async def call_any_tool(data: dict):
    """Generic endpoint to call ANY tool from TOOLS registry"""
    tool_name = data.get("tool", data.get("name", ""))
    args = data.get("args", data.get("arguments", {}))
    
    if not tool_name:
        raise HTTPException(400, "Tool name is required")
    
    if tool_name not in TOOLS:
        raise HTTPException(404, f"Tool '{tool_name}' not found")
    
    try:
        handler = TOOLS[tool_name]["handler"]
        result = await handler(**args)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================
# 🧠 INTENT DETECTION API ENDPOINTS
# ============================================================

@app.post("/api/detect_intent")
async def api_detect_intent(data: dict):
    """
    Phân tích intent từ text input
    Trả về suggested tool và confidence
    """
    text = data.get("text", data.get("query", ""))
    use_llm = data.get("use_llm", False)
    
    if not text:
        raise HTTPException(400, "Text is required")
    
    try:
        if use_llm:
            result = await intent_detector.detect_with_llm(text, GEMINI_API_KEY)
        else:
            result = intent_detector.detect_intent(text)
        
        return {
            "success": True,
            "text": text,
            **result
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/smart_chat")
async def api_smart_chat(data: dict):
    """
    Smart Chat với Intent Detection tự động
    1. Phân tích intent
    2. Nếu cần tool → tự động gọi tool trước
    3. Gửi kết quả tool + query đến Gemini
    4. Trả về response hoàn chỉnh
    """
    query = data.get("query", data.get("prompt", data.get("text", "")))
    use_llm_intent = data.get("use_llm_intent", False)
    model = data.get("model", "gemini-2.0-flash-exp")
    
    if not query:
        raise HTTPException(400, "Query is required")
    
    try:
        # Step 1: Detect intent
        if use_llm_intent:
            intent_result = await intent_detector.detect_with_llm(query, GEMINI_API_KEY)
        else:
            intent_result = intent_detector.detect_intent(query)
        
        print(f"🧠 [Intent] {intent_result}")
        
        tool_result = None
        tool_used = None
        
        # Step 2: Nếu cần force tool, gọi tool trước
        if intent_result.get("should_force_tool") and intent_result.get("suggested_tool"):
            tool_name = intent_result["suggested_tool"]
            
            if tool_name in TOOLS and TOOLS[tool_name]["handler"]:
                print(f"🔧 [Auto Tool] Calling {tool_name} for query: {query}")
                
                try:
                    # Tạo arguments dựa trên intent
                    tool_args = {"query": query}
                    
                    # Gọi tool
                    handler = TOOLS[tool_name]["handler"]
                    tool_result = await handler(**tool_args)
                    tool_used = tool_name
                    
                    print(f"✅ [Auto Tool] {tool_name} result: {str(tool_result)[:200]}...")
                except Exception as e:
                    print(f"⚠️ [Auto Tool] Error calling {tool_name}: {e}")
                    tool_result = {"error": str(e)}
        
        # Step 3: Gửi đến Gemini với context từ tool
        final_prompt = query
        if tool_result and not tool_result.get("error"):
            # Thêm context từ tool result
            context = json.dumps(tool_result, ensure_ascii=False, indent=2)
            final_prompt = f"""Dựa trên thông tin tra cứu sau đây, hãy trả lời câu hỏi của user.

📊 THÔNG TIN TRA CỨU (từ {tool_used}):
{context}

❓ CÂU HỎI CỦA USER:
{query}

📝 YÊU CẦU:
- Trả lời ngắn gọn, chính xác
- Dựa trên thông tin tra cứu ở trên
- Nếu thông tin không đủ, nói rõ và đưa ra những gì có"""
        
        # Gọi Gemini
        gemini_result = await ask_gemini(prompt=final_prompt, model=model)
        
        # Lưu vào conversation history
        add_to_conversation(
            role="user",
            content=query,
            metadata={
                "source": "smart_chat",
                "intent": intent_result.get("intent"),
                "tool_suggested": intent_result.get("suggested_tool")
            }
        )
        
        if gemini_result.get("success"):
            add_to_conversation(
                role="assistant",
                content=gemini_result.get("response", ""),
                metadata={
                    "source": "smart_chat",
                    "tool_used": tool_used,
                    "model": model
                }
            )
        
        return {
            "success": True,
            "query": query,
            "intent": intent_result,
            "tool_used": tool_used,
            "tool_result": tool_result,
            "response": gemini_result.get("response", ""),
            "model": model
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

# ===== 23 API ENDPOINTS MỚI (Tool 8-30) =====

@app.post("/api/tool/ask_gemini")
async def api_ask_gemini(data: dict):
    """Gemini AI endpoint - MOVED TO TOP FOR PRIORITY"""
    prompt = data.get("prompt", "")
    model = data.get("model", "models/gemini-2.5-pro")
    
    if not prompt:
        raise HTTPException(400, "Prompt is required")
    
    # Lưu user message vào history
    add_to_conversation(
        role="user",
        content=prompt,
        metadata={
            "source": "web_ui",
            "model_requested": model,
            "ai_provider": "gemini"
        }
    )
    
    result = await ask_gemini(prompt=prompt, model=model)
    
    # Lưu AI response vào history
    if result.get("success"):
        add_to_conversation(
            role="assistant",
            content=result.get("response", ""),
            metadata={
                "source": "web_ui",
                "model": model,
                "ai_provider": "gemini",
                "token_count": result.get("token_count", 0) if "token_count" in result else None
            }
        )
    
    return result

@app.post("/api/tool/open_application")
async def api_open_app(data: dict):
    result = await open_application(data.get("app_name", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

# MEDIA PLAYER CONTROL ENDPOINTS
@app.post("/api/tool/media_play_pause")
async def api_media_play_pause(data: dict):
    result = await media_play_pause()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/media_next_track")
async def api_media_next(data: dict):
    result = await media_next_track()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/media_previous_track")
async def api_media_previous(data: dict):
    result = await media_previous_track()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/media_stop")
async def api_media_stop(data: dict):
    result = await media_stop()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/media_control")
async def api_media_control(data: dict):
    result = await media_control(data.get("action", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/get_active_media_players")
async def api_get_active_media(data: dict):
    result = await get_active_media_players()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/list_running_processes")
async def api_list_procs(data: dict):
    result = await list_running_processes(data.get("limit", 10))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/kill_process")
async def api_kill_proc(data: dict):
    result = await kill_process(data.get("identifier", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/create_file")
async def api_create_file(data: dict):
    result = await create_file(data.get("path", ""), data.get("content", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/read_file")
async def api_read_file(data: dict):
    result = await read_file(data.get("path", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/list_files")
async def api_list_files(data: dict):
    result = await list_files(data.get("directory", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/get_disk_usage")
async def api_disk_usage():
    result = await get_disk_usage()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/get_network_info")
async def api_network():
    result = await get_network_info()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/get_battery_status")
async def api_battery():
    result = await get_battery_status()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/search_web")
async def api_search(data: dict):
    result = await search_web(data.get("query", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/get_clipboard")
async def api_get_clip():
    result = await get_clipboard()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/set_clipboard")
async def api_set_clip(data: dict):
    result = await set_clipboard(data.get("text", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/play_sound")
async def api_sound(data: dict):
    result = await play_sound(data.get("frequency", 1000), data.get("duration", 500))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/set_volume")
async def api_tool_set_volume(data: dict):
    result = await set_volume(data.get("level", 50))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/set_brightness")
async def api_brightness(data: dict):
    result = await set_brightness(data.get("level", 50))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/mute_volume")
async def api_mute_volume(data: dict):
    result = await mute_volume()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/unmute_volume")
async def api_unmute_volume(data: dict):
    result = await unmute_volume()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/volume_up")
async def api_volume_up(data: dict):
    result = await volume_up(data.get("steps", 5))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/volume_down")
async def api_volume_down(data: dict):
    result = await volume_down(data.get("steps", 5))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/minimize_all_windows")
async def api_minimize():
    result = await show_desktop()  # Sử dụng show_desktop thay vì minimize_all_windows
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/undo_action")
async def api_undo():
    result = await undo_operation()  # Sử dụng undo_operation thay vì undo_action
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/toggle_dark_mode")
async def api_theme():
    result = await set_theme(dark_mode=None)  # Toggle bằng cách để None, hàm set_theme sẽ xử lý
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/set_wallpaper")
async def api_wallpaper(data: dict):
    path = data.get("path", "")
    keyword = data.get("keyword", "")
    # Dùng change_wallpaper với custom_path nếu có path
    result = await change_wallpaper(keyword=keyword, custom_path=path)
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/paste_text")
async def api_paste():
    result = await paste_content(content="")  # paste_content với clipboard hiện tại
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/press_enter")
async def api_enter():
    result = await press_enter()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/find_on_screen")
async def api_find(data: dict):
    result = await find_in_document(data.get("text", ""))  # Sử dụng find_in_document
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/lock_computer")
async def api_lock():
    result = await lock_computer()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/shutdown_computer")
async def api_shutdown(data: dict):
    delay = data.get("delay", 0)
    # Sử dụng shutdown_schedule với action="shutdown"
    result = await shutdown_schedule(action="shutdown", delay=delay)
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result


@app.get("/logo.png")
async def get_logo():
    from fastapi.responses import FileResponse
    import os
    import sys
    
    # Tìm logo theo thứ tự ưu tiên
    possible_paths = []
    
    # 1. PyInstaller frozen EXE - trong thư mục _internal hoặc cùng thư mục EXE
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        possible_paths.extend([
            os.path.join(exe_dir, "_internal", "logo.png"),
            os.path.join(exe_dir, "logo.png"),
            os.path.join(getattr(sys, '_MEIPASS', exe_dir), "logo.png"),
        ])
    
    # 2. Thư mục script
    possible_paths.append(os.path.join(os.path.dirname(__file__), "logo.png"))
    
    # 3. Thư mục làm việc hiện tại
    possible_paths.append(os.path.join(os.getcwd(), "logo.png"))
    
    # Tìm file đầu tiên tồn tại
    for logo_path in possible_paths:
        if os.path.exists(logo_path):
            return FileResponse(logo_path, media_type="image/png")
    
    # Log để debug
    print(f"⚠️ Logo not found. Checked paths: {possible_paths}")
    raise HTTPException(404, "Logo not found")

@app.get("/api/endpoints")
async def get_endpoints():
    global GEMINI_API_KEY, OPENAI_API_KEY, SERPER_API_KEY
    return {
        "endpoints": endpoints_config,
        "gemini_api_key": GEMINI_API_KEY,
        "openai_api_key": OPENAI_API_KEY,
        "serper_api_key": SERPER_API_KEY
    }

# YouTube Playlists API
@app.get("/api/youtube_playlists")
async def api_get_youtube_playlists():
    """Lấy danh sách playlist YouTube"""
    return await get_youtube_playlists()

@app.post("/api/youtube_playlists/add")
async def api_add_youtube_playlist(data: dict):
    """Thêm playlist YouTube mới"""
    name = data.get("name", "").strip()
    url = data.get("url", "").strip()
    
    if not name or not url:
        return {"success": False, "error": "Tên và URL không được để trống"}
    
    return await add_youtube_playlist(name, url)

@app.post("/api/youtube_playlists/remove")
async def api_remove_youtube_playlist(data: dict):
    """Xóa playlist YouTube"""
    name = data.get("name", "").strip()
    
    if not name:
        return {"success": False, "error": "Tên playlist không được để trống"}
    
    return await remove_youtube_playlist(name)

# ============================================================
# KNOWLEDGE BASE API - Quản lý dữ liệu cho LLM
# ============================================================

# File lưu cấu hình knowledge base - Lưu vào AppData để tránh Permission denied
def get_knowledge_data_dir():
    """Lấy thư mục lưu trữ knowledge base data trong AppData"""
    if os.name == 'nt':  # Windows
        appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
        data_dir = Path(appdata) / "miniZ_MCP" / "knowledge"
    else:  # Linux/Mac
        data_dir = Path.home() / ".miniz_mcp" / "knowledge"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

KNOWLEDGE_DATA_DIR = get_knowledge_data_dir()
KNOWLEDGE_CONFIG_FILE = KNOWLEDGE_DATA_DIR / "knowledge_config.json"
KNOWLEDGE_INDEX_FILE = KNOWLEDGE_DATA_DIR / "knowledge_index.json"

# Các extension được hỗ trợ
SUPPORTED_EXTENSIONS = {'.pdf', '.txt', '.docx', '.doc', '.md', '.json', '.csv', '.xlsx', '.xls', '.rtf'}

def load_knowledge_config():
    """Load cấu hình knowledge base"""
    if KNOWLEDGE_CONFIG_FILE.exists():
        try:
            # Sử dụng utf-8-sig để tự động xử lý BOM
            with open(KNOWLEDGE_CONFIG_FILE, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ [Knowledge] Error loading config: {e}")
    return {"folder_path": "", "indexed_files": [], "last_update": ""}

def save_knowledge_config(config: dict):
    """Lưu cấu hình knowledge base"""
    try:
        with open(KNOWLEDGE_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ [Knowledge] Error saving config: {e}")
        return False

def load_knowledge_index():
    """Load index đã lưu"""
    if KNOWLEDGE_INDEX_FILE.exists():
        try:
            # Sử dụng utf-8-sig để tự động xử lý BOM
            with open(KNOWLEDGE_INDEX_FILE, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ [Knowledge] Error loading index: {e}")
    return {"documents": [], "total_chunks": 0, "last_update": ""}

def save_knowledge_index(index_data: dict):
    """Lưu index"""
    try:
        with open(KNOWLEDGE_INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ [Knowledge] Error saving index: {e}")
        return False

async def summarize_with_gemini(text: str, filename: str) -> dict:
    """Tóm tắt document bằng Gemini Flash"""
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Tạo prompt để tóm tắt
        prompt = f"""Hãy phân tích và tóm tắt nội dung của tài liệu sau đây:

Tên file: {filename}

Nội dung:
{text[:8000]}  # Giới hạn 8K ký tự để tránh quá tải

---

Yêu cầu:
1. Tóm tắt ngắn gọn (2-3 câu) về nội dung chính
2. Liệt kê 5-7 keywords quan trọng
3. Trích dẫn 2-3 câu quan trọng nhất từ tài liệu
4. Phân loại tài liệu (ví dụ: technical, business, educational, etc.)

Trả lời theo format JSON:
{{
  "summary": "...",
  "keywords": ["...", "..."],
  "key_quotes": ["...", "..."],
  "category": "..."
}}"""
        
        print(f"🤖 [Gemini] Đang tóm tắt: {filename}...")
        response = model.generate_content(prompt)
        
        # Parse JSON response
        import json
        result_text = response.text.strip()
        # Remove markdown code blocks if present
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        result_text = result_text.strip()
        
        result = json.loads(result_text)
        print(f"✅ [Gemini] Đã tóm tắt: {filename}")
        return result
        
    except Exception as e:
        print(f"⚠️ [Gemini] Lỗi tóm tắt {filename}: {e}")
        # Fallback: trả về summary cơ bản
        return {
            "summary": text[:500] + "...",
            "keywords": [],
            "key_quotes": [],
            "category": "unknown"
        }

def extract_text_from_file(file_path: str) -> str:
    """Trích xuất text từ file"""
    ext = Path(file_path).suffix.lower()
    text = ""
    
    try:
        if ext == '.txt' or ext == '.md':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        
        elif ext == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                text = json.dumps(data, ensure_ascii=False, indent=2)
        
        elif ext == '.csv':
            import csv
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                rows = [', '.join(row) for row in reader]
                text = '\n'.join(rows)
        
        elif ext == '.pdf':
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
            except ImportError:
                text = f"[PDF file - Cần cài PyPDF2: pip install PyPDF2]"
            except Exception as e:
                text = f"[Lỗi đọc PDF: {str(e)}]"
        
        elif ext in ['.docx', '.doc']:
            try:
                from docx import Document
                doc = Document(file_path)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            except ImportError:
                text = f"[Word file - Cần cài python-docx: pip install python-docx]"
            except Exception as e:
                text = f"[Lỗi đọc Word: {str(e)}]"
        
        elif ext in ['.xlsx', '.xls']:
            try:
                import openpyxl
                wb = openpyxl.load_workbook(file_path, data_only=True)
                for sheet in wb.worksheets:
                    for row in sheet.iter_rows():
                        row_text = ', '.join([str(cell.value) if cell.value else '' for cell in row])
                        if row_text.strip():
                            text += row_text + "\n"
            except ImportError:
                text = f"[Excel file - Cần cài openpyxl: pip install openpyxl]"
            except Exception as e:
                text = f"[Lỗi đọc Excel: {str(e)}]"
        
        elif ext == '.rtf':
            try:
                from striprtf.striprtf import rtf_to_text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    rtf_content = f.read()
                text = rtf_to_text(rtf_content)
            except ImportError:
                text = f"[RTF file - Cần cài striprtf: pip install striprtf]"
            except Exception as e:
                text = f"[Lỗi đọc RTF: {str(e)}]"
        
    except Exception as e:
        text = f"[Lỗi đọc file: {str(e)}]"
    
    return text.strip()

def scan_folder_for_files(folder_path: str) -> list:
    """Quét thư mục và trả về danh sách files được hỗ trợ"""
    files = []
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ [Scan] Folder not exists: {folder_path}")
        return files
    
    print(f"📂 [Scan] Scanning folder: {folder_path}")
    total_checked = 0
    
    for file_path in folder.rglob('*'):
        if file_path.is_file():
            total_checked += 1
            ext = file_path.suffix.lower()
            if ext in SUPPORTED_EXTENSIONS:
                try:
                    stat = file_path.stat()
                    files.append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                        "extension": ext,
                        "indexed": False
                    })
                    print(f"  ✅ Added: {file_path.name} ({ext})")
                except Exception as e:
                    print(f"  ⚠️ Error scanning file {file_path}: {e}")
            else:
                print(f"  ⏭️ Skipped: {file_path.name} ({ext}) - Not supported")
    
    print(f"📊 [Scan] Result: {len(files)} files found (checked {total_checked} files)")
    return files

@app.get("/api/knowledge/status")
async def api_knowledge_status():
    """Lấy trạng thái Knowledge Base"""
    config = load_knowledge_config()
    index = load_knowledge_index()
    
    folder_path = config.get("folder_path", "")
    files = []
    total_size = 0
    
    if folder_path and Path(folder_path).exists():
        files = scan_folder_for_files(folder_path)
        total_size = sum(f["size"] for f in files)
        
        # Đánh dấu các file đã được index
        indexed_paths = set(config.get("indexed_files", []))
        for f in files:
            f["indexed"] = f["path"] in indexed_paths
    
    return {
        "success": True,
        "folder_path": folder_path,
        "total_files": len(files),
        "indexed_files": len(config.get("indexed_files", [])),
        "total_size": total_size,
        "last_update": config.get("last_update", "--"),
        "files": files
    }

@app.post("/api/knowledge/set_folder")
async def api_knowledge_set_folder(data: dict):
    """Cấu hình thư mục knowledge base"""
    folder_path = data.get("folder_path", "").strip()
    
    if not folder_path:
        return {"success": False, "error": "Đường dẫn không được để trống"}
    
    # Kiểm tra thư mục tồn tại
    if not Path(folder_path).exists():
        return {"success": False, "error": f"Thư mục không tồn tại: {folder_path}"}
    
    if not Path(folder_path).is_dir():
        return {"success": False, "error": "Đường dẫn phải là thư mục, không phải file"}
    
    config = load_knowledge_config()
    config["folder_path"] = folder_path
    config["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    if save_knowledge_config(config):
        return {"success": True, "message": f"Đã lưu thư mục: {folder_path}"}
    else:
        return {"success": False, "error": "Lỗi khi lưu cấu hình"}

@app.post("/api/knowledge/scan")
async def api_knowledge_scan(data: dict):
    """Quét thư mục để tìm files"""
    folder_path = data.get("folder_path", "").strip()
    
    if not folder_path:
        config = load_knowledge_config()
        folder_path = config.get("folder_path", "")
    
    if not folder_path:
        return {"success": False, "error": "Chưa cấu hình thư mục"}
    
    if not Path(folder_path).exists():
        return {"success": False, "error": f"Thư mục không tồn tại: {folder_path}"}
    
    files = scan_folder_for_files(folder_path)
    total_size = sum(f["size"] for f in files)
    
    # Cập nhật config
    config = load_knowledge_config()
    config["folder_path"] = folder_path
    indexed_paths = set(config.get("indexed_files", []))
    for f in files:
        f["indexed"] = f["path"] in indexed_paths
    save_knowledge_config(config)
    
    return {
        "success": True,
        "total_files": len(files),
        "total_size": total_size,
        "files": files
    }

@app.post("/api/knowledge/index_all")
async def api_knowledge_index_all():
    """Index tất cả files trong thư mục"""
    config = load_knowledge_config()
    folder_path = config.get("folder_path", "")
    
    if not folder_path or not Path(folder_path).exists():
        return {"success": False, "error": "Chưa cấu hình thư mục hoặc thư mục không tồn tại"}
    
    files = scan_folder_for_files(folder_path)
    indexed_count = 0
    documents = []
    
    for file_info in files:
        try:
            text = extract_text_from_file(file_info["path"])
            if text and not text.startswith("["):  # Không phải lỗi
                # Tóm tắt bằng Gemini Flash
                ai_summary = await summarize_with_gemini(text, file_info["name"])
                
                documents.append({
                    "file_path": file_info["path"],
                    "file_name": file_info["name"],
                    "content": text[:50000],  # Giới hạn 50k ký tự mỗi file
                    "summary": ai_summary.get("summary", ""),
                    "keywords": ai_summary.get("keywords", []),
                    "key_quotes": ai_summary.get("key_quotes", []),
                    "category": ai_summary.get("category", "general"),
                    "indexed_at": datetime.now().isoformat()
                })
                indexed_count += 1
        except Exception as e:
            print(f"⚠️ Error indexing {file_info['path']}: {e}")
    
    # Lưu index
    index_data = {
        "documents": documents,
        "total_chunks": indexed_count,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    save_knowledge_index(index_data)
    
    # Cập nhật config
    config["indexed_files"] = [f["path"] for f in files if any(d["file_path"] == f["path"] for d in documents)]
    config["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_knowledge_config(config)
    
    return {
        "success": True,
        "message": f"Đã index {indexed_count}/{len(files)} files",
        "indexed_count": indexed_count,
        "last_update": index_data["last_update"]
    }

@app.post("/api/knowledge/index_file")
async def api_knowledge_index_file(data: dict):
    """Index một file cụ thể"""
    file_path = data.get("file_path", "").strip()
    
    if not file_path or not Path(file_path).exists():
        return {"success": False, "error": "File không tồn tại"}
    
    try:
        text = extract_text_from_file(file_path)
        if not text or text.startswith("["):
            return {"success": False, "error": f"Không thể đọc file: {text}"}
        
        # Load existing index
        index_data = load_knowledge_index()
        
        # Remove existing entry for this file
        index_data["documents"] = [d for d in index_data["documents"] if d["file_path"] != file_path]
        
        # Tóm tắt bằng Gemini Flash
        ai_summary = await summarize_with_gemini(text, Path(file_path).name)
        
        # Add new entry
        index_data["documents"].append({
            "file_path": file_path,
            "file_name": Path(file_path).name,
            "content": text[:50000],
            "summary": ai_summary.get("summary", ""),
            "keywords": ai_summary.get("keywords", []),
            "key_quotes": ai_summary.get("key_quotes", []),
            "category": ai_summary.get("category", "general"),
            "indexed_at": datetime.now().isoformat()
        })
        index_data["total_chunks"] = len(index_data["documents"])
        index_data["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        save_knowledge_index(index_data)
        
        # Update config
        config = load_knowledge_config()
        if file_path not in config.get("indexed_files", []):
            config.setdefault("indexed_files", []).append(file_path)
        config["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_knowledge_config(config)
        
        return {"success": True, "message": f"Đã index: {Path(file_path).name}"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/knowledge/clear")
async def api_knowledge_clear():
    """Xóa toàn bộ index"""
    try:
        # Clear index file
        save_knowledge_index({"documents": [], "total_chunks": 0, "last_update": ""})
        
        # Update config
        config = load_knowledge_config()
        config["indexed_files"] = []
        config["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_knowledge_config(config)
        
        return {"success": True, "message": "Đã xóa toàn bộ index"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/knowledge/search")
async def api_knowledge_search(query: str = ""):
    """Tìm kiếm trong knowledge base"""
    if not query:
        return {"success": False, "error": "Vui lòng nhập từ khóa tìm kiếm"}
    
    index_data = load_knowledge_index()
    documents = index_data.get("documents", [])
    
    if not documents:
        return {"success": False, "error": "Knowledge base chưa có dữ liệu. Vui lòng index files trước."}
    
    # AI-powered search - tìm trong summary, keywords và content
    query_lower = query.lower()
    results = []
    
    for doc in documents:
        score = 0
        matched_in = []
        
        # Tìm trong summary (điểm cao nhất)
        summary = doc.get("summary", "")
        if query_lower in summary.lower():
            score += 10
            matched_in.append("summary")
        
        # Tìm trong keywords (điểm trung bình)
        keywords = doc.get("keywords", [])
        for keyword in keywords:
            if query_lower in keyword.lower():
                score += 5
                matched_in.append("keywords")
                break
        
        # Tìm trong content (điểm thấp nhất)
        content = doc.get("content", "")
        if query_lower in content.lower():
            score += 1
            matched_in.append("content")
            
            # Tìm đoạn text chứa query
            idx = content.lower().find(query_lower)
            start = max(0, idx - 200)
            end = min(len(content), idx + 200)
            snippet = content[start:end]
        else:
            snippet = summary[:400] if summary else content[:400]
        
        # Chỉ thêm vào results nếu có match
        if score > 0:
            results.append({
                "file_name": doc.get("file_name", ""),
                "file_path": doc.get("file_path", ""),
                "summary": summary,
                "keywords": keywords,
                "category": doc.get("category", "general"),
                "snippet": "..." + snippet + "...",
                "score": score,
                "matched_in": matched_in,
                "indexed_at": doc.get("indexed_at", "")
            })
    
    # Sắp xếp theo score
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "success": True,
        "query": query,
        "total_results": len(results),
        "results": results[:20]  # Giới hạn 20 kết quả
    }

@app.get("/api/knowledge/context")
async def api_knowledge_get_context(query: str = "", max_chars: int = 10000):
    """Lấy context từ knowledge base để cung cấp cho LLM"""
    index_data = load_knowledge_index()
    documents = index_data.get("documents", [])
    
    if not documents:
        return {"success": False, "context": "", "message": "Knowledge base trống"}
    
    context_parts = []
    total_chars = 0
    
    # Nếu có query, ưu tiên các document liên quan
    if query:
        query_lower = query.lower()
        # Sắp xếp theo độ liên quan
        scored_docs = []
        for doc in documents:
            content = doc.get("content", "")
            score = content.lower().count(query_lower)
            scored_docs.append((score, doc))
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        documents = [d for _, d in scored_docs]
    
    for doc in documents:
        file_name = doc.get("file_name", "unknown")
        summary = doc.get("summary", "")
        keywords = doc.get("keywords", [])
        key_quotes = doc.get("key_quotes", [])
        category = doc.get("category", "general")
        
        # Ưu tiên dùng summary và key_quotes thay vì full content
        # Điều này giảm đáng kể token và tăng chất lượng context
        
        # Build compact context
        compact_content = f"📝 {summary}\n"
        if keywords:
            compact_content += f"🔑 Keywords: {', '.join(keywords[:5])}\n"
        if key_quotes:
            compact_content += f"💬 Trích dẫn:\n"
            for quote in key_quotes[:3]:
                compact_content += f"  • {quote}\n"
        
        # Thêm header cho mỗi document
        header = f"\n\n=== [{category.upper()}] {file_name} ===\n"
        full_entry = header + compact_content
        
        if total_chars + len(full_entry) > max_chars:
            break
        else:
            context_parts.append(full_entry)
            total_chars += len(full_entry)
    
    full_context = "".join(context_parts)
    
    return {
        "success": True,
        "context": full_context,
        "total_documents": len(documents),
        "context_length": len(full_context)
    }

# ============================================================
# TASK MEMORY API - Ghi nhớ tác vụ đã thực hiện
# ============================================================

@app.get("/api/tasks/recent")
async def api_get_recent_tasks(limit: int = 10):
    """Lấy các tác vụ gần đây"""
    tasks = get_recent_tasks(limit)
    return {
        "success": True,
        "count": len(tasks),
        "tasks": tasks
    }

@app.get("/api/tasks/search/{keyword}")
async def api_search_tasks(keyword: str):
    """Tìm kiếm tác vụ theo từ khóa"""
    results = search_task_memory(keyword)
    return {
        "success": True,
        "count": len(results),
        "tasks": results
    }

@app.get("/api/tasks/all")
async def api_get_all_tasks():
    """Lấy toàn bộ lịch sử tác vụ"""
    tasks = load_task_memory()
    return {
        "success": True,
        "total": len(tasks),
        "tasks": tasks
    }

@app.post("/api/tasks/clear")
async def api_clear_tasks():
    """Xóa toàn bộ lịch sử tác vụ"""
    success = clear_task_memory()
    return {
        "success": success,
        "message": "Đã xóa toàn bộ lịch sử tác vụ" if success else "Lỗi khi xóa"
    }

@app.get("/api/tasks/summary")
async def api_get_task_summary():
    """Lấy tổng hợp thống kê tác vụ"""
    tasks = load_task_memory()
    
    if not tasks:
        return {
            "success": True,
            "total_tasks": 0,
            "by_tool": {},
            "success_rate": 0,
            "recent_tools": []
        }
    
    # Đếm theo tool
    tool_counts = {}
    success_count = 0
    
    for task in tasks:
        tool = task.get('tool', 'unknown')
        tool_counts[tool] = tool_counts.get(tool, 0) + 1
        if task.get('result_success'):
            success_count += 1
    
    # Sắp xếp theo số lần sử dụng
    sorted_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "success": True,
        "total_tasks": len(tasks),
        "by_tool": dict(sorted_tools[:20]),
        "success_rate": round(success_count / len(tasks) * 100, 1),
        "recent_tools": [t.get('tool') for t in tasks[-5:]]
    }

# ============================================================
# CONVERSATION HISTORY API
# ============================================================

@app.get("/api/conversation/history")
async def api_get_conversation_history():
    """Lấy toàn bộ lịch sử hội thoại"""
    return {
        "success": True,
        "total_messages": len(conversation_history),
        "messages": conversation_history
    }

@app.get("/api/conversation/recent/{count}")
async def api_get_recent_conversation(count: int = 10):
    """Lấy N messages gần nhất"""
    recent = conversation_history[-count:] if len(conversation_history) > count else conversation_history
    return {
        "success": True,
        "count": len(recent),
        "messages": recent
    }

@app.post("/api/conversation/clear")
async def api_clear_conversation():
    """Xóa toàn bộ lịch sử hội thoại"""
    global conversation_history
    conversation_history = []
    save_conversation_history()
    return {
        "success": True,
        "message": "Đã xóa toàn bộ lịch sử hội thoại"
    }

@app.post("/api/conversation/export")
async def api_export_conversation(data: dict = None):
    """Export lịch sử hội thoại ra file"""
    filename = data.get("filename", "") if data else ""
    return await export_conversation_to_file(filename)

@app.post("/api/conversation/add")
async def api_add_conversation_message(data: dict):
    """Thêm message từ Web UI vào history"""
    role = data.get("role", "user")
    content = data.get("content", "")
    metadata = data.get("metadata", {})
    
    if not content:
        return {"success": False, "error": "Content không được để trống"}
    
    add_to_conversation(role, content, metadata)
    
    return {
        "success": True,
        "message": "Đã thêm message vào history"
    }

@app.post("/api/chat/log")
async def api_log_chat_message(data: dict):
    """
    Endpoint đặc biệt để Web UI log TOÀN BỘ cuộc hội thoại
    Dùng cho các chat không qua MCP
    """
    messages = data.get("messages", [])
    
    if not messages:
        return {"success": False, "error": "Không có messages để log"}
    
    # Log từng message
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        metadata = msg.get("metadata", {})
        
        if content:
            add_to_conversation(role, content, metadata)
    
    return {
        "success": True,
        "message": f"Đã log {len(messages)} messages vào history",
        "total_messages": len(conversation_history)
    }

# ============================================================
# USER PROFILE API - Hiểu người dùng
# ============================================================

@app.get("/api/user/profile")
async def api_get_user_profile():
    """Lấy user profile"""
    return {
        "success": True,
        "profile": load_user_profile(),
        "summary": get_user_profile_summary()
    }

@app.get("/api/user/context")
async def api_get_user_context(max_messages: int = 10):
    """Lấy context từ lịch sử hội thoại + user profile"""
    return {
        "success": True,
        "user_profile": get_user_profile_summary(),
        "recent_conversation": get_conversation_context(max_messages),
        "hint": "Dùng thông tin này để hiểu người dùng tốt hơn"
    }

@app.get("/api/conversation/files")
async def api_list_conversation_files():
    """Liệt kê các file hội thoại đã lưu"""
    files = list_conversation_files()
    return {
        "success": True,
        "storage_path": str(CONVERSATION_BASE_DIR),
        "total_files": len(files),
        "files": files
    }

@app.get("/api/conversation/today")
async def api_get_today_conversation():
    """Lấy hội thoại của ngày hôm nay"""
    today_file = get_today_conversation_file()
    if today_file.exists():
        try:
            with open(today_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    return {"success": True, "data": {"date": datetime.now().strftime("%Y-%m-%d"), "messages": []}}

@app.post("/api/endpoints/switch/{index}")
async def switch_endpoint(index: int):
    global active_endpoint_index, should_reconnect
    if index < 0 or index >= len(endpoints_config):
        return {"success": False, "error": "Thiết bị không tồn tại"}
    
    device = endpoints_config[index]
    if not device.get("token"):
        return {"success": False, "error": "Thiết bị chưa có token. Hãy nhập token và lưu lại!"}
    
    # Thay đổi endpoint và trigger reconnect
    old_index = active_endpoint_index
    active_endpoint_index = index
    should_reconnect = True  # Trigger reconnect trong xiaozhi_websocket_client
    
    # Lưu vào file
    save_endpoints_to_file(endpoints_config, active_endpoint_index)
    
    print(f"🔄 [Endpoint] Switching from device {old_index} to {index} ({device['name']})")
    
    return {"success": True, "message": f"Đã chuyển sang {device['name']}. Đang kết nối lại..."}

@app.post("/api/endpoints/save")
async def save_endpoints(data: dict):
    global endpoints_config, should_reconnect
    try:
        devices = data.get('devices', [])
        if not devices:
            return {"success": False, "error": "Không có dữ liệu"}
        
        # Lưu token cũ của thiết bị đang active để so sánh
        old_active_token = endpoints_config[active_endpoint_index].get('token', '') if active_endpoint_index < len(endpoints_config) else ''
        
        # Cập nhật endpoints_config
        endpoints_config = []
        for dev in devices:
            endpoints_config.append({
                'name': dev.get('name', 'Thiết bị'),
                'token': dev.get('token', ''),
                'enabled': bool(dev.get('token', ''))
            })
        
        # Lưu vào file JSON
        if save_endpoints_to_file(endpoints_config, active_endpoint_index):
            print(f"✅ [Endpoint] Successfully saved {len(devices)} devices to file")
        else:
            print(f"⚠️ [Endpoint] Failed to save to file, but config updated in memory")
        
        # CHỈ reconnect nếu token thay đổi VÀ có giá trị mới khác rỗng
        new_active_token = endpoints_config[active_endpoint_index].get('token', '') if active_endpoint_index < len(endpoints_config) else ''
        if old_active_token != new_active_token and new_active_token and old_active_token:
            # Token đã thay đổi (không phải lần đầu nhập)
            should_reconnect = True
            print(f"🔄 [Endpoint] Token changed for active device {active_endpoint_index}. Triggering reconnect...")
        
        return {"success": True, "message": "Đã lưu cấu hình"}
    except Exception as e:
        print(f"❌ [Endpoint] Error saving: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@app.post("/api/gemini-key")
async def save_gemini_key(data: dict):
    """Save Gemini API key - Auto-save endpoint"""
    global GEMINI_API_KEY
    try:
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return {"success": False, "error": "API key không được để trống"}
        
        # Validate format (Gemini API key starts with AIzaSy)
        if not api_key.startswith('AIzaSy'):
            return {"success": False, "error": "API key không hợp lệ (phải bắt đầu với 'AIzaSy')"}
        
        # Update global variable
        GEMINI_API_KEY = api_key
        
        # Save to file
        if save_endpoints_to_file(endpoints_config, active_endpoint_index):
            print(f"✅ [Gemini] API key saved (ends with ...{api_key[-8:]})")
            return {
                "success": True,
                "message": "✓ Đã lưu Gemini API key",
                "key_preview": f"...{api_key[-8:]}"
            }
        else:
            return {"success": False, "error": "Lỗi lưu file config"}
    except Exception as e:
        print(f"❌ [Gemini] Error saving API key: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/openai-key")
async def save_openai_key(data: dict):
    """Save OpenAI API key - Auto-save endpoint"""
    global OPENAI_API_KEY
    try:
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return {"success": False, "error": "API key không được để trống"}
        
        # Validate format (OpenAI API key starts with sk-)
        if not api_key.startswith('sk-'):
            return {"success": False, "error": "API key không hợp lệ (phải bắt đầu với 'sk-')"}
        
        # Update global variable
        OPENAI_API_KEY = api_key
        
        # Save to file
        if save_endpoints_to_file(endpoints_config, active_endpoint_index):
            print(f"✅ [OpenAI] API key saved (ends with ...{api_key[-8:]})")
            return {
                "success": True,
                "message": "✓ Đã lưu OpenAI API key",
                "key_preview": f"...{api_key[-8:]}"
            }
        else:
            return {"success": False, "error": "Lỗi lưu file config"}
    except Exception as e:
        print(f"❌ [OpenAI] Error saving API key: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/serper-key")
async def save_serper_key(data: dict):
    """Save Serper API key (Google Search) - Auto-save endpoint"""
    global SERPER_API_KEY
    try:
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return {"success": False, "error": "API key không được để trống"}
        
        # Update global variable
        SERPER_API_KEY = api_key
        
        # Cập nhật environment variable để rag_system.py có thể dùng
        os.environ['SERPER_API_KEY'] = api_key
        
        # Save to file
        if save_endpoints_to_file(endpoints_config, active_endpoint_index):
            print(f"✅ [Serper] Google Search API key saved (ends with ...{api_key[-8:]})")
            return {
                "success": True,
                "message": "✓ Đã lưu Serper API key - Google Search sẵn sàng!",
                "key_preview": f"...{api_key[-8:]}"
            }
        else:
            return {"success": False, "error": "Lỗi lưu file config"}
    except Exception as e:
        print(f"❌ [Serper] Error saving API key: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/serper-key")
async def get_serper_key():
    """Get current Serper API key status"""
    if SERPER_API_KEY:
        return {
            "success": True,
            "has_key": True,
            "key_preview": f"...{SERPER_API_KEY[-8:]}"
        }
    return {"success": True, "has_key": False}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        await websocket.send_json({"type": "xiaozhi_status", "connected": xiaozhi_connected})
        while True:
            data = await websocket.receive_text()
            
            # Parse và log WebSocket messages
            try:
                msg_data = json.loads(data)
                msg_type = msg_data.get("type", "")
                
                # Lưu user messages từ Web UI
                if msg_type == "chat_message":
                    user_msg = msg_data.get("message", "")
                    if user_msg:
                        add_to_conversation(
                            role="user",
                            content=user_msg,
                            metadata={
                                "source": "websocket",
                                "msg_type": msg_type
                            }
                        )
                
                # Lưu AI responses từ Web UI
                elif msg_type == "ai_response":
                    ai_msg = msg_data.get("response", "")
                    if ai_msg:
                        add_to_conversation(
                            role="assistant",
                            content=ai_msg,
                            metadata={
                                "source": "websocket",
                                "msg_type": msg_type,
                                "model": msg_data.get("model", "unknown")
                            }
                        )
            except json.JSONDecodeError:
                pass  # Not JSON, skip logging
            
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"⚠️ WebSocket client error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.on_event("startup")
async def startup():
    # Check music folder config and notify
    config_info = check_music_folder_config()
    if config_info.get("has_config"):
        folder_path = config_info.get("folder_path", "")
        print(f"🎵 [Music Config] User music folder configured: {folder_path}")
        print(f"⭐ [Music Priority] Will use play_music_from_user_folder for music requests")
    else:
        print(f"⚠️ [Music Config] No user music folder configured. Will use VLC music_library as fallback.")
    
    # Enable WebSocket client with error handling
    try:
        asyncio.create_task(xiaozhi_websocket_client())
    except Exception as e:
        print(f"⚠️ Failed to start WebSocket client: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading
    import time
    
    # ============================================================
    # LICENSE VERIFICATION - PROFESSIONAL EDITION
    # ============================================================
    if LICENSE_SYSTEM_AVAILABLE:
        print("=" * 60)
        print(" 🔐 miniZ MCP v4.3.0 - PROFESSIONAL EDITION")
        print("=" * 60)
        print(" Đang kiểm tra license...")
        
        license_manager = get_license_manager()
        license_status = license_manager.check_license()
        
        if not license_status['valid']:
            print(f" ❌ {license_status['message']}")
            print(" 📋 Hardware ID của máy này:")
            print(f"    {license_manager.get_hardware_id()}")
            print()
            print(" Vui lòng kích hoạt license để tiếp tục...")
            print("=" * 60)
            
            # Show activation window
            try:
                activated = show_activation_window()
                if not activated:
                    print("\n❌ Chưa kích hoạt license. Thoát chương trình.")
                    sys.exit(1)
                else:
                    print("\n✅ License kích hoạt thành công!")
                    license_status = license_manager.check_license()
            except Exception as e:
                print(f"\n❌ Lỗi khi mở cửa sổ kích hoạt: {e}")
                print("Vui lòng liên hệ hỗ trợ: support@miniz-mcp.com")
                sys.exit(1)
        else:
            print(f" ✅ License hợp lệ")
            print(f" 📋 Loại: {license_status['license_data'].get('license_type', 'N/A')}")
            print(f" 👤 Khách hàng: {license_status['license_data'].get('customer_name', 'N/A')}")
            print(f" 🔑 Hardware ID: {license_manager.get_hardware_id()}")
            
            if license_status.get('warning'):
                print(f" {license_status['warning']}")
            
            print("=" * 60)
    else:
        print("⚠️ WARNING: License system not available - Running in trial mode")
        print("=" * 60)
    
    # ============================================================
    # START SERVER
    # ============================================================
    
    def open_browser():
        """Mo browser sau 2 giay"""
        time.sleep(2)
        webbrowser.open("http://localhost:8000")
    
    # Khoi dong thread mo browser
    threading.Thread(target=open_browser, daemon=True).start()
    
    print()
    print("=" * 60)
    print(" 🚀 miniZ MCP - SIDEBAR UI")
    print("=" * 60)
    print(" 🌐 Web Dashboard: http://localhost:8000")
    print(" 📡 WebSocket MCP: Multi-device support")
    print(" 🛠️  Tools: 30 available (20 original + 10 new from reference)")
    print(" 🌐 Browser se tu dong mo sau 2 giay...")
    print("=" * 60)
    
    # Fix logging error when running as frozen EXE
    import sys
    if getattr(sys, 'frozen', False):
        # Disable uvicorn's default logging config when frozen
        uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000)

