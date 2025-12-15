di doct# Dita AI Assistant

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

## Quick Start

### 1. Start Docker Infrastructure

```bash
# Start WebSocket server and dashboard
docker compose up -d

# Check status
docker compose ps
```

### 2. Install Dependencies (First time only)

```bash
cd backend
uv sync
```

### 3. Run Voice Assistant

```bash
cd backend
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

Configure `.env` file:
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
