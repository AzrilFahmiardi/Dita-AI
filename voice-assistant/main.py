from wakeword import wait_for_wake_word
from stt import transcribe_audio
from rag import DitaRAGAssistant
from vad_recorder import VoiceActivityRecorder
from tts import DitaTTS
from config_manager import get_vad_config, get_tts_config, get_config
from auth import authenticate_terminal_user, DitaAuthClient
import sys
import os

# Import broadcast_client from sibling backend directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
try:
    from broadcast_client import broadcast_client
except ImportError:
    print("Warning: broadcast_client not available")
    broadcast_client = None

print("Initializing Dita...")

# Initialize authentication
auth_config = get_config().get('auth', {})
auth_required = auth_config.get('required', True)
backend_url = auth_config.get('backend_url', 'http://localhost:8000')

auth_client = None
if auth_required:
    print("\nAuthentication required for Dita Voice Assistant")
    auth_client = authenticate_terminal_user(backend_url)
    
    if not auth_client:
        print("\n✗ Authentication failed. Exiting...")
        sys.exit(1)
    
    print(f"\nWelcome, {auth_client.user_context['full_name']}!")
    print(f"Role: {auth_client.user_context['role']['name']}")
else:
    print("\n⚠ Authentication disabled (running in demo mode)")

dita_rag = DitaRAGAssistant(auth_client=auth_client)

vad_config = get_vad_config()
use_vad = vad_config.get('enabled', False)

tts_config = get_tts_config()
use_tts = tts_config.get('enabled', False)

if use_vad:
    print("Voice Activity Detection enabled")
    recorder = VoiceActivityRecorder()

if use_tts:
    print("Text-to-Speech enabled")
    tts = DitaTTS()

def run_rag(query):
    """Process query using RAG assistant"""
    # Check token validity before processing
    if auth_client and not auth_client.validate_token():
        print("\n✗ Session expired. Please restart Dita and login again.")
        broadcast_client.update_state("error")
        broadcast_client.update_response("Session expired. Please restart and login again.")
        return {"answer": "Session expired", "status": "error"}
    
    response = dita_rag.ask(query)
    print(f"\nDita: {response['answer']}")
    print(f"Response time: {response['response_time']:.3f}s")
    print(f"Status: {response['status']}")
    
    # Broadcast response
    broadcast_client.update_response(response['answer'])
    
    if use_tts:
        # State: Speaking
        broadcast_client.update_state("speaking")
        print("\nDita berbicara...")
        tts.speak(response['answer'])
        
        # Back to idle after speaking
        broadcast_client.update_state("idle")
        broadcast_client.clear_content()
    else:
        # Back to idle if no TTS
        broadcast_client.update_state("idle")
        broadcast_client.clear_content()
    
    return response

def main():
    print("Dita RAG Assistant ready!")
    print("Ask me about news and current information!")
    
    # Get dashboard URL from broadcast_client
    from backend.broadcast_client import DASHBOARD_URL
    print(f"Dashboard available at {DASHBOARD_URL}")
    
    try:
        # Set idle state at start
        broadcast_client.update_state("idle")
        
        while True:
            # State: Listening for wake word
            broadcast_client.update_state("listening")
            wait_for_wake_word()
            
            # State: Wake word detected
            broadcast_client.update_state("wake_word_detected")
            print("Dita aktif, silakan bicara...")
            
            # State: Recording
            broadcast_client.update_state("recording")
            if use_vad:
                audio_buffer = recorder.record()
                user_text = transcribe_audio(audio_buffer=audio_buffer)
            else:
                user_text = transcribe_audio(duration=5)
            
            if user_text.strip() == "":
                print("Tidak mendengar dengan jelas.")
                broadcast_client.update_state("idle")
                continue
            
            # Broadcast transcription
            broadcast_client.update_transcript(user_text)
            
            if user_text.lower() in ["keluar", "exit", "stop"]:
                print("Dita berhenti.")
                broadcast_client.update_state("idle")
                break
            
            # State: Processing with RAG
            broadcast_client.update_state("processing")
            run_rag(user_text)
    except KeyboardInterrupt:
        print("\n\nShutting down Dita...")
        if auth_client:
            print("Logging out...")
            auth_client.logout()
    finally:
        if use_vad:
            recorder.close()
        if use_tts:
            tts.close()

if __name__ == "__main__":
    main()
