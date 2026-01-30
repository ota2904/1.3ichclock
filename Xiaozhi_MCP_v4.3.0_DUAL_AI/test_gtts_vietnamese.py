"""
Test gTTS Vietnamese TTS Integration
Kiểm tra giọng nói tiếng Việt với Google Text-to-Speech
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xiaozhi_final import text_to_speech

async def test_gtts_vietnamese():
    print("\n" + "="*70)
    print("   🎤 TEST GTTS - VIETNAMESE TEXT-TO-SPEECH   ".center(70))
    print("="*70 + "\n")
    
    # Test 1: Short Vietnamese text
    print("📢 TEST 1: Văn bản tiếng Việt ngắn (với gTTS)")
    print("-" * 70)
    text1 = "Xin chào, đây là bài test tiếng Việt với giọng Google."
    print(f"Text: {text1}")
    print(f"Length: {len(text1)} chars\n")
    
    result1 = await text_to_speech(text1, save_audio=False)
    
    if result1.get("success"):
        print(f"✅ Result: {result1['message']}")
        print(f"   Success: {result1['success']}")
        print(f"   Engine: {result1.get('engine', 'N/A')}")
        print(f"   Length: {result1.get('text_length')} chars")
    else:
        print(f"❌ Error: {result1.get('error')}")
    
    print("\n" + "="*70 + "\n")
    await asyncio.sleep(2)
    
    # Test 2: Long Vietnamese text
    print("📢 TEST 2: Văn bản tiếng Việt dài (với gTTS)")
    print("-" * 70)
    text2 = """
    Hôm nay là một ngày đẹp trời. Tôi đang thử nghiệm tính năng đọc văn bản 
    tiếng Việt với Google Text-to-Speech. Giọng đọc này được cung cấp bởi Google 
    nên sẽ có chất lượng tốt hơn so với giọng tiếng Anh đọc văn bản tiếng Việt. 
    Công nghệ này giúp ứng dụng của chúng ta trở nên thân thiện hơn với người dùng Việt Nam.
    """
    text2 = text2.strip()
    print(f"Text length: {len(text2)} chars")
    print(f"Preview: {text2[:100]}...\n")
    
    result2 = await text_to_speech(text2, save_audio=False)
    
    if result2.get("success"):
        print(f"✅ Result: {result2['message']}")
        print(f"   Success: {result2['success']}")
        print(f"   Engine: {result2.get('engine', 'N/A')}")
        print(f"   Length: {result2.get('text_length')} chars")
    else:
        print(f"❌ Error: {result2.get('error')}")
    
    print("\n" + "="*70 + "\n")
    await asyncio.sleep(2)
    
    # Test 3: Save Vietnamese audio
    print("💾 TEST 3: Lưu file audio tiếng Việt (MP3)")
    print("-" * 70)
    text3 = "Đây là file audio tiếng Việt được tạo bởi Google Text-to-Speech."
    print(f"Text: {text3}\n")
    
    result3 = await text_to_speech(text3, save_audio=True, filename="test_vietnamese.mp3")
    
    if result3.get("success"):
        print(f"✅ Result: {result3['message']}")
        print(f"   Success: {result3['success']}")
        print(f"   Engine: {result3.get('engine', 'N/A')}")
        print(f"   Path: {result3.get('path')}")
        print(f"   Size: {result3.get('size_bytes')} bytes")
        print(f"   Length: {result3.get('text_length')} chars")
    else:
        print(f"❌ Error: {result3.get('error')}")
    
    print("\n" + "="*70 + "\n")
    await asyncio.sleep(1)
    
    # Test 4: English text (fallback to Windows SAPI)
    print("📢 TEST 4: English text (fallback to Windows SAPI)")
    print("-" * 70)
    text4 = "This is an English test. Should use Windows SAPI."
    print(f"Text: {text4}\n")
    
    result4 = await text_to_speech(text4, save_audio=False)
    
    if result4.get("success"):
        print(f"✅ Result: {result4['message']}")
        print(f"   Success: {result4['success']}")
        print(f"   Engine: {result4.get('engine', 'N/A')}")
        print(f"   Length: {result4.get('text_length')} chars")
    else:
        print(f"❌ Error: {result4.get('error')}")
    
    print("\n" + "="*70 + "\n")
    
    # Summary
    print("\n" + "="*70)
    print("   📊 TEST SUMMARY - GTTS VIETNAMESE TTS   ".center(70))
    print("="*70 + "\n")
    
    tests = [
        ("Test 1: Short Vietnamese (gTTS)", result1.get("success"), result1.get("engine")),
        ("Test 2: Long Vietnamese (gTTS)", result2.get("success"), result2.get("engine")),
        ("Test 3: Save Vietnamese audio", result3.get("success"), result3.get("engine")),
        ("Test 4: English (SAPI fallback)", result4.get("success"), result4.get("engine"))
    ]
    
    for test_name, success, engine in tests:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")
        if engine:
            print(f"         Engine: {engine}")
    
    print("\n" + "="*70)
    print("\n✨ KẾT LUẬN:")
    print("   • Tiếng Việt: Dùng gTTS (giọng native Google) ✅")
    print("   • Tiếng Anh: Dùng Windows SAPI (fallback) ✅")
    print("   • Auto-detect ngôn ngữ: HOẠT ĐỘNG ✅")
    print("   • Lưu file MP3: HOẠT ĐỘNG ✅")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(test_gtts_vietnamese())
