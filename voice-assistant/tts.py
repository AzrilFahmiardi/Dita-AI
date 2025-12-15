import os
import io
import wave
import pyaudio
from google.cloud import texttospeech
from config_manager import ConfigManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DitaTTS:
    def __init__(self):
        # Check environment variable first (highest priority)
        disable_tts_env = os.getenv('DISABLE_TTS', 'false').lower() == 'true'
        
        if disable_tts_env:
            print("TTS is DISABLED via DISABLE_TTS environment variable")
            print("   No Google Cloud API calls will be made")
            self.enabled = False
            return
        
        config = ConfigManager()
        tts_config = config.get_tts_config()
        
        self.enabled = tts_config.get('enabled', True)
        
        if not self.enabled:
            print("TTS is disabled in configuration")
            return
        
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not credentials_path:
            print("Warning: GOOGLE_APPLICATION_CREDENTIALS not set")
            print("TTS will be disabled. See SETUP_GOOGLE_CLOUD_TTS.md")
            self.enabled = False
            return
        
        if not os.path.exists(credentials_path):
            print(f"Error: Credentials file not found: {credentials_path}")
            self.enabled = False
            return
        
        try:
            self.client = texttospeech.TextToSpeechClient()
            
            language_code = tts_config.get('language_code', 'id-ID')
            voice_name = tts_config.get('voice_name', 'id-ID-Standard-B')
            
            self.voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name,
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            
            self.audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                speaking_rate=tts_config.get('speaking_rate', 1.0),
                pitch=tts_config.get('pitch', 0.0),
                sample_rate_hertz=16000
            )
            
            self.audio_interface = pyaudio.PyAudio()
            
            print("✅ Google Cloud TTS initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Google Cloud TTS: {e}")
            self.enabled = False
    
    def speak(self, text: str, save_path: str = None) -> bool:
        if not self.enabled:
            print(f"TTS disabled. Text: {text}")
            return False
        
        if not text or not text.strip():
            print("Warning: Empty text provided to TTS")
            return False
        
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            print("Synthesizing speech...")
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice,
                audio_config=self.audio_config
            )
            
            if save_path:
                with open(save_path, 'wb') as out:
                    out.write(response.audio_content)
                print(f"Audio saved to: {save_path}")
            
            self._play_audio(response.audio_content)
            
            return True
            
        except Exception as e:
            print(f"TTS error: {e}")
            return False
    
    def _play_audio(self, audio_content: bytes):
        try:
            audio_stream = io.BytesIO(audio_content)
            
            with wave.open(audio_stream, 'rb') as wf:
                stream = self.audio_interface.open(
                    format=self.audio_interface.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                
                chunk_size = 1024
                data = wf.readframes(chunk_size)
                
                while data:
                    stream.write(data)
                    data = wf.readframes(chunk_size)
                
                stream.stop_stream()
                stream.close()
                
        except Exception as e:
            print(f"Audio playback error: {e}")
    
    def close(self):
        if hasattr(self, 'audio_interface'):
            self.audio_interface.terminate()
    
    def __del__(self):
        self.close()
