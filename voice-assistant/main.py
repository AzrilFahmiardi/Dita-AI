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
import time

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
    
    if not dita_rag:
        print("\n✗ No active session. Cannot process query.")
        broadcast_client.update_state("error")
        return {"answer": "No active session", "status": "error"}
    
    if auth_client and not auth_client.validate_token():
        print("\n✗ Session expired. Please login again via dashboard.")
        broadcast_client.update_state("error")
        broadcast_client.update_response("Session expired. Please login again.")
        return {"answer": "Session expired", "status": "error"}
    
    response = dita_rag.ask(query)
    print(f"\nDita: {response['answer']}")
    print(f"Response time: {response['response_time']:.3f}s")
    print(f"Status: {response['status']}")
    
    broadcast_client.update_response(response['answer'])
    
    if use_tts:
        broadcast_client.update_state("speaking")
        print("\nDita berbicara...")
        tts.speak(response['answer'])
        
        broadcast_client.update_state("idle")
        print("Response displayed. Waiting 5 seconds before returning to listening mode...")
        time.sleep(5)
        
        broadcast_client.clear_content()
        print("Ready for next question.")
    else:
        print(f"TTS disabled. Text: {response['answer']}")
        broadcast_client.update_state("idle")
        print("Response displayed. Waiting 15 seconds before returning to listening mode...")
        time.sleep(15)
        
        broadcast_client.clear_content()
        print("Ready for next question.")
    
    return response

def main():
    global auth_client
    
    print("Dita RAG Assistant ready!")
    print("Ask me about news and current information!")
    
    from backend.broadcast_client import DASHBOARD_URL
    print(f"Dashboard available at {DASHBOARD_URL}")
    
    def on_login(user_data):
        global auth_client, dita_rag
        print(f"\n✓ User logged in: {user_data.get('full_name')} ({user_data.get('role')})")
        session_active.set()
        
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
        auth_client = DitaAuthClient(backend_url)
        auth_client.check_active_session()
        dita_rag = DitaRAGAssistant(auth_client=auth_client)
        print("✓ Context updated for new user")

    
    session_monitor = SessionMonitor(backend_url)
    session_monitor.on_login = on_login
    session_monitor.on_logout = on_logout
    session_monitor.on_switch = on_switch
    session_monitor.start()
    
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
            session_active.wait()
            
            broadcast_client.update_state("listening")
            wake_word_detected = wait_for_wake_word(stop_event=session_active)
            
            if not wake_word_detected:
                broadcast_client.update_state("paused")
                print("⏸  Wake word detection stopped. Waiting for login...")
                continue
            
            broadcast_client.update_state("wake_word_detected")
            print("Dita aktif, silakan bicara...")
            
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
            
            print(f"\nUser: {user_text}")
            
            if user_text.lower() in ["keluar", "exit", "stop"]:
                print("Dita berhenti.")
                broadcast_client.update_state("idle")
                break
            
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
