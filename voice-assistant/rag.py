import os
import time
import json
from typing import Dict, Any, List, Optional, Annotated

# Configuration management
from config_manager import get_api_key, get_model_config

# Elasticsearch integration
from elasticsearch_news import ElasticsearchNewsRAG

# Fonnte WhatsApp client
from fonnte_client import FontteClient

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# LangChain core
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_message_histories import ChatMessageHistory

# LangChain agent
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# Google Generative AI for fallback
import google.genai as genai


class LangChainConversationMemory:
    """
    Memory Implementation - conversation management
    """
    
    def __init__(self, max_messages: int = 10):
        self.messages: List[BaseMessage] = []
        self.max_messages = max_messages
        self.chat_history = ChatMessageHistory()
    
    def add_user_message(self, message: str):
        """Add user message to conversation history"""
        human_msg = HumanMessage(content=message)
        self.messages.append(human_msg)
        self.chat_history.add_user_message(message)
        self._trim_messages()
    
    def add_ai_message(self, message: str):
        """Add AI response to conversation history"""
        ai_msg = AIMessage(content=message)
        self.messages.append(ai_msg)
        self.chat_history.add_ai_message(message)
        self._trim_messages()
    
    def _trim_messages(self):
        """Keep only last max_messages for efficiency"""
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_conversation_context(self) -> str:
        """Get formatted conversation context for prompt"""
        if not self.messages:
            return ""
        
        context = []
        for msg in self.messages[-6:]:  # Last 3 conversations (6 messages)
            if isinstance(msg, HumanMessage):
                context.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                context.append(f"Assistant: {msg.content}")
        
        return "\n".join(context)
    
    def clear_history(self):
        """Clear conversation history"""
        self.messages.clear()
        self.chat_history.clear()
    
    def get_message_count(self) -> int:
        """Get total message count"""
        return len(self.messages)


