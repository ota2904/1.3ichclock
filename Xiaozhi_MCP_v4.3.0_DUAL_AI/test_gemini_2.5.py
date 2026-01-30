"""
Test Gemini 2.5 Flash
"""
import os
import asyncio
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the ask_gemini function
async def test_gemini():
    print("=" * 70)
    print("🧪 TEST GEMINI 2.5 FLASH")
    print("=" * 70)
    print()
    
    # Check if API key is set
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        print("❌ GEMINI_API_KEY chưa được set!")
        print()
        print("Hãy set API key trước:")
        print("   set GEMINI_API_KEY=your_api_key_here")
        print()
        print("Lấy API key tại: https://aistudio.google.com/apikey")
        return
    
    print(f"✅ API Key: ...{api_key[-8:]}")
    print()
    
    # Test với prompt đơn giản
    test_prompt = "Hello! What is 2+2? Answer in one short sentence."
    
    print(f"📝 Test prompt: {test_prompt}")
    print()
    print("⏳ Đang gọi Gemini 2.5 Flash...")
    print()
    
    try:
        # Import function from xiaozhi_final
        import importlib.util
        spec = importlib.util.spec_from_file_location("xiaozhi", "xiaozhi_final.py")
        xiaozhi = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(xiaozhi)
        
        # Call ask_gemini with default model (2.5-flash)
        result = await xiaozhi.ask_gemini(test_prompt)
        
        print("=" * 70)
        print("📊 KẾT QUẢ")
        print("=" * 70)
        print()
        
        if result.get("success"):
            print(f"✅ Status: SUCCESS")
            print(f"🤖 Model: {result.get('model', 'N/A')}")
            print(f"💬 Response: {result.get('response_text', 'N/A')[:200]}")
            print()
            print("=" * 70)
            print("🎉 GEMINI 2.5 FLASH HOẠT ĐỘNG HOÀN HẢO!")
            print("=" * 70)
        else:
            print(f"❌ Status: FAILED")
            print(f"⚠️  Error: {result.get('error', 'Unknown error')}")
            print()
            if "404" in str(result.get('error', '')):
                print("💡 Lỗi 404 - Model không tồn tại!")
                print("   Có thể API chưa có gemini-2.5-flash")
                print("   Thử dùng: models/gemini-2.0-flash-exp")
            
    except Exception as e:
        print("=" * 70)
        print("❌ LỖI KHI TEST")
        print("=" * 70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini())
