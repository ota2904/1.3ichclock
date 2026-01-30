"""
Test Gemini 3.0 Flash API
"""
import os
import google.generativeai as genai

# Configure API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAEYz5uP2pS6rXs10K0m1Ls6P1z8iC8nPQyg")
genai.configure(api_key=GEMINI_API_KEY)

print("🧪 Testing Gemini 3.0 Flash...")
print(f"📋 API Key: {GEMINI_API_KEY[-10:]}")

try:
    # Test với model 3.0-flash
    model = genai.GenerativeModel('models/gemini-3.0-flash')
    print(f"✅ Model initialized: {model.model_name}")
    
    # Simple test
    response = model.generate_content("Hello! What model are you?")
    print(f"\n📝 Response:\n{response.text}")
    
    # Check usage metadata
    if hasattr(response, 'usage_metadata'):
        print(f"\n📊 Token usage:")
        print(f"   Prompt: {response.usage_metadata.prompt_token_count}")
        print(f"   Response: {response.usage_metadata.candidates_token_count}")
        print(f"   Total: {response.usage_metadata.total_token_count}")
    
    print("\n✅ Gemini 3.0 Flash hoạt động HOÀN HẢO!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"   Type: {type(e).__name__}")
