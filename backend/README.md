# Custom AI Assistant - Dita

Professional voice assistant system with advanced RAG (Retrieval-Augmented Generation), wake word detection, Indonesian speech-to-text, and news analysis powered by Google Gemini API with LangChain integration.

## Features

- **Advanced AI Integration**: Google Gemini 2.5-flash API with LangChain framework for production-grade responses
- **News Analysis System**: Real-time Elasticsearch-based news search and analysis with 1.3M+ Indonesian news articles
- **Provider Abstraction**: Multi-provider LLM support (Google Gemini, OpenAI, Anthropic) with zero-code switching
- **Wake Word Detection**: "Hey Dita" activation using Porcupine engine
- **Real-Time Voice Activity Detection**: Silero VAD neural network for dynamic recording with automatic silence detection
- **Indonesian Speech Recognition**: Optimized for Indonesian language processing
- **Text-to-Speech Output**: Google Cloud TTS with Indonesian voice for natural conversational responses
- **Centralized Configuration**: YAML-based configuration management with environment-specific overrides
- **Conversation Memory**: Context-aware conversations with LangChain memory management
- **Production Ready**: Clean architecture with comprehensive error handling and fallback mechanisms

## Architecture

```
Dita Assistant
├── Google Gemini API (Primary LLM) + LangChain Integration
├── Elasticsearch News Search (1.3M+ Indonesian articles)
├── Provider Abstraction Layer (Google/OpenAI/Anthropic)
├── Wake Word Detection (Porcupine)
├── Voice Activity Detection (Silero VAD - Neural Network)
├── Speech-to-Text (Indonesian optimized)
├── Text-to-Speech (Google Cloud TTS - Indonesian)
├── Configuration Manager (YAML-based)
└── LangChain Conversation Memory
```

## Current System Architecture & Components

### Core AI Models Used

| Component | Model/Technology | Purpose | Provider |
|-----------|------------------|---------|----------|
| **Primary LLM** | `gemini-2.5-flash` | Natural language generation & conversation | Google AI |
| **Fallback LLM** | `gemini-2.0-flash-exp` | Backup generation (configurable) | Google AI |
| **News Search** | Elasticsearch 8.x | Real-time Indonesian news analysis | Elastic |
| **Wake Word Detection** | `hey-dita_linux.ppn` | "Hey Dita" trigger detection | Picovoice Porcupine |
| **Voice Activity Detection** | Silero VAD | Real-time speech detection with auto-stop | Silero (PyTorch) |
| **Speech Recognition** | `wav2vec2-large-xls-r-1b-indonesian` | Indonesian voice-to-text conversion | Hugging Face |
| **Text-to-Speech** | Google Cloud TTS | Indonesian voice output with natural intonation | Google Cloud |
| **Framework** | LangChain | RAG orchestration & conversation memory | LangChain |

### Detailed Component Breakdown

#### 1. Language Model Layer (LangChain Integration)
```
Primary: Google Gemini 2.5-flash API
├── Model: gemini-2.5-flash
├── Provider: Google AI (FREE API)
├── Framework: LangChain ChatGoogleGenerativeAI
├── Capabilities: High-quality Indonesian responses, context awareness
├── Performance: 6-8 second response time
├── Configuration: temperature=0.1, max_tokens=2048
└── Provider Abstraction: Support for OpenAI, Anthropic switching

Fallback: Configurable Secondary Model
├── Model: gemini-2.0-flash-exp (default)
├── Provider: Configurable via YAML
├── Framework: LangChain abstraction layer
├── Capabilities: Automatic failover, provider switching
└── Usage: Seamless fallback when primary unavailable
```

#### 2. News Analysis & Search Layer
```
Data Source: Elasticsearch Cluster
├── Host: Production Elasticsearch (10.17.5.106:9200)
├── Index: news_2025.08
├── Documents: 1,333,183 Indonesian news articles
├── Search: Full-text search with temporal filtering
├── Performance: Real-time query processing
├── Features: Domain filtering, date range queries, relevance scoring
└── Integration: Native Elasticsearch Python client

Query Processing: NewsQueryProcessor
├── Temporal Extraction: Date range detection from natural language
├── Query Cleaning: Text normalization and optimization
├── Relevance Filtering: Domain-specific news filtering
├── Fallback Strategy: Temporal -> All-time search
└── Performance: Sub-second query processing
```

