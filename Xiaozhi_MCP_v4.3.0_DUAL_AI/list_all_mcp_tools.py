#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Liệt kê tất cả MCP Tools trong xiaozhi_final.py
"""

import re

def list_all_tools():
    # Đọc file
    with open('xiaozhi_final.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tìm TOOLS dictionary
    tools_match = re.search(r'TOOLS\s*=\s*\{(.*?)\n\}', content, re.DOTALL)
    
    if not tools_match:
        print("❌ Không tìm thấy TOOLS dictionary")
        return
    
    # Trích xuất tên tools
    tool_names = re.findall(r'"([^"]+)"\s*:\s*\{', tools_match.group(1))
    
    print("\n" + "="*80)
    print(f"   📋 DANH SÁCH TOOLS CỦA miniZ MCP v4.3.2 (3-DEVICE)")
    print("="*80 + "\n")
    print(f"✅ Tổng số tools: {len(tool_names)}\n")
    
    # Phân loại tools
    categories = {
        'AI & Chat': [],
        'Media Player': [],
        'YouTube Control': [],
        'File System': [],
        'Process & App': [],
        'Web Search': [],
        'System Control': [],
        'Info & Monitor': [],
        'Action & Input': [],
        'Other': []
    }
    
    for idx, tool in enumerate(tool_names, 1):
        tool_lower = tool.lower()
        
        if 'gemini' in tool_lower or 'gpt' in tool_lower or 'chat' in tool_lower:
            categories['AI & Chat'].append((idx, tool))
        elif 'vlc' in tool_lower or 'wmp' in tool_lower or 'music' in tool_lower or 'spotify' in tool_lower:
            categories['Media Player'].append((idx, tool))
        elif 'youtube' in tool_lower:
            categories['YouTube Control'].append((idx, tool))
        elif 'file' in tool_lower or 'folder' in tool_lower or 'directory' in tool_lower:
            categories['File System'].append((idx, tool))
        elif 'process' in tool_lower or 'application' in tool_lower or 'app' in tool_lower or 'kill' in tool_lower:
            categories['Process & App'].append((idx, tool))
        elif 'web' in tool_lower or 'search' in tool_lower or 'google' in tool_lower:
            categories['Web Search'].append((idx, tool))
        elif 'volume' in tool_lower or 'brightness' in tool_lower or 'clipboard' in tool_lower or 'wallpaper' in tool_lower or 'lock' in tool_lower or 'shutdown' in tool_lower or 'restart' in tool_lower or 'minimize' in tool_lower or 'dark_mode' in tool_lower or 'mute' in tool_lower:
            categories['System Control'].append((idx, tool))
        elif 'battery' in tool_lower or 'network' in tool_lower or 'disk' in tool_lower or 'system_info' in tool_lower or 'memory' in tool_lower or 'cpu' in tool_lower:
            categories['Info & Monitor'].append((idx, tool))
        elif 'screenshot' in tool_lower or 'notification' in tool_lower or 'calculator' in tool_lower or 'remember' in tool_lower or 'type' in tool_lower or 'mouse' in tool_lower or 'find' in tool_lower or 'paste' in tool_lower or 'enter' in tool_lower or 'undo' in tool_lower or 'sound' in tool_lower or 'click' in tool_lower or 'move' in tool_lower or 'scroll' in tool_lower:
            categories['Action & Input'].append((idx, tool))
        else:
            categories['Other'].append((idx, tool))
    
    # In ra theo danh mục
    print("📌 PHÂN LOẠI THEO CHỨC NĂNG:\n")
    
    for cat_name in ['AI & Chat', 'Media Player', 'YouTube Control', 'File System', 'Process & App', 'Web Search', 'System Control', 'Info & Monitor', 'Action & Input', 'Other']:
        if categories[cat_name]:
            print(f"\n🔹 {cat_name.upper()} ({len(categories[cat_name])} tools):")
            print("-" * 80)
            for num, name in categories[cat_name]:
                print(f"   {num:3d}. {name}")
    
    print("\n" + "="*80)
    print(f"   📊 THỐNG KÊ:")
    print("="*80)
    for cat_name in ['AI & Chat', 'Media Player', 'YouTube Control', 'File System', 'Process & App', 'Web Search', 'System Control', 'Info & Monitor', 'Action & Input', 'Other']:
        count = len(categories[cat_name])
        if count > 0:
            print(f"   • {cat_name:20s}: {count:3d} tools")
    
    print(f"\n   🎯 TỔNG CỘNG: {len(tool_names)} tools\n")
    print("="*80 + "\n")

if __name__ == '__main__':
    list_all_tools()
