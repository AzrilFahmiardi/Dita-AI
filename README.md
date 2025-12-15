# Dita AI Assistant

Voice-enabled AI assistant with web dashboard.

## Architecture

```
Host Machine (Terminal)          Docker Containers
┌──────────────────────┐         ┌─────────────────────┐
│ Voice Assistant      │         │ WebSocket Server    │
│ - Wake word detect   │────────▶│ FastAPI (port 8000) │
│ - Speech to text     │  HTTP   └──────────┬──────────┘
│ - RAG + Gemini AI    │                    │ WebSocket
│ - Text to speech     │         ┌──────────▼──────────┐
└──────────────────────┘         │ Dashboard           │
  (Requires microphone)          │ React (port 5173)   │
                                 └─────────────────────┘
```

## Project Structure

```
Dita/
├── voice-assistant/       # Voice I/O + AI processing (runs on host)
│   ├── main.py           # Entry point
│   ├── wakeword.py       # Wake word detection
│   ├── stt.py            # Speech-to-text
│   ├── rag.py            # RAG with Gemini
│   ├── tts.py            # Text-to-speech
│   └── pyproject.toml    # Dependencies
├── backend/              # WebSocket API server (Docker)
│   ├── main.py           # FastAPI server
│   ├── broadcaster.py    # WebSocket broadcaster
│   ├── Dockerfile
│   └── pyproject.toml    # API dependencies
├── frontend/             # React dashboard (Docker)
│   ├── src/
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

## Quick Start

### 1. Start Docker Infrastructure

```bash
# Start WebSocket server and dashboard
docker compose up -d

# Check status
docker compose ps
```

### 2. Install Voice Assistant Dependencies

```bash
cd voice-assistant
uv sync
```

### 3. Run Voice Assistant

```bash
cd voice-assistant
uv run python main.py
```

**Note:** Keep this terminal running. Say "Hey Dita" to interact.

### 4. Access Dashboard

Open browser: http://localhost:5173

## Stop Services

```bash
# Stop voice assistant: Ctrl+C in terminal

# Stop Docker containers
docker compose down
```

## Access Points

- **Frontend Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Environment Setup

Configure `.env` file in root directory:
- `PORCUPINE_ACCESS_KEY` - Wake word detection
- `GEMINI_API_KEY` - Google Gemini API
- `ES_PASSWORD` - Elasticsearch password
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to GCP credentials

## Components

- **Voice Assistant** (Host): Python wake word + STT + RAG + TTS
- **WebSocket Server** (Docker): FastAPI broadcast server (port 8000)
- **Dashboard** (Docker): React real-time monitor (port 5173)

## Requirements

- Docker Engine 20.10+
- Docker Compose 2.0+
- Python 3.13+
- Microphone and speaker
