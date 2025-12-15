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
    def __init__(self):
        print("\n" + "="*60)
        print("Initializing Dita RAG Assistant with Agent System")
        print("="*60)
        
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

    ATURAN KETAT:
    - Jika berita TIDAK RELEVAN dengan pertanyaan: "Maaf, informasi tentang [topik] belum tersedia dalam berita yang saya akses"
    - Jika pertanyaan tentang pejabat tapi berita tidak menyebut tindakan pejabat: WAJIB bilang "Belum ada informasi"
    - JANGAN menambahkan informasi di luar berita yang diberikan
    - JANGAN menggunakan format list, bullet, atau numbering dalam jawaban

    JAWABAN:"""
            )
                
        except Exception as e:
            print(f"❌ Language model setup failed: {e}")
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
        def send_to_whatsapp() -> str:
            """
            Send summary of current conversation (news articles + recommendations) to WhatsApp.
            Call this tool when user requests to send/share information to WhatsApp.
            
            Trigger phrases: "kirim ke whatsapp", "send to wa", "share ke whatsapp", "kirim rangkuman"
            
            Returns:
                JSON string with send status
            """
            print(f"[TOOL] send_to_whatsapp called")
            
            if not self.fonnte_client:
                return json.dumps({
                    "status": "error",
                    "message": "WhatsApp service not configured"
                })
            
            # Get target phone number from environment
            target_number = os.getenv('FONNTE_TARGET_NUMBER')
            if not target_number:
                return json.dumps({
                    "status": "error",
                    "message": "Target phone number not configured in .env"
                })
            
            # Build message from conversation history
            conversation_context = self.memory.get_conversation_context()
            
            if not conversation_context:
                return json.dumps({
                    "status": "error",
                    "message": "No conversation to send"
                })
            
            # Build message: Context + Recommendation
            message_parts = []
            
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
                    "message": "No content to send"
                })
            
            message_parts.append("\n---")
            message_parts.append("Dikirim oleh Dita AI Assistant")
            
            full_message = "\n".join(message_parts)
            
            # Send via Fonnte
            try:
                result = self.fonnte_client.send_message(target_number, full_message)
                
                if result['status'] == 'success':
                    print(f"[TOOL] Message sent to {target_number}")
                    return json.dumps({
                        "status": "success",
                        "message": f"Rangkuman berhasil dikirim ke WhatsApp {target_number}",
                        "phone_number": result.get('phone_number', target_number)
                    }, ensure_ascii=False)
                else:
                    print(f"[TOOL] Failed to send: {result.get('message')}")
                    return json.dumps({
                        "status": "error",
                        "message": result.get('message', 'Failed to send')
                    })
                    
            except Exception as e:
                print(f"[TOOL] send_to_whatsapp error: {e}")
                return json.dumps({
                    "status": "error",
                    "message": f"Error sending message: {str(e)}"
                })
        
        # Register tools
        tools_list = [search_news, use_cached_context]
        
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

LANGKAH 1 - ANALISIS PERTANYAAN:
Tentukan apakah ini pertanyaan follow-up atau topik baru:
- Cari kata rujukan: "itu", "tersebut", "tadi", "yang tadi", "sebelumnya"
- Periksa apakah pertanyaan terkait percakapan sebelumnya

LANGKAH 2 - PILIH TOOL:
- use_cached_context: Jika pertanyaan follow-up tentang berita yang sudah dibahas
- search_news: Jika pertanyaan tentang topik baru atau butuh informasi fresh
- send_to_whatsapp: Jika user minta kirim/share rangkuman ke WhatsApp

LANGKAH 3 - KLASIFIKASI INTENT PERTANYAAN:
Setelah mendapat artikel, identifikasi jenis pertanyaan:
1. INFORMATIONAL: "apa yang terjadi", "ada berita", "bagaimana kejadian"
   → Jawab dengan FAKTA dari berita
   
2. ACTION: "apa tindakan", "langkah apa", "apa yang dilakukan"
   → Sebutkan tindakan KONKRET dari berita
   → Jika tidak ada: "Belum ada informasi tentang tindakan..."
   
3. RECOMMENDATION: "apa rekomendasi", "sebaiknya bagaimana", "apa yang bisa dilakukan"
   → Berikan REKOMENDASI berdasarkan konteks berita
   → Format: (1) Ringkas situasi, (2) Saran 2-3 hal, (3) Penutup
   → Contoh: "Mengingat [situasi], beberapa hal yang bisa dilakukan: [saran 1], [saran 2]. [penutup]"

LANGKAH 4 - GENERATE RESPONSE:
- Narasi natural dan mengalir (2-4 kalimat)
- Sertakan sumber: "Menurut [sumber] tanggal [tanggal]..."
- TIDAK gunakan bullet points, markdown, atau numbering
- WAJIB jawab sesuai intent: faktual untuk info, rekomendasi untuk saran

ATURAN PENTING:
- Jika user minta rekomendasi: WAJIB berikan rekomendasi konkret
- Jangan hanya melaporkan "tidak ada rekomendasi di berita"
- Berikan insight/saran berdasarkan konteks situasi di berita"""

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
            
            # Store last response for WhatsApp sharing
            self.last_response = final_response
            
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