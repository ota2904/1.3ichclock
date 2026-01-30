"""
Test Gemini 2.5 TTS với SDK mới (google-genai)
"""
import asyncio
import os
import json
import tempfile
import base64

def get_gemini_key():
    config_file = os.path.join(os.path.dirname(__file__), 'xiaozhi_endpoints.json')
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data.get('gemini_api_key'):
                return data['gemini_api_key']
    return os.environ.get("GEMINI_API_KEY")

def play_audio_windows(file_path):
    """Play audio file using Windows"""
    try:
        if file_path.endswith('.wav'):
            import winsound
            winsound.PlaySound(file_path, winsound.SND_FILENAME)
            return True
        else:
            # Open with default player
            os.startfile(file_path)
            return True
    except Exception as e:
        print(f"⚠️ Playback error: {e}")
        return False

async def test_gemini_tts_new_sdk():
    """Test Gemini TTS với google-genai SDK mới"""
    print("="*60)
    print("🎙️ Gemini 2.5 TTS - New SDK Test")
    print("="*60)
    
    try:
        from google import genai
        from google.genai import types
        
        api_key = get_gemini_key()
        if not api_key:
            print("❌ Không tìm thấy GEMINI_API_KEY")
            return False
        
        print(f"✅ API key loaded (ends with ...{api_key[-8:]})")
        
        # Create client
        client = genai.Client(api_key=api_key)
        
        # Test text (Vietnamese)
        text = "Xin chào! Đây là test Text to Speech của Gemini. Hệ thống miniZ MCP đang hoạt động rất tốt."
        
        print(f"\n📝 Text: {text}")
        print(f"📊 Length: {len(text)} characters")
        
        # Available voices: Puck, Charon, Kore, Fenrir, Aoede
        voices = ["Puck", "Charon", "Kore", "Fenrir", "Aoede"]
        print(f"\n🎤 Available voices: {', '.join(voices)}")
        
        # Test with each voice
        voice_to_test = "Aoede"  # Female voice, good for Vietnamese
        print(f"\n🔊 Testing with voice: {voice_to_test}")
        
        # Model name
        model_name = "gemini-2.5-flash-preview-tts"
        print(f"🤖 Model: {model_name}")
        
        # Generate speech
        print("⏳ Generating speech...")
        
        response = client.models.generate_content(
            model=model_name,
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_to_test
                        )
                    )
                )
            )
        )
        
        print(f"✅ Response received!")
        
        # Extract audio
        if response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and candidate.content:
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            audio_data = part.inline_data.data
                            mime_type = part.inline_data.mime_type
                            
                            print(f"🎵 Audio: {mime_type}, {len(audio_data):,} bytes")
                            
                            # Determine file extension
                            if 'wav' in mime_type.lower():
                                ext = '.wav'
                            elif 'mp3' in mime_type.lower():
                                ext = '.mp3'
                            elif 'pcm' in mime_type.lower():
                                ext = '.wav'  # PCM can be played as WAV
                            else:
                                ext = '.wav'
                            
                            # Save to file
                            output_file = os.path.join(tempfile.gettempdir(), f'gemini_tts_{voice_to_test}{ext}')
                            
                            with open(output_file, 'wb') as f:
                                f.write(audio_data)
                            
                            print(f"💾 Saved: {output_file}")
                            print(f"📊 Size: {os.path.getsize(output_file):,} bytes")
                            
                            # Play audio
                            print("▶️ Playing audio...")
                            if play_audio_windows(output_file):
                                print("✅ Audio playback started!")
                            
                            return True
                        
                        # Check for text fallback
                        if hasattr(part, 'text') and part.text:
                            print(f"📝 Text response (no audio): {part.text[:200]}...")
        
        print("⚠️ No audio data in response")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_all_voices():
    """Test tất cả voices"""
    print("\n" + "="*60)
    print("🎤 Testing All Voices")
    print("="*60)
    
    try:
        from google import genai
        from google.genai import types
        
        api_key = get_gemini_key()
        client = genai.Client(api_key=api_key)
        
        text = "Xin chào, đây là giọng nói của tôi."
        voices = ["Puck", "Charon", "Kore", "Fenrir", "Aoede"]
        
        for voice in voices:
            print(f"\n🎤 Voice: {voice}")
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash-preview-tts",
                    contents=f"{text} Tên tôi là {voice}.",
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice
                                )
                            )
                        )
                    )
                )
                
                if response.candidates:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            data = part.inline_data.data
                            output_file = os.path.join(tempfile.gettempdir(), f'voice_{voice}.wav')
                            with open(output_file, 'wb') as f:
                                f.write(data)
                            print(f"   ✅ Saved: {output_file} ({len(data):,} bytes)")
                            
                            # Play
                            import winsound
                            winsound.PlaySound(output_file, winsound.SND_FILENAME)
                            print(f"   ▶️ Played!")
                            break
                            
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🚀 Gemini TTS Test - New SDK")
    print("="*60)
    
    # Test single voice
    asyncio.run(test_gemini_tts_new_sdk())
    
    # Uncomment to test all voices
    # asyncio.run(test_all_voices())
    
    print("\n" + "="*60)
    print("✅ Test completed!")

if __name__ == "__main__":
    main()
