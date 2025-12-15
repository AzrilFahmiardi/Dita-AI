# Dita AI Assistant - Backend

Backend API untuk Dita AI Assistant Web Interface menggunakan FastAPI dengan WebSocket support.

## Instalasi

Dependencies sudah diatur di `pyproject.toml`:

```bash
cd "/home/azril/Azril/Magang/SDD/Dita/backend"

# Sync semua dependencies (termasuk backend)
uv sync
```

## Menjalankan Backend

```bash
# Dari root folder backend dengan uv
uv run python backend/main.py
```

Atau dengan start script:

```bash
./backend/start.sh
```

Backend akan berjalan di: `http://localhost:8000`

## API Endpoints

### HTTP Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health check
- `POST /api/chat` - Text-based chat (fallback)

### WebSocket

- `WS /ws/voice` - Real-time voice interaction

## WebSocket Message Format

### Client -> Server

```json
{
  "type": "audio",
  "audio": "base64_encoded_wav_audio"
}
```

### Server -> Client

```json
// Status update
{
  "type": "status",
  "message": "Mendengarkan..."
}

// Transcription result
{
  "type": "transcription",
  "text": "hasil transkripsi"
}

// Text response
{
  "type": "response",
  "text": "jawaban dari Dita",
  "response_time": 1.234,
  "status": "success"
}

// Audio response
{
  "type": "audio_response",
  "audio": "base64_encoded_wav_audio",
  "format": "wav"
}
```

## Environment Variables

Pastikan environment variables sudah di-set di file `.env` di root folder:

- `GEMINI_API_KEY` - Google Gemini API key
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to Google Cloud TTS credentials
- `ES_PASSWORD` - Elasticsearch password
- `PORCUPINE_ACCESS_KEY` - Porcupine wake word key (optional untuk web)

## Tech Stack

- **FastAPI** - Modern Python web framework
- **WebSocket** - Real-time bidirectional communication
- **Uvicorn** - ASGI server
