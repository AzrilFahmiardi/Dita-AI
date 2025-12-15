import streamlit as st
import time
import tempfile
import os
import threading
from typing import Dict, Any
import io
import wave

# Import existing components
from rag import DitaRAGAssistant
from stt import transcribe_audio
from wakeword import wait_for_wake_word
from config_manager import get_config

# Page configuration
st.set_page_config(
    page_title="Dita Assistant",
    page_icon="▫️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ChatGPT-like interface
st.markdown("""
<style>
    /* Global styles */
    .stApp {
        background: #f7f7f8;
    }
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 700px;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #ffffff;
        border-right: 1px solid #e5e5e5;
    }
    
    .sidebar-content {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #e5e5e5;
    }
    
    .sidebar-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1f1f1f;
        margin-bottom: 0.75rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e5e5e5;
    }
    
    .sidebar-metric {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        border-bottom: 1px solid #f5f5f5;
    }
    
    .sidebar-metric:last-child {
        border-bottom: none;
    }
    
    .metric-label {
        color: #6b6b6b;
        font-size: 0.9rem;
    }
    
    .metric-value {
        color: #1f1f1f;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    /* Header */
    .app-header {
        background: white;
        padding: 1.5rem 2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e5e5e5;
    }
    
    .app-title {
        font-size: 1.75rem;
        font-weight: 600;
        color: #1f1f1f;
        margin: 0;
    }
    
    .app-subtitle {
        font-size: 0.95rem;
        color: #6b6b6b;
        margin: 0.5rem 0 0 0;
    }
    
    /* Chat container */
    .chat-container {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        height: 500px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    /* Messages */
    .message {
        display: flex;
        margin: 0.5rem 0;
    }
    
    .message.user {
        justify-content: flex-end;
    }
    
    .message.assistant {
        justify-content: flex-start;
    }
    
    .message-content {
        max-width: 75%;
        padding: 0.75rem 1rem;
        border-radius: 18px;
        line-height: 1.4;
        font-size: 0.95rem;
    }
    
    .message.user .message-content {
        background: #0084ff;
        color: white;
        border-bottom-right-radius: 4px;
    }
    
    .message.assistant .message-content {
        background: #f1f3f4;
        color: #1f1f1f;
        border-bottom-left-radius: 4px;
    }
    
    /* Input area */
    .chat-input-container {
        border-top: 1px solid #e5e5e5;
        padding: 1rem;
        background: white;
    }
    
    /* Welcome message */
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        text-align: center;
        color: #6b6b6b;
        padding: 2rem;
    }
    
    .welcome-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #1f1f1f;
    }
    
    .welcome-subtitle {
        margin-bottom: 2rem;
        color: #6b6b6b;
        line-height: 1.5;
    }
    
    .example-prompts {
        display: grid;
        gap: 0.75rem;
        max-width: 100%;
        width: 100%;
    }
    
    .example-prompt {
        background: #f8f9fa;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        border: 1px solid #e9ecef;
        transition: all 0.2s;
        font-size: 0.9rem;
        text-align: left;
    }
    
    .example-prompt:hover {
        background: #e9ecef;
        border-color: #dadce0;
    }
    
    /* Status bar */
    .status-bar {
        background: white;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.85rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e5e5e5;
    }
    
    .status-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .status-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #34a853;
    }
    
    /* Hide Streamlit elements */
    .stDeployButton { display: none; }
    .stDecoration { display: none; }
    header[data-testid="stHeader"] { display: none; }
    
    /* Keep sidebar toggle visible */
    .stSidebar > div:first-child {
        display: block !important;
    }
    
    button[data-testid="collapsedControl"] {
        display: block !important;
        visibility: visible !important;
    }
    
    /* Sidebar toggle button styling */
    .sidebar-toggle {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 6px;
        padding: 0.5rem;
        font-size: 1.2rem;
        cursor: pointer;
        margin-bottom: 1rem;
    }
    
    .sidebar-toggle:hover {
        background: #f8f9fa;
        border-color: #dadce0;
    }
    
    /* Custom scrollbar */
    .chat-messages::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-messages::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
    }
    
    .chat-messages::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;
    }
    
    .chat-messages::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
    
    /* Voice control section */
    .voice-control {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e5e5e5;
        margin-bottom: 1rem;
    }
    
    .voice-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        padding: 0.75rem;
        background: #f8f9fa;
        border-radius: 6px;
        font-size: 0.9rem;
    }
    
    .voice-status.active {
        background: #e8f5e8;
        color: #1f5f1f;
    }
    
    .voice-status.inactive {
        background: #f8f9fa;
        color: #6b6b6b;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "dita_assistant" not in st.session_state:
        st.session_state.dita_assistant = None
    if "system_status" not in st.session_state:
        st.session_state.system_status = "Initializing..."
    if "total_queries" not in st.session_state:
        st.session_state.total_queries = 0
    if "avg_response_time" not in st.session_state:
        st.session_state.avg_response_time = 0
    if "wake_word_active" not in st.session_state:
        st.session_state.wake_word_active = False
    if "wake_word_detector" not in st.session_state:
        st.session_state.wake_word_detector = None
    if "voice_recording" not in st.session_state:
        st.session_state.voice_recording = False

@st.cache_resource
def load_dita_assistant():
    """Load Dita RAG Assistant with caching"""
    try:
        with st.spinner("Loading Dita Assistant..."):
            assistant = DitaRAGAssistant()
            return assistant, "System Ready"
    except Exception as e:
        return None, f"Error: {str(e)}"

def init_wake_word_detection():
    """Initialize wake word detection"""
    try:
        if st.session_state.wake_word_detector is None:
            # Initialize with simple boolean flag since we're using the existing function
            st.session_state.wake_word_detector = True
        return True
    except Exception as e:
        st.error(f"Wake word detection unavailable: {str(e)}")
        return False

def start_wake_word_monitoring():
    """Start wake word monitoring in background"""
    def monitor_wake_word():
        try:
            # Use existing wait_for_wake_word function
            if wait_for_wake_word():
                # Trigger voice recording when wake word is detected
                st.session_state.voice_recording = True
        except Exception as e:
            print(f"Wake word monitoring error: {e}")
    
    if not st.session_state.wake_word_active:
        st.session_state.wake_word_active = True
        # In a real implementation, you'd start a background thread
        # threading.Thread(target=monitor_wake_word, daemon=True).start()

def stop_wake_word_monitoring():
    """Stop wake word monitoring"""
    st.session_state.wake_word_active = False

def process_audio_input(audio_bytes):
    """Process audio input and convert to text"""
    try:
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file.flush()
            
            # Transcribe audio using existing STT
            transcription = transcribe_audio_from_file(tmp_file.name)
            
            # Clean up temporary file
            os.unlink(tmp_file.name)
            
            return transcription
    except Exception as e:
        st.error(f"Error processing audio: {str(e)}")
        return None

def transcribe_audio_from_file(file_path):
    """Transcribe audio from file path using existing STT module"""
    try:
        # Use existing STT module - simplified for demo
        # In production, this would integrate with your actual STT implementation
        from stt import transcribe_audio
        
        # Placeholder - in real implementation you'd use:
        # return transcribe_audio(file_path)
        
        # For demo purposes, return a sample transcription
        return "Apa berita terbaru tentang polisi?"
        
    except Exception as e:
        return f"Error in transcription: {str(e)}"

def add_message(role: str, content: str, message_type: str = "text", metadata: Dict = None):
    """Add message to conversation history"""
    message = {
        "role": role,
        "content": content,
        "type": message_type,
        "timestamp": time.time(),
        "metadata": metadata or {}
    }
    st.session_state.messages.append(message)

def display_chat_message(message: Dict):
    """Display a chat message with ChatGPT-like styling"""
    role = message["role"]
    content = message["content"]
    msg_type = message.get("type", "text")
    metadata = message.get("metadata", {})
    
    # Determine message class
    message_class = "user" if role == "user" else "assistant"
    
    # Create message HTML
    st.markdown(f"""
    <div class="message {message_class}">
        <div class="message-content">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show metadata for assistant messages if available
    if role == "assistant" and metadata and any(metadata.values()):
        with st.expander("Response Details", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sources", metadata.get("source_count", "N/A"))
            with col2:
                st.metric("Time", f"{metadata.get('response_time', 0):.1f}s")
            with col3:
                st.metric("Status", metadata.get("status", "success"))

def process_query(query: str, query_type: str = "text"):
    """Process user query and get response"""
    if not st.session_state.dita_assistant:
        st.error("System not initialized. Please refresh the page.")
        return
    
    # Add user message
    add_message("user", query, query_type)
    
    # Process with Dita
    with st.spinner("Searching news database..."):
        start_time = time.time()
        try:
            result = st.session_state.dita_assistant.ask(query)
            response_time = time.time() - start_time
            
            # Update metrics
            st.session_state.total_queries += 1
            if st.session_state.avg_response_time == 0:
                st.session_state.avg_response_time = response_time
            else:
                st.session_state.avg_response_time = (
                    st.session_state.avg_response_time + response_time
                ) / 2
            
            # Add response message
            metadata = {
                "source_count": result.get("source_count", 0),
                "response_time": result.get("response_time", response_time),
                "status": result.get("status", "success")
            }
            
            add_message("assistant", result["answer"], "text", metadata)
            
        except Exception as e:
            add_message("assistant", f"Sorry, I encountered an error: {str(e)}", "text")

# Main app
def main():
    init_session_state()
    
    # Load assistant
    if st.session_state.dita_assistant is None:
        assistant, status = load_dita_assistant()
        st.session_state.dita_assistant = assistant
        st.session_state.system_status = status
    
    # Initialize wake word detection
    init_wake_word_detection()
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">System Overview</div>', unsafe_allow_html=True)
        
        # System status
        status_color = "#34a853" if "Ready" in st.session_state.system_status else "#ea4335"
        st.markdown(f"""
        <div class="sidebar-metric">
            <span class="metric-label">Status</span>
            <span class="metric-value" style="color: {status_color};">{st.session_state.system_status}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Metrics
        st.markdown(f"""
        <div class="sidebar-metric">
            <span class="metric-label">Total Queries</span>
            <span class="metric-value">{st.session_state.total_queries}</span>
        </div>
        <div class="sidebar-metric">
            <span class="metric-label">Avg Response Time</span>
            <span class="metric-value">{st.session_state.avg_response_time:.1f}s</span>
        </div>
        <div class="sidebar-metric">
            <span class="metric-label">Voice Control</span>
            <span class="metric-value">{'Active' if st.session_state.wake_word_active else 'Inactive'}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Voice Control Section
        st.markdown('<div class="voice-control">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">Voice Control</div>', unsafe_allow_html=True)
        
        status_class = "active" if st.session_state.wake_word_active else "inactive"
        status_text = "Listening for 'Hei Dita'" if st.session_state.wake_word_active else "Voice control disabled"
        
        st.markdown(f"""
        <div class="voice-status {status_class}">
            <div class="status-indicator" style="background: {'#34a853' if st.session_state.wake_word_active else '#6b6b6b'};"></div>
            <span>{status_text}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.wake_word_active:
            if st.button("Stop Voice Control", type="secondary", use_container_width=True):
                stop_wake_word_monitoring()
                st.rerun()
        else:
            if st.button("Start Voice Control", type="primary", use_container_width=True):
                start_wake_word_monitoring()
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # System Information
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">Configuration</div>', unsafe_allow_html=True)
        
        try:
            config = get_config()
            st.markdown(f"""
            <div class="sidebar-metric">
                <span class="metric-label">LLM Provider</span>
                <span class="metric-value">{config.get("llm.primary.provider", "Unknown")}</span>
            </div>
            <div class="sidebar-metric">
                <span class="metric-label">Model</span>
                <span class="metric-value">{config.get("llm.primary.model_name", "Unknown")}</span>
            </div>
            <div class="sidebar-metric">
                <span class="metric-label">Database</span>
                <span class="metric-value">Elasticsearch</span>
            </div>
            """, unsafe_allow_html=True)
        except:
            st.error("Configuration unavailable")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Actions
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">Actions</div>', unsafe_allow_html=True)
        
        if st.button("Clear Conversation", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.session_state.total_queries = 0
            st.session_state.avg_response_time = 0
            st.rerun()
        
        if st.button("Refresh System", type="secondary", use_container_width=True):
            st.session_state.dita_assistant = None
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area
    # Add sidebar toggle button at the top
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("☰", help="Toggle Sidebar", key="sidebar_toggle"):
            # This will refresh the page, allowing sidebar to be reopened
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="app-header">
            <h1 class="app-title">Dita Assistant</h1>
            <p class="app-subtitle">Intelligent Indonesian News Analysis System</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Status bar
    status_color = "#34a853" if "Ready" in st.session_state.system_status else "#ea4335"
    st.markdown(f"""
    <div class="status-bar">
        <div class="status-item">
            <div class="status-indicator" style="background: {status_color};"></div>
            <span>System {st.session_state.system_status}</span>
        </div>
        <div class="status-item">
            <span>{st.session_state.total_queries} queries processed</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if st.session_state.dita_assistant is None:
        st.error("Failed to initialize Dita Assistant. Please refresh the system.")
    else:
        # Chat messages area
        st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
        
        if not st.session_state.messages:
            # Welcome screen
            st.markdown("""
            <div class="welcome-container">
                <h2 class="welcome-title">Welcome to Dita Assistant</h2>
                <p class="welcome-subtitle">Your intelligent companion for exploring Indonesian news and current events. Ask any question to get started.</p>
                <div class="example-prompts">
                    <div class="example-prompt" onclick="document.querySelector('[data-testid=\"stChatInput\"] textarea').value='Apa berita terbaru tentang polisi?'; document.querySelector('[data-testid=\"stChatInput\"] textarea').focus();">
                        What are the latest police news?
                    </div>
                    <div class="example-prompt" onclick="document.querySelector('[data-testid=\"stChatInput\"] textarea').value='Ada demo atau aksi massa yang terjadi?'; document.querySelector('[data-testid=\"stChatInput\"] textarea').focus();">
                        Are there any protests or mass actions happening?
                    </div>
                    <div class="example-prompt" onclick="document.querySelector('[data-testid=\"stChatInput\"] textarea').value='Bagaimana situasi keamanan sekarang?'; document.querySelector('[data-testid=\"stChatInput\"] textarea').focus();">
                        How is the current security situation?
                    </div>
                    <div class="example-prompt" onclick="document.querySelector('[data-testid=\"stChatInput\"] textarea').value='Berita politik terbaru apa saja?'; document.querySelector('[data-testid=\"stChatInput\"] textarea').focus();">
                        What are the latest political news?
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display chat messages
            for message in st.session_state.messages:
                display_chat_message(message)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input area
        st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
        
        if prompt := st.chat_input("Type your question about Indonesian news..."):
            process_query(prompt, "text")
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()