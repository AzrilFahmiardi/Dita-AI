from wakeword import wait_for_wake_word
from stt import transcribe_audio
from rag import DitaRAGAssistant
from vad_recorder import VoiceActivityRecorder
from tts import DitaTTS
from config_manager import get_vad_config, get_tts_config, get_config
from auth import authenticate_terminal_user, DitaAuthClient
from session_monitor import SessionMonitor
import sys
import os
import threading

# Import broadcast_client from sibling backend directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
try:
    from broadcast_client import broadcast_client
except ImportError:
    print("Warning: broadcast_client not available")
    broadcast_client = None

print("Initializing Dita...")

# Global state
session_active = threading.Event()
auth_client = None
dita_rag = None

# Initialize authentication
auth_config = get_config().get('auth', {})
auth_required = auth_config.get('required', True)
backend_url = auth_config.get('backend_url', 'http://localhost:8000')

# Don't prompt for login - wait for frontend session
if auth_required:
    print("\nAuthentication: Monitoring frontend sessions")
    print("Please login via dashboard at http://localhost:5173")
    auth_client = DitaAuthClient(backend_url)
    
    # Check if already logged in
    active_session = auth_client.check_active_session()
    if active_session:
        session_active.set()
        dita_rag = DitaRAGAssistant(auth_client=auth_client)
    else:
        print("⏸  Waiting for login...")
else:
    print("\n⚠ Authentication disabled (running in demo mode)")
    dita_rag = DitaRAGAssistant(auth_client=None)
    session_active.set()

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
    global dita_rag
    
    # Check if RAG is initialized (user logged in)
    if not dita_rag:
        print("\n✗ No active session. Cannot process query.")
        broadcast_client.update_state("error")
        return {"answer": "No active session", "status": "error"}
    
    # Check token validity before processing
    if auth_client and not auth_client.validate_token():
        print("\n✗ Session expired. Please login again via dashboard.")
        broadcast_client.update_state("error")
        broadcast_client.update_response("Session expired. Please login again.")
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
    global auth_client
    
    print("Dita RAG Assistant ready!")
    print("Ask me about news and current information!")
    
    # Get dashboard URL from broadcast_client
    from backend.broadcast_client import DASHBOARD_URL
    print(f"Dashboard available at {DASHBOARD_URL}")
    
    # Setup session monitoring callbacks
    def on_login(user_data):
        global auth_client, dita_rag
        print(f"\n✓ User logged in: {user_data.get('full_name')} ({user_data.get('role')})")
        session_active.set()
        
        # Reinitialize auth client and RAG with active session
        auth_client = DitaAuthClient(backend_url)
        auth_client.check_active_session()
        dita_rag = DitaRAGAssistant(auth_client=auth_client)
        
        broadcast_client.update_state("listening")
        print("🎙️  Dita is now listening for wake word...")
    
    def on_logout(user_data):
        global auth_client, dita_rag
        print(f"\n✗ User logged out: {user_data.get('username')}")
        session_active.clear()
        auth_client = None
        dita_rag = None
        broadcast_client.update_state("paused")
        print("⏸  Dita paused. Waiting for login...")
    
    def on_switch(user_data):
        global auth_client, dita_rag
        print(f"\n↻ User switched: {user_data.get('full_name')} ({user_data.get('role')})")
        # Update auth client and RAG with new session
        auth_client = DitaAuthClient(backend_url)
        auth_client.check_active_session()
        dita_rag = DitaRAGAssistant(auth_client=auth_client)
        print("✓ Context updated for new user")

    
    # Start session monitor
    session_monitor = SessionMonitor(backend_url)
    session_monitor.on_login = on_login
    session_monitor.on_logout = on_logout
    session_monitor.on_switch = on_switch
    session_monitor.start()
    
    # Check initial state
    if session_active.is_set():
        print(f"\n✓ Active session detected!")
        print(f"Welcome, {auth_client.user_context['full_name']}!")
        print(f"Role: {auth_client.user_context['role']['name']}")
        print("🎙️  Dita is listening for wake word...")
        broadcast_client.update_state("listening")
    else:
        print("\n⏸  No active session. Waiting for login from dashboard...")
        broadcast_client.update_state("paused")
    
    try:
        while True:
            # Wait for active session
            session_active.wait()
            
            # State: Listening for wake word
            broadcast_client.update_state("listening")
            wake_word_detected = wait_for_wake_word(stop_event=session_active)
            
            # If wake word detection was stopped (logout), restart loop
            if not wake_word_detected:
                broadcast_client.update_state("paused")
                print("⏸  Wake word detection stopped. Waiting for login...")
                continue
            
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
        session_monitor.stop()
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
