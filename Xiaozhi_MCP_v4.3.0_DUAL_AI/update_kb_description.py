# Update Knowledge Base tool description
with open('xiaozhi_final.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the exact location
marker = '"get_knowledge_context": {'
start_idx = content.find(marker)

if start_idx != -1:
    # Find the description line
    desc_start = content.find('"description":', start_idx)
    desc_end = content.find('",', desc_start)
    
    if desc_start != -1 and desc_end != -1:
        old_full = content[desc_start:desc_end + 2]  # Include the ending "
        
        new_desc_text = "📚 LẤY CONTEXT TỪ CƠ SỞ DỮ LIỆU TÀI LIỆU (Knowledge Base) - ⚡ GỌI ĐẦU TIÊN khi user hỏi về: dữ liệu cá nhân, tài liệu đã lưu, thông tin trong files, cơ sở dữ liệu nội bộ, knowledge base. Tool này tìm kiếm trong TẤT CẢ documents đã được index và trả về context đầy đủ nhất. ⛔ TRIGGERS BẮT BUỘC: 'cơ sở dữ liệu', 'database', 'knowledge base', 'tài liệu của tôi', 'thông tin trong file', 'theo dữ liệu', 'dữ liệu đã lưu', 'based on my docs', 'what's in my documents', 'tìm trong tài liệu', 'search my files', hỏi về TÊN NGƯỜI/DỰ ÁN cụ thể (có thể trong docs). QUY TRÌNH: 1) Gọi get_knowledge_context(query='keywords') 2) Nhận context từ docs 3) Dùng context trả lời. VD: 'Nguyễn Văn A làm gì?' → get_knowledge_context(query='Nguyễn Văn A') | 'Thông tin trong cơ sở dữ liệu về dự án X?' → get_knowledge_context(query='dự án X') | 'Tài liệu nói gì về ABC?' → get_knowledge_context(query='ABC')."
        
        new_full = f'        "description": "{new_desc_text}",'
        
        content = content.replace(old_full, new_full)
        
        with open('xiaozhi_final.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Updated successfully!")
        print(f"\nOld length: {len(old_full)}")
        print(f"New length: {len(new_full)}")
    else:
        print("❌ Could not find description field")
else:
    print("❌ get_knowledge_context not found")
