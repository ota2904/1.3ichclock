"""
Test Gemini TTS (Text-to-Speech)
Gemini 2.0 Flash hỗ trợ native speech synthesis
"""
import asyncio
import os
import base64

# Load API key
def get_gemini_key():
    import json
    # Try xiaozhi_endpoints.json first
    config_file = os.path.join(os.path.dirname(__file__), 'xiaozhi_endpoints.json')
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data.get('gemini_api_key'):
                return data['gemini_api_key']
    
    # Try .env file
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('GEMINI_API_KEY='):
                    return line.split('=', 1)[1].strip().strip('"\'')
    return os.environ.get("GEMINI_API_KEY")

async def test_gemini_tts():
    """Test Gemini 2.0 Flash với speech output"""
    try:
        import google.generativeai as genai
        
        api_key = get_gemini_key()
        if not api_key:
            print("❌ Không tìm thấy GEMINI_API_KEY")
            return
        
        print(f"✅ API key loaded (ends with ...{api_key[-8:]})")
        genai.configure(api_key=api_key)
        
        # Test 1: Kiểm tra models có hỗ trợ speech
        print("\n📋 Checking available models with speech support...")
        
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                if 'flash' in model.name.lower() or 'pro' in model.name.lower():
                    print(f"  • {model.name}")
        
        # Test 2: Thử generate với audio config
        print("\n🔊 Testing Gemini TTS...")
        
        text = "Xin chào, đây là test Text to Speech của Gemini. Hệ thống miniZ MCP đang hoạt động tốt."
        
        # Gemini 2.0 Flash supports multimodal output including audio
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        
        # Generate text response first
        response = model.generate_content(
            f"Đọc câu sau với giọng tự nhiên: '{text}'",
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=500
            )
        )
        
        print(f"\n📝 Gemini Response:")
        print(response.text)
        
        # Check if response has audio parts
        if hasattr(response, 'parts'):
            for part in response.parts:
                print(f"  Part type: {type(part)}")
                if hasattr(part, 'inline_data'):
                    print(f"  Has inline_data: {part.inline_data.mime_type if part.inline_data else 'None'}")
        
        # Alternative: Use gTTS as fallback for actual audio
        print("\n🔊 Generating audio with gTTS (current implementation)...")
        try:
            from gtts import gTTS
            import pygame
            
            # Create audio
            tts = gTTS(text=text, lang='vi', slow=False)
            
            # Save to temp file
            temp_file = os.path.join(os.environ.get('TEMP', '.'), 'gemini_tts_test.mp3')
            tts.save(temp_file)
            
            print(f"✅ Audio saved to: {temp_file}")
            print(f"📊 File size: {os.path.getsize(temp_file):,} bytes")
            
            # Play audio
            print("▶️ Playing audio...")
            pygame.mixer.init()
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
            
            pygame.mixer.quit()
            
            # Cleanup
            try:
                os.remove(temp_file)
            except:
                pass
            
            print("✅ Audio playback completed!")
            
        except ImportError as e:
            print(f"⚠️ Missing package: {e}")
            print("   Install: pip install gTTS pygame")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_gemini_live_api():
    """
    Test Gemini 2.0 Live API (experimental)
    Requires google-genai package (newer SDK)
    """
    print("\n" + "="*60)
    print("🎙️ Testing Gemini 2.0 Live API (Speech Synthesis)")
    print("="*60)
    
    try:
        # New SDK: google-genai (not google-generativeai)
        from google import genai
        from google.genai import types
        
        api_key = get_gemini_key()
        client = genai.Client(api_key=api_key)
        
        # Gemini 2.0 Flash supports real-time speech
        MODEL = "gemini-2.0-flash-exp"
        
        text = "Xin chào, đây là Gemini Text to Speech. Tôi có thể nói tiếng Việt."
        
        # Use generate_content with speech config
        response = client.models.generate_content(
            model=MODEL,
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],  # Request audio output
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Aoede"  # Female voice
                        )
                    )
                )
            )
        )
        
        # Check for audio in response
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    audio_data = part.inline_data.data
                    mime_type = part.inline_data.mime_type
                    print(f"✅ Received audio: {mime_type}, {len(audio_data)} bytes")
                    
                    # Save audio
                    output_file = os.path.join(os.environ.get('TEMP', '.'), 'gemini_speech.wav')
                    with open(output_file, 'wb') as f:
                        f.write(audio_data)
                    print(f"💾 Saved to: {output_file}")
                    
                    # Play with pygame
                    import pygame
                    pygame.mixer.init()
                    pygame.mixer.music.load(output_file)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        await asyncio.sleep(0.1)
                    pygame.mixer.quit()
                    
                    return True
        
        print("⚠️ No audio in response")
        return False
        
    except ImportError:
        print("⚠️ google-genai package not installed")
        print("   Install: pip install google-genai")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 Gemini TTS Test")
    print("="*60)
    
    # Test standard API
    asyncio.run(test_gemini_tts())
    
    # Test Live API (experimental)
    # asyncio.run(test_gemini_live_api())
    
    print("\n" + "="*60)
    print("✅ Test completed!")

if __name__ == "__main__":
    main()
