"""
Check available Gemini models
"""
import os
import google.generativeai as genai

# Configure with your API key
api_key = os.getenv("GEMINI_API_KEY", "")
if not api_key:
    print("⚠️  Set GEMINI_API_KEY environment variable first!")
    print("   Example: set GEMINI_API_KEY=your_key_here")
    exit(1)

genai.configure(api_key=api_key)

print("=" * 70)
print("📋 Available Gemini Models for generateContent")
print("=" * 70)
print()

models = genai.list_models()
content_models = [m for m in models if 'generateContent' in m.supported_generation_methods]

for i, model in enumerate(content_models, 1):
    print(f"{i}. {model.name}")
    if hasattr(model, 'display_name'):
        print(f"   Display: {model.display_name}")
    if hasattr(model, 'description'):
        print(f"   Desc: {model.description[:100] if model.description else 'N/A'}")
    print()

print("=" * 70)
print(f"Total: {len(content_models)} models")
print("=" * 70)