class DitaRAGAssistant:
    def __init__(self, auth_client=None, user_context=None, access_token=None):
        print("\n" + "="*60)
        print("Initializing Dita RAG Assistant with Agent System")
        print("="*60)
        
        # Store authentication info
        self.auth_client = auth_client
        self.user_context = user_context
        self.access_token = access_token
        
        # If user_context provided directly, use it
        if user_context:
            self.user_id = user_context['id']
            self.user_role = user_context['role']
            print(f"✓ User context loaded: {user_context['username']} ({user_context['role']['name']})")
        elif auth_client:
            user_info = auth_client.get_user_context()
            self.user_context = user_info
            self.user_id = user_info['id']
            self.user_role = user_info['role']
            self.access_token = auth_client.access_token
            print(f"✓ User context from auth_client: {user_info['username']} ({user_info['role']['name']})")
        else:
            # No authentication (legacy mode)
            self.user_context = None
            self.user_id = None
            self.user_role = None
            self.access_token = None
            print("⚠ Running without authentication")
        
        # Setup components
        self._setup_elasticsearch()
        self._setup_llm()
        self._setup_memory()
        
        # Conversation context tracking
        self.recent_articles_cache = []
        self.conversation_articles = []  
        self.last_query = ""
        self.last_query_time = 0
        self.last_response = ""
        
        # WhatsApp content storage
        self.saved_recommendation = ""  # Saved content for WhatsApp sending
        self.saved_news_summary = ""    # Saved news summary
        
        # Track index untuk WhatsApp message
        self.last_news_fetch_index = -1  
        self.context_answer = ""  
        
        # Initialize Fonnte client before agent setup
        try:
            self.fonnte_client = FontteClient()
            print("Fonnte WhatsApp client initialized")
        except Exception as e:
            print(f"Warning: Fonnte client not available: {e}")
            self.fonnte_client = None
        
        # Setup agent 
        self._setup_agent()
        
        print("Agent-based RAG Assistant ready!\n")
        
    
    def _setup_elasticsearch(self):
        """Setup data source integration"""        
        try:
            self.news_rag = ElasticsearchNewsRAG()
            
            if not self.news_rag.es_available:
                print("Data source connection failed")
                raise Exception("Data source connection failed")
                
        except Exception as e:
            print(f"Data source setup failed: {e}")
            raise
    
    def _setup_llm(self):
        try:
            from config_manager import get_config
            config = get_config()
            llm_config = config.get_model_config('primary')
            
            # Abstracted LLM creation based on provider
            self.langchain_llm = self._create_llm(llm_config)
            self.fallback_config = config.get_model_config('fallback')
            
            # ========== SINGLE UNIFIED SMART PROMPT ==========
            self.rag_prompt_template = PromptTemplate(
                input_variables=["context", "question", "conversation_history"],
                template="""Anda adalah Dita, asisten AI untuk berita Indonesia.

    PERCAKAPAN SEBELUMNYA:
    {conversation_history}

    BERITA TERKINI:
    {context}

    PERTANYAAN USER: {question}

    INSTRUKSI UTAMA:
    - Jawab dalam bentuk NARASI yang natural dan mengalir seperti berbicara
    - Jawaban harus RINGKAS dan TO THE POINT (2-4 kalimat)
    - JANGAN PERNAH gunakan formatting markdown, bullet points, asterisk, atau numbering
    - Gunakan bahasa percakapan natural
    - Sertakan sumber berita: "Menurut [sumber] tanggal [tanggal]..."

    KLASIFIKASI PERTANYAAN & CARA MENJAWAB:

    1. JIKA user bertanya tentang SITUASI/KEJADIAN/PERISTIWA (apa yang terjadi, bagaimana kronologi, dll):
    → Jawab dengan FAKTA dari berita: apa, kapan, dimana, siapa terlibat
    → JANGAN tambahkan opini atau rekomendasi
    → Contoh: "Menurut Republika tanggal 5 Desember, terjadi banjir di Jakarta Timur akibat hujan deras sejak kemarin malam. Lima kelurahan terdampak dengan ketinggian air mencapai 80 sentimeter."

    2. JIKA user bertanya tentang TINDAKAN PEJABAT/PEMERINTAH/APARAT (apa yang dilakukan, langkah yang diambil, dll):
    → CEK DULU: Apakah berita BENAR-BENAR menyebutkan tindakan konkret pejabat?
    → Jika ADA: Sebutkan tindakan faktual dari berita
    → Jika TIDAK ADA atau TIDAK JELAS: Katakan "Belum ada informasi tentang tindakan pejabat dalam berita yang saya akses saat ini"
    → JANGAN mengarang atau mengasumsikan tindakan yang tidak disebutkan
    → Contoh (ada info): "Berdasarkan Kompas tanggal 5 Desember, Gubernur DKI Jakarta telah menerjunkan 50 pompa air dan membuka 10 posko pengungsian untuk menangani banjir."
    → Contoh (tidak ada info): "Belum ada informasi tentang tindakan pejabat terkait kasus ini dalam berita yang saya akses saat ini."

    3. JIKA user meminta REKOMENDASI/SARAN/SOLUSI (sebaiknya bagaimana, apa yang bisa dilakukan, dll):
    → Berikan rekomendasi berdasarkan KONTEKS situasi yang ada di berita
    → Struktur: (1) Ringkas situasi, (2) Saran logis 2-3 hal, (3) Penutup
    → Gunakan kata: "Berdasarkan situasi ini, beberapa hal yang bisa dilakukan adalah..."
    → JANGAN buat rekomendasi tidak realistis atau di luar konteks
    → Jika konteks tidak cukup: "Untuk memberikan rekomendasi yang tepat, perlu informasi lebih detail tentang [aspek]"
    → Contoh: "Mengingat banjir sudah mencapai 80 sentimeter di lima kelurahan, prioritas adalah memastikan evakuasi warga ke tempat aman dan menyiapkan logistik bantuan. Koordinasi dengan pihak terkait untuk pembuangan air juga penting. Untuk jangka panjang, perlu evaluasi sistem drainase."

    4. JIKA pertanyaan UMUM atau FOLLOW-UP:
    → Jawab sesuai konteks percakapan dan berita
    → Tetap faktual dan natural

    INSTRUKSI KHUSUS - SAVE CONTENT FOR WHATSAPP:
    
    Setelah memberikan REKOMENDASI, SARAN, atau ANALISIS penting:
    - WAJIB panggil tool save_recommendation untuk menyimpan konten
    - Parameter content: isi rekomendasi/analisis yang baru saja kamu generate
    - Parameter content_type: "recommendation" untuk saran, "summary" untuk rangkuman, "analysis" untuk analisis
    
    Kapan WAJIB save:
    - User minta rekomendasi/saran → SAVE DUA KALI:
      1. save_recommendation(content="[ringkasan berita]", content_type="summary")
      2. save_recommendation(content="[rekomendasi lengkap]", content_type="recommendation")
    - User minta rangkuman berita → save_recommendation(content="...", content_type="summary")
    - User minta analisis situasi → save_recommendation(content="...", content_type="analysis")
    
    Mengapa save dua kali untuk rekomendasi?
    - WhatsApp message perlu konteks berita (summary) DAN rekomendasi
    - Jadi save summary dulu, baru save recommendation
    
    Tool save_recommendation akan menyimpan konten sehingga ketika user minta "kirim ke WhatsApp",
    konten yang tersimpan inilah yang akan dikirim (bukan menebak dari conversation).

    INSTRUKSI KHUSUS - WHATSAPP CONTACT SELECTION:
    
    Jika user meminta kirim ke WhatsApp:
    - Jika user TIDAK SEBUTKAN NAMA KONTAK: Panggil tool dengan parameter kosong → tool akan tampilkan daftar kontak
    - Jika user SEBUTKAN NAMA KONTAK: Ekstrak nama kontaknya dan panggil tool dengan parameter nama
      Contoh: "kirim ke Grup Keluarga" → contact_name="Grup Keluarga"
              "kirim ke semua kontak" → contact_name="semua"
              "kirim ke Emergency Contact dan Tim Operasional" → panggil tool dua kali terpisah
    - Jika tool return "awaiting_selection": Tunjukkan daftar ke user dan tunggu pilihan
    - Jika tool return "error": SAMPAIKAN ERROR MESSAGE PERSIS DARI TOOL, JANGAN INTERPRETASI ULANG
      * Tool sudah memberikan error message yang tepat (misal: "Maaf, Anda (...) tidak memiliki akses...")
      * JANGAN ubah "Anda" menjadi "saya" atau "akun saya"
      * Sampaikan PERSIS seperti yang tool berikan
    - Jika tool return "success": Konfirmasi ke user bahwa pesan berhasil dikirim

    ATURAN KETAT:
    - Jika berita TIDAK RELEVAN dengan pertanyaan: "Maaf, informasi tentang [topik] belum tersedia dalam berita yang saya akses"
    - Jika pertanyaan tentang pejabat tapi berita tidak menyebut tindakan pejabat: WAJIB bilang "Belum ada informasi"
    - JANGAN menambahkan informasi di luar berita yang diberikan
    - JANGAN menggunakan format list, bullet, atau numbering dalam jawaban

    JAWABAN:"""
            )
                
        except Exception as e:
            print(f"Language model setup failed: {e}")
            raise
    
    def _create_llm(self, llm_config: Dict[str, Any]):
        """Factory method to create LLM based on provider - ABSTRACTED"""
        provider = llm_config['provider']
        api_key = get_api_key(llm_config['api_key_name'])
        
        if not api_key:
            raise ValueError(f"API key for {llm_config['api_key_name']} not found")
            
        if provider == "google_gemini":
            return ChatGoogleGenerativeAI(
                model=llm_config['model_name'],
                google_api_key=api_key,
                temperature=llm_config['temperature'],
                max_tokens=llm_config['max_tokens'],
                timeout=llm_config.get('timeout', 30),
                convert_system_message_to_human=True
            )
        elif provider == "openai":
            try:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model=llm_config['model_name'],
                    openai_api_key=api_key,
                    temperature=llm_config['temperature'],
                    max_tokens=llm_config['max_tokens'],
                    timeout=llm_config.get('timeout', 30)
                )
            except ImportError:
                raise ImportError("langchain_openai not installed. Install with: pip install langchain-openai")
        elif provider == "anthropic":
            try:
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(
                    model=llm_config['model_name'],
                    anthropic_api_key=api_key,
                    temperature=llm_config['temperature'],
                    max_tokens=llm_config['max_tokens']
                )
            except ImportError:
                raise ImportError("langchain_anthropic not installed. Install with: pip install langchain-anthropic")
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def _setup_memory(self):
        """Setup conversation memory"""
        self.memory = LangChainConversationMemory()
    
    def _setup_agent(self):
        """Setup LangChain agent with tools"""
        print("Setting up agent with tools...")
        
        # Define tools for the agent
        @tool
        def search_news(query: str, time_filter: Optional[str] = None) -> str:
            """
            Search for news articles in Elasticsearch database.
            
            Args:
                query: Search query for news (e.g., "banjir jakarta", "kebijakan pemerintah")
                time_filter: Optional time filter - "today", "week", "month", or None for all time
            
            Returns:
                JSON string containing news articles with headline, summary, date, and source
            """
            print(f"[TOOL] search_news called: query='{query}', time_filter={time_filter}")
            
            try:
                articles = self.news_rag.search_news(query)
                
                if not articles:
                    return json.dumps({"status": "no_results", "message": "Tidak ada artikel ditemukan"})
                
                # Format articles for agent
                formatted_articles = []
                for article in articles[:5]:
                    formatted_articles.append({
                        "headline": article.get('headline', ''),
                        "summary": article.get('summary', ''),
                        "date": article.get('tanggal', ''),
                        "source": article.get('source', '')
                    })
                
                # Cache articles
                self.recent_articles_cache = articles[:5]
                self.conversation_articles = articles[:5]  
                self.last_query = query
                self.last_query_time = time.time()
                
                # Track index untuk WhatsApp (setelah search_news dipanggil)
                self.last_news_fetch_index = self.memory.get_message_count()
                
                result = {
                    "status": "success",
                    "count": len(formatted_articles),
                    "articles": formatted_articles
                }
                
                print(f"[TOOL] search_news returned {len(formatted_articles)} articles")
                return json.dumps(result, ensure_ascii=False)
                
            except Exception as e:
                print(f"[TOOL] search_news error: {e}")
                return json.dumps({"status": "error", "message": str(e)})
        
        @tool
        def use_cached_context() -> str:
            """
            Use previously cached news articles from recent conversation.
            Call this tool when user asks follow-up questions about previously discussed news.
            
            Returns:
                JSON string containing cached news articles
            """
            print(f"[TOOL] use_cached_context called")
            
            if not self.recent_articles_cache:
                return json.dumps({"status": "no_cache", "message": "Tidak ada konteks sebelumnya"})
            
            # Calculate time since last query
            time_diff = time.time() - self.last_query_time
            
            if time_diff > 300:  # 5 minutes
                print(f"[TOOL] Cache expired ({time_diff:.1f}s old)")
                return json.dumps({"status": "expired", "message": "Konteks sudah terlalu lama"})
            
            # Format cached articles
            formatted_articles = []
            for article in self.recent_articles_cache:
                formatted_articles.append({
                    "headline": article.get('headline', ''),
                    "summary": article.get('summary', ''),
                    "date": article.get('tanggal', ''),
                    "source": article.get('source', '')
                })
            
            if self.last_news_fetch_index == -1:
                self.last_news_fetch_index = self.memory.get_message_count()
            
            result = {
                "status": "success",
                "count": len(formatted_articles),
                "last_query": self.last_query,
                "time_since_query": f"{time_diff:.1f}s",
                "articles": formatted_articles
            }
            
            print(f"[TOOL] use_cached_context returned {len(formatted_articles)} cached articles")
            return json.dumps(result, ensure_ascii=False)
        
        @tool
        def save_recommendation(content: str, content_type: str = "recommendation") -> str:
            """
            Save important content (recommendation, summary, analysis) for later sending to WhatsApp.
            Call this tool when you generate important content that user might want to share.
            
            Args:
                content: The content to save (recommendation, summary, analysis, etc.)
                content_type: Type of content - "recommendation", "summary", "analysis", or "news"
            
            Use cases:
                - After generating recommendation: save_recommendation(content="...", content_type="recommendation")
                - After summarizing news: save_recommendation(content="...", content_type="summary")
                - After analysis: save_recommendation(content="...", content_type="analysis")
            
            IMPORTANT FOR RECOMMENDATIONS:
                When user asks for recommendation based on news:
                1. FIRST save news context: save_recommendation(content="[ringkasan berita]", content_type="summary")
                2. THEN save recommendation: save_recommendation(content="[rekomendasi]", content_type="recommendation")
                
                This ensures WhatsApp message includes both context and recommendation.
            
            Returns:
                JSON string with save status
            """
            print(f"[TOOL] save_recommendation called: type='{content_type}', length={len(content)}")
            
            if not content or content.strip() == "":
                return json.dumps({
                    "status": "error",
                    "message": "Cannot save empty content"
                })
            
            # Save based on content type
            if content_type.lower() in ["recommendation", "rekomendasi", "saran"]:
                self.saved_recommendation = content
                print(f"[TOOL] ✓ Saved recommendation ({len(content)} chars)")
            elif content_type.lower() in ["summary", "rangkuman", "ringkasan", "news", "berita"]:
                self.saved_news_summary = content
                print(f"[TOOL] ✓ Saved news summary ({len(content)} chars)")
            elif content_type.lower() in ["analysis", "analisis"]:
                self.saved_recommendation = content  # Treat analysis like recommendation
                print(f"[TOOL] ✓ Saved analysis ({len(content)} chars)")
            else:
                # Default: save as recommendation
                self.saved_recommendation = content
                print(f"[TOOL] ✓ Saved as recommendation ({len(content)} chars)")
            
            return json.dumps({
                "status": "success",
                "message": f"Content saved successfully ({content_type})",
                "content_length": len(content)
            })
        
        @tool
        def send_to_whatsapp(contact_name: str = "") -> str:
            """
            Send summary of current conversation (news articles + recommendations) to WhatsApp contact(s).
            Call this tool when user requests to send/share information to WhatsApp.
            
            Args:
                contact_name: Optional. Specify which contact(s) to send to.
                            - "" (empty) → will list available contacts for user to choose
                            - "Grup Keluarga" → send to specific contact by name (fuzzy match)
                            - "all" or "semua" → send to all assigned contacts
            
            Trigger phrases: 
                - "kirim ke whatsapp" → will list contacts
                - "kirim ke Grup Keluarga" → send to that specific contact
                - "kirim ke semua kontak" → send to all contacts
            
            Returns:
                JSON string with send status and results
            """
            print(f"[TOOL] send_to_whatsapp called with contact_name: '{contact_name}'")
            
            # Check authentication
            if self.auth_client and not self.auth_client.is_authenticated():
                return json.dumps({
                    "status": "error",
                    "message": "Authentication required to send WhatsApp messages"
                })
            
            # Check permission
            if self.auth_client and not self.auth_client.has_permission("send_whatsapp"):
                user_name = self.auth_client.user_context.get('full_name', self.auth_client.user_context.get('username', 'User'))
                user_role = self.auth_client.user_context.get('role', {}).get('name', 'Unknown')
                return json.dumps({
                    "status": "error",
                    "message": f"Maaf, Anda ({user_name}) dengan role {user_role} tidak memiliki akses untuk mengirim pesan WhatsApp"
                })
            
            if not self.fonnte_client:
                return json.dumps({
                    "status": "error",
                    "message": "WhatsApp service not configured"
                })
            
            # Get available contacts for user (authenticated)
            if self.auth_client:
                available_contacts = self.auth_client.get_available_contacts()
                if not available_contacts:
                    return json.dumps({
                        "status": "error",
                        "message": "No WhatsApp contacts assigned to your account. Contact administrator."
                    })
            else:
                # Fallback to env variable if no auth (legacy mode)
                target_number = os.getenv('FONNTE_TARGET_NUMBER')
                if not target_number:
                    return json.dumps({
                        "status": "error",
                        "message": "Target phone number not configured"
                    })
                available_contacts = [{"id": 0, "name": "Default Contact", "phone_number": target_number}]
            
            # ====================================================================================
            # CONTACT SELECTION LOGIC
            # ====================================================================================
            
            target_contacts = []
            
            # Case 1: No contact specified - ASK USER TO CHOOSE
            if not contact_name or contact_name.strip() == "":
                contact_list_str = "\n".join([
                    f"{i+1}. {c['name']} ({c['phone_number']})" 
                    for i, c in enumerate(available_contacts)
                ])
                
                return json.dumps({
                    "status": "awaiting_selection",
                    "message": f"Anda memiliki {len(available_contacts)} kontak WhatsApp yang tersedia:\n\n{contact_list_str}\n\nMau kirim ke kontak mana? Sebutkan nama kontaknya, atau bilang 'semua' untuk kirim ke semua kontak.",
                    "available_contacts": [{"name": c['name'], "phone": c['phone_number']} for c in available_contacts]
                })
            
            # Case 2: Send to ALL contacts
            if contact_name.lower().strip() in ["all", "semua", "semua kontak", "all contacts", "semuanya", "ke semua"]:
                target_contacts = available_contacts
                print(f"[TOOL] User requested to send to ALL {len(target_contacts)} contacts")
            
            # Case 3: Search for specific contact by name (FUZZY MATCH)
            else:
                contact_name_lower = contact_name.lower().strip()
                
                for contact in available_contacts:
                    contact_name_in_db = contact['name'].lower()
                    
                    # Fuzzy matching: check if user input is substring of contact name or vice versa
                    if (contact_name_lower in contact_name_in_db or 
                        contact_name_in_db in contact_name_lower or
                        contact_name_lower == contact_name_in_db):
                        target_contacts.append(contact)
                
                # If no match found, show available contacts
                if not target_contacts:
                    available_names = ", ".join([f"'{c['name']}'" for c in available_contacts])
                    return json.dumps({
                        "status": "error",
                        "message": f"Kontak '{contact_name}' tidak ditemukan dalam daftar Anda.\n\nKontak yang tersedia: {available_names}\n\nSilakan sebutkan nama kontak yang benar atau bilang 'semua' untuk kirim ke semua kontak."
                    })
                
                print(f"[TOOL] Found {len(target_contacts)} matching contact(s) for '{contact_name}': {[c['name'] for c in target_contacts]}")
            
            # ====================================================================================
            # BUILD MESSAGE FROM SAVED CONTENT (PRIORITY) OR CONVERSATION
            # ====================================================================================
            
            message_parts = []
            
            # PRIORITY 1: Use explicitly saved content (from save_recommendation tool)
            if self.saved_recommendation or self.saved_news_summary:
                print("[TOOL] Using saved content for WhatsApp message")
                
                if self.saved_news_summary:
                    message_parts.append("KONTEKS BERITA:")
                    message_parts.append(self.saved_news_summary)
                
                if self.saved_recommendation:
                    message_parts.append("\n\nREKOMENDASI:")
                    message_parts.append(self.saved_recommendation)
            
            # PRIORITY 2: Fallback to conversation context (legacy behavior)
            else:
                print("[TOOL] No saved content, using conversation context")
                conversation_context = self.memory.get_conversation_context()
                
                if not conversation_context:
                    return json.dumps({
                        "status": "error",
                        "message": "Tidak ada konten untuk dikirim. Silakan minta saya membuat rekomendasi atau rangkuman terlebih dahulu."
                    })
                
                # Ambil jawaban setelah search_news/use_cached_context terakhir
                if self.last_news_fetch_index >= 0 and self.context_answer:
                    message_parts.append("KONTEKS BERITA:")
                    message_parts.append(self.context_answer)
                
                # Add Dita's latest response (recommendation/analysis)
                if self.last_response and self.last_response != self.context_answer:
                    message_parts.append("\n\nREKOMENDASI DITA:")
                    message_parts.append(self.last_response)
            
            if not message_parts:
                return json.dumps({
                    "status": "error",
                    "message": "Tidak ada konten untuk dikirim. Silakan minta saya membuat rekomendasi atau rangkuman terlebih dahulu."
                })
            
            message_parts.append("\n---")
            
            # Add sender info if authenticated
            if self.auth_client:
                user_info = self.auth_client.get_user_context()
                sender_name = user_info.get('full_name', user_info.get('username'))
                sender_role = user_info.get('role', {}).get('name', '')
                message_parts.append(f"Dikirim oleh: {sender_name} ({sender_role})")
                message_parts.append("via Dita AI Assistant")
            else:
                message_parts.append("Dikirim oleh Dita AI Assistant")
            
            full_message = "\n".join(message_parts)
            
            # ====================================================================================
            # SEND TO TARGET CONTACT(S)
            # ====================================================================================
            
            send_results = []
            send_failures = []
            
            for idx, contact in enumerate(target_contacts):
                contact_name = contact['name']
                phone_number = contact['phone_number']
                
                try:
                    print(f"[TOOL] Sending to {contact_name} ({phone_number})...")
                    result = self.fonnte_client.send_message(phone_number, full_message)
                    
                    if result['status'] == 'success':
                        send_results.append({
                            "name": contact_name,
                            "phone": phone_number,
                            "status": "success"
                        })
                        print(f"[TOOL] ✓ Successfully sent to {contact_name}")
                    else:
                        send_failures.append({
                            "name": contact_name,
                            "phone": phone_number,
                            "error": result.get('message', 'Unknown error')
                        })
                        print(f"[TOOL] ✗ Failed to send to {contact_name}: {result.get('message')}")
                
                except Exception as e:
                    send_failures.append({
                        "name": contact_name,
                        "phone": phone_number,
                        "error": str(e)
                    })
                    print(f"[TOOL] ✗ Exception sending to {contact_name}: {e}")
                
                # Add delay between sends to avoid being flagged as bot/spam
                # Skip delay for last contact
                if idx < len(target_contacts) - 1:
                    delay_seconds = 2  # 2 seconds delay between sends
                    print(f"[TOOL] ⏳ Waiting {delay_seconds}s before next send...")
                    time.sleep(delay_seconds)
            
            # Log audit if authenticated (log all attempts)
            if self.auth_client:
                self.auth_client.log_action(
                    action="send_whatsapp",
                    resource="whatsapp",
                    details={
                        "contacts_sent": [r['name'] for r in send_results],
                        "contacts_failed": [f['name'] for f in send_failures],
                        "message_length": len(full_message),
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                )
            
            # Build response message
            if send_results and not send_failures:
                # All sent successfully
                contact_names = "\n".join([f"✓ {r['name']} ({r['phone']})" for r in send_results])
                return json.dumps({
                    "status": "success",
                    "message": f"Berhasil dikirim ke {len(send_results)} kontak:\n{contact_names}",
                    "sent_to": send_results,
                    "message_length": len(full_message)
                }, ensure_ascii=False)
            
            elif send_results and send_failures:
                # Partial success
                success_names = "\n".join([f"✓ {r['name']}" for r in send_results])
                failed_names = "\n".join([f"✗ {f['name']}: {f['error']}" for f in send_failures])
                return json.dumps({
                    "status": "partial_success",
                    "message": f"Berhasil dikirim ke {len(send_results)} dari {len(target_contacts)} kontak:\n\nBerhasil:\n{success_names}\n\nGagal:\n{failed_names}",
                    "sent_to": send_results,
                    "failed": send_failures
                }, ensure_ascii=False)
            
            else:
                # All failed
                failed_names = "\n".join([f"✗ {f['name']}: {f['error']}" for f in send_failures])
                return json.dumps({
                    "status": "error",
                    "message": f"Gagal mengirim ke semua kontak:\n{failed_names}",
                    "failed": send_failures
                }, ensure_ascii=False)
        
        # Register tools
        tools_list = [search_news, use_cached_context, save_recommendation]
        
        # Add WhatsApp tool if available
        if self.fonnte_client:
            tools_list.append(send_to_whatsapp)
        
        self.tools = tools_list
        
        # Create agent with tools
        try:
            self.agent_executor = create_react_agent(
                self.langchain_llm,
                self.tools,
                checkpointer=MemorySaver()
            )
            print(f"Agent created with {len(self.tools)} tools")
        except Exception as e:
            print(f"Failed to create agent: {e}")
            raise

    def ask(self, question: str) -> Dict[str, Any]:
        """Process user question using agent-based tool calling"""
        start_time = time.time()
        
        try:
            print(f"\n{'='*60}")
            print(f"Query: '{question}'")
            print(f"{'='*60}")
            
            # Build comprehensive agent prompt
            conversation_context = self.memory.get_conversation_context()
            
            agent_prompt = f"""Anda adalah Dita, asisten AI untuk berita Indonesia.

PERCAKAPAN SEBELUMNYA:
{conversation_context if conversation_context else "Belum ada percakapan sebelumnya"}

PERTANYAAN USER: {question}

INSTRUKSI RESPONSE:

1. ANALISIS PERTANYAAN (internal, jangan ditulis di output):
   - Cek apakah follow-up (kata: "itu", "tersebut", "tadi") atau topik baru
   - Pilih tool: use_cached_context (follow-up) atau search_news (topik baru)
   - Identifikasi intent: INFORMATIONAL, ACTION, atau RECOMMENDATION

2. GENERATE RESPONSE (output ke user):
   - Narasi natural dan mengalir (2-4 kalimat)
   - TIDAK gunakan bullet points, markdown, numbering, atau **bold**
   - TIDAK jelaskan proses berpikir (tool yang dipilih, intent, dll)
   - Sertakan sumber: "Menurut [sumber] tanggal [tanggal]..."
   
3. HANDLING BERDASARKAN INTENT:
   
   a) INFORMATIONAL: "apa yang terjadi", "ada berita", "bagaimana kejadian"
      → Jawab dengan FAKTA dari berita
      → Contoh: "Menurut Kompas tanggal 10 Desember, terjadi demo di Jakarta terkait penolakan UU Cipta Kerja. Ribuan mahasiswa turun ke jalan dan aksi berjalan hingga sore hari."
   
   b) ACTION: "apa tindakan", "langkah apa", "apa yang dilakukan"
      → Sebutkan tindakan KONKRET dari berita
      → Jika tidak ada: "Belum ada informasi tentang tindakan pejabat dalam berita yang saya akses."
   
   c) RECOMMENDATION: "apa rekomendasi", "sebaiknya bagaimana", "apa yang bisa dilakukan"
      → Berikan REKOMENDASI dalam bentuk NARASI MENGALIR
      → Format: Ringkas situasi → saran konkret → penutup
      → Contoh: "Mengingat situasi demo yang sensitif, penting untuk mengutamakan dialog antara pihak berwenang dan massa untuk mencari solusi damai. Transparansi dalam penanganan insiden juga perlu dijaga agar tidak timbul eskalasi. Semua pihak sebaiknya mengedepankan musyawarah demi ketertiban bersama."
      → WAJIB call save_recommendation DUA KALI:
         1. save_recommendation(content="[ringkasan berita]", content_type="summary")
         2. save_recommendation(content="[rekomendasi lengkap]", content_type="recommendation")

4. WHATSAPP HANDLING:
   - Jika user minta kirim tanpa sebutkan kontak → call send_to_whatsapp("")
   - Jika user sebutkan nama kontak → call send_to_whatsapp("nama_kontak")
   - Jika user minta kirim ke semua → call send_to_whatsapp("semua")
   - Jika tool return error: SAMPAIKAN ERROR MESSAGE PERSIS SEPERTI YANG DIBERIKAN TOOL
     * JANGAN ubah atau interpretasi ulang error message
     * Contoh: Tool return "Maaf, Anda (...) tidak memiliki akses..."
              → Sampaikan PERSIS: "Maaf, Anda (...) tidak memiliki akses..."
              → JANGAN ubah jadi "akun saya tidak memiliki akses"

PENTING: Jangan pernah tampilkan proses berpikir internal ke user. Output harus natural seperti percakapan biasa."""

            # Execute agent
            print("[AGENT] Invoking agent...")
            config = {"configurable": {"thread_id": "dita-session"}}
            
            agent_response = self.agent_executor.invoke(
                {"messages": [HumanMessage(content=agent_prompt)]},
                config=config
            )
            
            # Extract agent's final response
            messages = agent_response.get("messages", [])
            final_response = ""
            
            for msg in reversed(messages):
                if isinstance(msg, AIMessage) and msg.content:
                    # Skip messages that are just tool calls
                    if msg.tool_calls:
                        continue
                    
                    # Extract text content from various formats
                    content = msg.content
                    if isinstance(content, str):
                        final_response = content
                        break
                    elif isinstance(content, list):
                        # Extract text from list format
                        for item in content:
                            if isinstance(item, dict) and item.get('type') == 'text':
                                final_response = item.get('text', '')
                                break
                        if final_response:
                            break
            
            if not final_response:
                final_response = "Maaf, saya tidak dapat memproses pertanyaan Anda."
            
            # Extract sources from cached articles
            sources = [article.get('headline', '') for article in self.recent_articles_cache]
            
            # Store last response for WhatsApp sharing (legacy fallback)
            # Note: Now we prefer explicit save_recommendation tool over this implicit approach
            self.last_response = final_response
            print(f"[CONTEXT] Saved to last_response: {final_response[:50]}...")
            
            # Update memory
            self.memory.add_user_message(question)
            self.memory.add_ai_message(final_response)
            
            # Simpan context_answer jika ini jawaban setelah news fetch
            current_message_count = self.memory.get_message_count()
            if self.last_news_fetch_index >= 0 and current_message_count == self.last_news_fetch_index + 2:
                self.context_answer = final_response
                print(f"[CONTEXT] Saved context_answer for WhatsApp")
            
            print(f"[AGENT] Response generated")
            print(f"{'='*60}\n")
            
            return {
                "answer": final_response,
                "sources": sources,
                "source_count": len(sources),
                "response_time": time.time() - start_time,
                "status": "success"
            }
            
        except Exception as e:
            error_response = f"Terjadi error saat memproses pertanyaan: {str(e)}"
            print(f"[ERROR] {e}")
            
            return {
                "answer": error_response,
                "sources": [],
                "source_count": 0,
                "response_time": time.time() - start_time,
                "status": "error"
            }
    

    
    def reset_memory(self):
        """Reset conversation history"""
        self.memory.clear()
        self.recent_articles_cache = []
        self.last_query = ""
        self.last_query_time = 0
        print("Memory and cache cleared")