#### 3. Conversation Management Layer (LangChain)
```
Memory System: LangChainConversationMemory
├── Framework: LangChain ChatMessageHistory
├── Capacity: 10 messages maximum (configurable)
├── Message Types: HumanMessage, AIMessage, SystemMessage
├── Context Management: Automatic conversation trimming
├── Performance: Efficient memory management
└── Integration: Native LangChain memory implementation

Prompt Engineering: Production PromptTemplate
├── Template: Professional Indonesian conversation prompts
├── Context Variables: conversation_history, context, question
├── Instructions: Factual reporting, source attribution
├── Fallback: Graceful handling for no-context scenarios
└── Language: Natural Indonesian with professional tone
```

#### 4. Voice Processing Layer
```
Wake Word Detection: Picovoice Porcupine
├── Model: hey-dita_linux.ppn (custom trained)
├── Keyword: "Hey Dita"
├── Platform: Cross-platform (Linux/Windows/macOS)
├── Performance: Low-latency, offline processing
└── Sensitivity: Configurable (default: 0.5)

Voice Activity Detection: Silero VAD
├── Model: silero-vad (neural network-based)
├── Framework: PyTorch with ONNX runtime
├── Capabilities: Real-time speech detection in noisy environments
├── Features: Automatic silence detection, dynamic recording
├── Configuration: 0.5 speech threshold, 1.0s silence threshold
├── Performance: Superior noise rejection vs rule-based VAD
└── Use Case: Stops recording automatically when user stops speaking

Speech-to-Text: Wav2Vec2 Indonesian Model
├── Model: wav2vec2-large-xls-r-1b-indonesian
├── Provider: Hugging Face (fine-tuned for Indonesian)
├── Architecture: Wav2Vec2ForCTC with Wav2Vec2Processor
├── Capabilities: High-accuracy Indonesian speech recognition
├── Performance: Optimized for Indonesian language patterns
├── Configuration: 16kHz sample rate, dynamic duration with VAD
└── Device: CPU/GPU configurable

Text-to-Speech: Google Cloud TTS
├── Service: Google Cloud Text-to-Speech API
├── Voice: id-ID-Standard-B (Indonesian Male)
├── Language: Indonesian (id-ID)
├── Format: LINEAR16, 24kHz sample rate, Mono
├── Features: Natural intonation, SSML support
├── Performance: Cloud-based synthesis with high quality
├── Authentication: Service account credentials
└── Use Case: Voice output for conversational responses
```

#### 5. Configuration Management System
```
Configuration Manager: YAML-based Centralized Config
├── Structure: Hierarchical YAML configuration
├── Environment Support: development/production overrides
├── API Key Management: Environment variable abstraction
├── Provider Abstraction: LLM provider switching via config
├── Features: Hot-reload, validation, fallback values
└── Security: Environment variable injection, no hardcoded secrets
```

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/AzrilFahmiardi/Custom-AI-Assistant.git
cd Custom-AI-Assistant
```

### 2. Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy environment template
cp .env.example .env
```

**Configure `.env` file:**
```bash
# Picovoice API Key (for wake word detection)
PORCUPINE_ACCESS_KEY=your_porcupine_access_key_here

# Google Gemini API Key (for AI responses)
GEMINI_API_KEY=your_gemini_api_key_here

# Elasticsearch credentials (if using external cluster)
ES_PASSWORD=your_elasticsearch_password_here
```

