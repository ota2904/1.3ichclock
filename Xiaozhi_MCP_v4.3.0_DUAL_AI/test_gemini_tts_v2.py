"""
Test Gemini 2.5 TTS Preview
Sử dụng model gemini-2.5-flash-preview-tts để generate speech
"""
import asyncio
import os
import json
import base64
import wave
import tempfile

def get_gemini_key():
    config_file = os.path.join(os.path.dirname(__file__), 'xiaozhi_endpoints.json')
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data.get('gemini_api_key'):
                return data['gemini_api_key']
    return os.environ.get("GEMINI_API_KEY")

def play_wav_windows(wav_path):
    """Play WAV file using Windows multimedia API"""
    try:
        import winsound
        winsound.PlaySound(wav_path, winsound.SND_FILENAME)
        return True
    except Exception as e:
        print(f"⚠️ winsound error: {e}")
        return False

async def test_gemini_tts_model():
    """Test Gemini 2.5 TTS Preview model"""
    print("="*60)
    print("🎙️ Gemini 2.5 TTS Preview Test")
    print("="*60)
    
    try:
        import google.generativeai as genai
        
        api_key = get_gemini_key()
        if not api_key:
            print("❌ Không tìm thấy GEMINI_API_KEY")
            return
        
        print(f"✅ API key loaded (ends with ...{api_key[-8:]})")
        genai.configure(api_key=api_key)
        
        # Test text
        text = "Xin chào, đây là test Text to Speech của Gemini. Hệ thống miniZ MCP đang hoạt động rất tốt."
        
        print(f"\n📝 Text: {text}")
        print(f"📊 Length: {len(text)} characters")
        
        # List TTS models
        print("\n🔍 Available TTS models:")
        tts_models = []
        for model in genai.list_models():
            if 'tts' in model.name.lower():
                print(f"  • {model.name}")
                tts_models.append(model.name)
        
        if not tts_models:
            print("❌ No TTS models available")
            return
        
        # Use TTS model
        tts_model_name = 'models/gemini-2.5-flash-preview-tts'
        print(f"\n🤖 Using model: {tts_model_name}")
        
        # Create model with speech config
        model = genai.GenerativeModel(tts_model_name)
        
        # Generate speech
        print("🔊 Generating speech...")
        
        # Thử với generation config cho audio
        response = model.generate_content(
            text,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="audio/wav",  # Request audio output
            )
        )
        
        print(f"\n📦 Response type: {type(response)}")
        
        # Check response
        if response.candidates:
            print(f"📄 Candidates: {len(response.candidates)}")
            for i, candidate in enumerate(response.candidates):
                print(f"  Candidate {i}: {type(candidate)}")
                if hasattr(candidate, 'content'):
                    for j, part in enumerate(candidate.content.parts):
                        print(f"    Part {j}: {type(part)}")
                        
                        # Check for audio data
                        if hasattr(part, 'inline_data') and part.inline_data:
                            mime_type = part.inline_data.mime_type
                            data = part.inline_data.data
                            print(f"    ✅ Got audio: {mime_type}, {len(data)} bytes")
                            
                            # Save to file
                            temp_file = os.path.join(tempfile.gettempdir(), 'gemini_tts_output.wav')
                            with open(temp_file, 'wb') as f:
                                f.write(data)
                            print(f"    💾 Saved to: {temp_file}")
                            
                            # Play audio
                            print("    ▶️ Playing...")
                            play_wav_windows(temp_file)
                            print("    ✅ Done!")
                            return True
                        
                        # Check for text (fallback)
                        if hasattr(part, 'text') and part.text:
                            print(f"    📝 Text response: {part.text[:100]}...")
        
        print("⚠️ No audio data in response")
        
        # Try alternative approach with google-genai SDK
        print("\n🔄 Trying with google-genai SDK...")
        try:
            from google import genai as genai_new
            from google.genai import types
            
            client = genai_new.Client(api_key=api_key)
            
            response = client.models.generate_content(
                model=tts_model_name,
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Puck"  # Available: Puck, Charon, Kore, Fenrir, Aoede
                            )
                        )
                    )
                )
            )
            
            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        data = part.inline_data.data
                        mime_type = part.inline_data.mime_type
                        print(f"✅ Got audio from new SDK: {mime_type}, {len(data)} bytes")
                        
                        temp_file = os.path.join(tempfile.gettempdir(), 'gemini_tts_new.wav')
                        with open(temp_file, 'wb') as f:
                            f.write(data)
                        print(f"💾 Saved to: {temp_file}")
                        
                        print("▶️ Playing...")
                        play_wav_windows(temp_file)
                        print("✅ Done!")
                        return True
                        
        except ImportError:
            print("⚠️ google-genai package not installed")
            print("   Install: pip install google-genai")
        except Exception as e:
            print(f"⚠️ New SDK error: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_gtts_fallback():
    """Test gTTS as fallback"""
    print("\n" + "="*60)
    print("🔊 Testing gTTS (Google Text-to-Speech) Fallback")
    print("="*60)
    
    try:
        from gtts import gTTS
        import tempfile
        
        text = "Xin chào, đây là test Text to Speech. Hệ thống đang hoạt động tốt."
        
        print(f"📝 Text: {text}")
        
        # Generate audio
        tts = gTTS(text=text, lang='vi', slow=False)
        
        # Save to temp file
        temp_file = os.path.join(tempfile.gettempdir(), 'gtts_test.mp3')
        tts.save(temp_file)
        
        print(f"✅ Audio saved: {temp_file}")
        print(f"📊 File size: {os.path.getsize(temp_file):,} bytes")
        
        # Convert to WAV for Windows playback
        print("🔄 Converting to WAV...")
        
        # Use ffmpeg if available, otherwise use pydub
        wav_file = temp_file.replace('.mp3', '.wav')
        
        try:
            import subprocess
            result = subprocess.run(
                ['ffmpeg', '-y', '-i', temp_file, wav_file],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"✅ Converted to: {wav_file}")
                print("▶️ Playing...")
                play_wav_windows(wav_file)
                print("✅ Done!")
                return True
        except FileNotFoundError:
            print("⚠️ ffmpeg not found")
        
        # Try playing MP3 directly with Windows Media Player
        print("▶️ Trying to play MP3 with Windows...")
        try:
            os.startfile(temp_file)
            print("✅ Opened in default player")
            return True
        except:
            pass
        
        return False
        
    except ImportError:
        print("⚠️ gTTS not installed: pip install gTTS")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Gemini TTS Test Suite")
    print("="*60)
    
    # Test Gemini TTS model
    asyncio.run(test_gemini_tts_model())
    
    # Test gTTS fallback
    asyncio.run(test_gtts_fallback())
    
    print("\n" + "="*60)
    print("✅ Tests completed!")

if __name__ == "__main__":
    main()
