"""
TEST: Text-to-Speech Tiếng Việt Support
Kiểm tra xem tool text_to_speech có hỗ trợ tiếng Việt không
"""
import asyncio
import sys
from xiaozhi_final import text_to_speech

async def test_tts_vietnamese():
    print("="*70)
    print("  TEXT-TO-SPEECH TIẾNG VIỆT - COMPATIBILITY TEST")
    print("="*70)
    
    # TEST 1: Short Vietnamese text
    print("\n📢 TEST 1: Văn bản tiếng Việt ngắn")
    print("-"*70)
    text1 = "Xin chào, đây là bài test tiếng Việt."
    print(f"Text: {text1}")
    result1 = await text_to_speech(text1, save_audio=False)
    print(f"✅ Result: {result1['message']}")
    print(f"   Success: {result1['success']}")
    
    # TEST 2: Long Vietnamese text (like screenshot)
    print("\n\n📢 TEST 2: Văn bản tiếng Việt dài (249 ký tự)")
    print("-"*70)
    text2 = """Gọi tool text_to_speech (text=Trám nằm trong cõi người ta.Chủ tài chỉ miệng khẽo là giải nhau Trái qua một cuộc bế đâu.Những điều trông thấy mà đâu dõng lạ gì bỉ sắc tự phong Trừ xanh quên thời mà hồng dành ghen.Các thơm làn giờ trước đen Phong tình cỗ lục còn truyền sự xanh save_audio=False)"""
    print(f"Text length: {len(text2)} chars")
    print(f"Text preview: {text2[:100]}...")
    result2 = await text_to_speech(text2, save_audio=False)
    print(f"✅ Result: {result2['message']}")
    print(f"   Success: {result2['success']}")
    print(f"   Length: {result2.get('text_length', 0)} chars")
    
    # TEST 3: Save audio file
    print("\n\n💾 TEST 3: Lưu file audio tiếng Việt")
    print("-"*70)
    text3 = "Đây là test lưu file audio tiếng Việt với giọng đọc Windows SAPI."
    print(f"Text: {text3}")
    result3 = await text_to_speech(text3, save_audio=True, filename="test_vietnamese_tts.wav")
    print(f"✅ Result: {result3['message']}")
    print(f"   Success: {result3['success']}")
    if result3['success']:
        print(f"   Path: {result3.get('path', 'N/A')}")
        print(f"   Size: {result3.get('size_bytes', 0)} bytes")
    
    # TEST 4: Check available voices
    print("\n\n🎤 TEST 4: Kiểm tra giọng nói có sẵn")
    print("-"*70)
    try:
        import win32com.client
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        voices = speaker.GetVoices()
        
        print(f"✅ Tìm thấy {voices.Count} giọng nói:")
        for i in range(voices.Count):
            voice = voices.Item(i)
            voice_name = voice.GetDescription()
            print(f"   {i+1}. {voice_name}")
            
            # Check if Vietnamese voice
            if any(keyword in voice_name.lower() for keyword in ['vietnam', 'vi-vn', 'vietnamese']):
                print(f"      ✅ TIẾNG VIỆT!")
        
        # Check current voice
        current_voice = speaker.Voice.GetDescription()
        print(f"\n🔊 Giọng đang dùng: {current_voice}")
        
    except Exception as e:
        print(f"⚠️ Không thể liệt kê voices: {e}")
    
    # SUMMARY
    print("\n\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    tests = [
        ("Short Vietnamese", result1),
        ("Long Vietnamese (249 chars)", result2),
        ("Save audio file", result3)
    ]
    
    all_passed = all(r['success'] for _, r in tests)
    
    for test_name, result in tests:
        status = "✅ PASSED" if result['success'] else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print("\n💡 PHÁT HIỆN:")
    print("   • Windows SAPI hoạt động với tiếng Việt")
    print("   • Giọng đọc: Phụ thuộc vào voice đã cài trong Windows")
    print("   • Nếu không có voice tiếng Việt → Đọc bằng English voice (accent lạ)")
    
    print("\n🔧 GIẢI PHÁP (nếu không có voice VN):")
    print("   1. Cài thêm Microsoft Voice Pack tiếng Việt")
    print("   2. HOẶC: Thêm gTTS (Google Text-to-Speech) vào code")
    print("      → gTTS hỗ trợ tiếng Việt native, online")
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED - TTS hoạt động với tiếng Việt!")
    else:
        print("\n⚠️ SOME TESTS FAILED - Cần kiểm tra lại")
    
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_tts_vietnamese())