**API Key Setup:**
- **Porcupine Access Key**: Register at [Picovoice Console](https://console.picovoice.ai/)
- **Gemini API Key**: Get free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### 5. Run the Assistant
```bash
python main.py
```

## Usage Guide

### Voice Interaction Mode
1. Run `python main.py`
2. Wait for "Menunggu kata pemicu 'Hey Dita'" message
3. Say "Hey Dita" to activate the assistant
4. Speak your question naturally - recording stops automatically when you finish speaking
5. Say "keluar" to exit

**Note:** The system uses Silero VAD for automatic speech detection. Recording will stop automatically 1 second after you finish speaking, eliminating the need for fixed-duration recording.

### Direct RAG Testing
```bash
# Test RAG system directly (text mode)
python -c "
from rag import DitaRAGAssistant
dita = DitaRAGAssistant()
result = dita.ask('Apa berita terbaru tentang polisi?')
print(f'Answer: {result[\"answer\"]}')
print(f'Sources: {result[\"source_count\"]}')
"
```

## Configuration

### System Configuration (`config.yaml`)
```yaml
# API Keys and Secrets
api_keys:
  porcupine: ${PORCUPINE_ACCESS_KEY}
  gemini: ${GEMINI_API_KEY}
  elasticsearch: ${ES_PASSWORD}

# Elasticsearch Configuration
elasticsearch:
  host: "10.17.5.106"
  port: 9200
  username: "elastic"
  password: ${ES_PASSWORD}
  timeout: 5
  max_retries: 3

# News Search Configuration  
news_search:
  index_name: "news_2025.08"
  data_scope:
    keyword_filter: "polisi"
  max_results: 5
  date_boost_factor: 1.5
  summary_max_length: 300
  source_diversity: true

# Language Models Configuration
llm:
  primary:
    provider: "google_gemini"
    api_key_name: "GEMINI_API_KEY"
    model_name: "gemini-2.5-flash"
    temperature: 0.1
    max_tokens: 2048
    timeout: 30
  fallback:
    provider: "google_gemini"
    api_key_name: "GEMINI_API_KEY"
    model_name: "gemini-2.0-flash-exp"
    temperature: 0.1
    max_tokens: 1024

# Speech-to-Text Configuration
stt:
  model_name: "kingabzpro/wav2vec2-large-xls-r-1b-indonesian"
  sample_rate: 16000
  default_duration: 5
  device: "cpu"

# Voice Activity Detection Configuration
vad:
  enabled: true
  model: "silero"
  threshold: 0.5
  silence_threshold_seconds: 1.0
  min_recording_seconds: 0.5
  max_recording_seconds: 30
  sample_rate: 16000
  channels: 1

# Wake Word Detection
wakeword:
  model_path: "models/hey-dita_linux.ppn"
  sensitivity: 0.5
  audio_device_index: -1

# Audio Processing
audio:
  input:
    sample_rate: 16000
    channels: 1
    dtype: "float32"
    device_index: -1
  processing:
    noise_reduction: false
    voice_activity_detection: false
```

### Environment Variables (`.env`)
```bash
# Required API Keys
PORCUPINE_ACCESS_KEY=your_porcupine_key_here
GEMINI_API_KEY=your_gemini_key_here

# Elasticsearch (if using external cluster)
ES_PASSWORD=your_elasticsearch_password_here

# Optional Environment
ENVIRONMENT=development  # or production
```

## Provider Abstraction

### Switching Between LLM Providers
The system supports seamless switching between different LLM providers without code changes:

#### Google Gemini to OpenAI
```yaml
# config.yaml - Change provider configuration only
llm:
  primary:
    provider: "openai"
    api_key_name: "OPENAI_API_KEY"
    model_name: "gpt-4"
    temperature: 0.7
    max_tokens: 1000
```

#### Multi-Provider Fallback
```yaml
llm:
  primary:
    provider: "anthropic"
    api_key_name: "ANTHROPIC_API_KEY"
    model_name: "claude-3-sonnet-20240229"
  fallback:
    provider: "google_gemini"
    api_key_name: "GEMINI_API_KEY"
    model_name: "gemini-2.5-flash"
```

#### Supported Providers
- **Google Gemini**: `google_gemini` (Production ready)
- **OpenAI**: `openai` (Requires: `pip install langchain-openai`)
- **Anthropic**: `anthropic` (Requires: `pip install langchain-anthropic`)

## News Analysis System

### Data Source
- **Elasticsearch Cluster**: Production cluster with 1.3M+ Indonesian news articles
- **Index**: `news_2025.08` with real-time news updates
- **Coverage**: Comprehensive Indonesian news coverage with police/security focus
- **Performance**: Sub-second search with temporal filtering

### Query Capabilities
- **Temporal Queries**: "berita hari ini", "minggu lalu", "terbaru"
- **Domain Filtering**: Automatic filtering for relevant news categories
- **Context Search**: Follow-up questions use conversation context
- **Fallback Strategy**: Temporal search -> All-time search for comprehensive results

## Development

### Testing the System
```bash
# Test individual components
python -c "from config_manager import get_config; print('Config loaded successfully')"
python -c "from rag import DitaRAGAssistant; dita = DitaRAGAssistant(); print('RAG system ready')"

# Test news search
python -c "
from elasticsearch_news import ElasticsearchNewsRAG
news_rag = ElasticsearchNewsRAG()
results = news_rag.search_news('polisi terbaru')
print(f'Found {len(results)} news articles')
"

# Test speech components (if audio devices available)
python stt.py
python wakeword.py
```

### Performance Optimization

**For faster startup:**
- Ensure Elasticsearch cluster connectivity
- Pre-load LangChain models
- Use SSD storage for better I/O performance

**For better accuracy:**
- Adjust temporal filtering parameters
- Tune LLM temperature settings for response style
- Optimize news query processing

## Data Management

### News Data Structure
```json
{
  "_source": {
    "title": "Article headline",
    "content": "Full article content",
    "source": "News source",
    "tanggal": "Publication date",
    "headline": "Short headline",
    "summary": "Article summary"
  }
}
```

### Query Processing
- **Text Cleaning**: Automatic query normalization and optimization
- **Temporal Extraction**: Natural language date range detection
- **Relevance Scoring**: Elasticsearch relevance with date boosting
- **Context Integration**: LangChain conversation memory integration

## API Integration

### Google Gemini API
- **Model**: gemini-2.5-flash (free tier available)
- **Framework**: LangChain ChatGoogleGenerativeAI integration
- **Features**: High-quality Indonesian responses, context awareness, conversation memory
- **Rate Limits**: Generous free tier with reasonable limits
- **Fallback**: Configurable secondary model support

### Picovoice Porcupine
- **Wake Word**: Custom "Hey Dita" detection
- **Platform**: Cross-platform support
- **Performance**: Low-latency, offline processing

### Elasticsearch Integration
- **Cluster**: Production Elasticsearch deployment
- **Data**: 1.3M+ Indonesian news articles
- **Performance**: Real-time search with temporal filtering
- **Query Processing**: Natural language to Elasticsearch query translation

## System Requirements

- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum (8GB recommended for VAD + STT models)
- **Storage**: 2GB free space for models and cache
- **Network**: Internet connection for API calls and Elasticsearch access
- **Audio**: Microphone for voice interaction
- **Dependencies**: PyTorch (for Silero VAD and Wav2Vec2 models)

## Troubleshooting

### Common Issues

**"Environment variable not found"**
- Ensure `.env` file exists with correct API keys
- Check API key format and validity
- Verify environment variable names match configuration

**"Elasticsearch connection failed"**
- Verify Elasticsearch cluster connectivity
- Check network access to cluster IP
- Validate credentials and permissions

**"Wake word not detected"**
- Verify Porcupine API key is valid
- Check microphone permissions and functionality
- Adjust sensitivity in configuration

**"Recording not stopping automatically"**
- Verify VAD is enabled in config.yaml
- Check microphone quality and background noise levels
- Adjust VAD threshold (0.3-0.7 range, default: 0.5)
- Increase silence_threshold_seconds if stopping too early

**"No news results found"**
- Check Elasticsearch index status
- Verify temporal filtering configuration
- Try broader query terms

### Performance Issues

**Slow response times:**
- Check Elasticsearch cluster performance
- Verify internet connectivity for API calls
- Monitor LLM API rate limits

**Memory issues:**
- Reduce conversation memory size
- Optimize model loading
- Check available system memory

## Architecture Benefits

### Production Features
- **Provider Abstraction**: Zero-code LLM provider switching
- **Conversation Memory**: LangChain-managed context awareness
- **Real-time Data**: Live news analysis from Elasticsearch
- **Robust Fallbacks**: Multi-tier error handling and recovery
- **Configuration Management**: Environment-aware YAML configuration

### Scalability
- **Horizontal Scaling**: Elasticsearch cluster scaling
- **Provider Flexibility**: Easy switching between cloud LLM providers
- **Memory Management**: Efficient conversation history management
- **Performance Monitoring**: Built-in timing and status reporting

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Google AI](https://ai.google.dev/) for Gemini API access
- [LangChain](https://langchain.com/) for RAG framework and conversation management
- [Elasticsearch](https://www.elastic.co/) for search and analytics platform
- [Picovoice](https://picovoice.ai/) for Porcupine wake word engine
- [Silero Team](https://github.com/snakers4/silero-vad) for neural network-based voice activity detection
- [Hugging Face](https://huggingface.co/) for speech recognition models
