# DITA AI Assistant

Multi-role voice-enabled AI assistant system with comprehensive web dashboard for Indonesian National Police (POLRI).

## System Overview

DITA (Digital Intelligence and Technical Assistant) is an enterprise-grade AI assistant system featuring voice interaction, role-based access control, real-time session synchronization, and multi-user management capabilities.

**Key Features:**
- Wake word-activated voice interaction
- Speech-to-text with Google Speech API
- RAG-based question answering using Google Gemini AI
- Text-to-speech with Google Cloud TTS
- Role-based authentication (KAPOLRI, KAPOLDA, KAPOLRES)
- Real-time WebSocket synchronization between frontend and voice assistant
- User and contact management with permission-based access control
- Comprehensive audit logging
- WhatsApp integration for notifications

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Host Machine                                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Voice Assistant (Python)                                     │  │
│  │ - Wake word detection (Porcupine)                            │  │
│  │ - Speech-to-text (Google Speech API)                         │  │
│  │ - RAG + Gemini AI for Q&A                                    │  │
│  │ - Text-to-speech (Google Cloud TTS)                          │  │
│  │ - Session monitor (WebSocket client)                         │  │
│  └────────────┬─────────────────────────────┬───────────────────┘  │
│               │ HTTP/WebSocket              │ File IPC             │
│               │                             │ (~/.dita/*.json)     │
└───────────────┼─────────────────────────────┼──────────────────────┘
                │                             │
                ▼                             ▼
┌───────────────────────────────────────────────────────────────────────┐
│                      Docker Environment                               │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ Backend (FastAPI) - Port 8000                                  │  │
│  │ - REST API endpoints                                           │  │
│  │ - WebSocket broadcaster (session events, voice state)          │  │
│  │ - JWT authentication                                           │  │
│  │ - Role-based access control                                    │  │
│  │ - Session manager (shared state via file)                      │  │
│  │ - User/Contact/Audit services                                  │  │
│  └───────┬────────────────────┬───────────────────────────────────┘  │
│          │                    │                                       │
│          │                    │                                       │
│  ┌───────▼────────┐  ┌────────▼────────────────────────────────┐    │
│  │ PostgreSQL     │  │ Frontend (React + Vite) - Port 5173     │    │
│  │ Port 5432      │  │ - User authentication                   │    │
│  │ - Users        │  │ - Role-based dashboard                  │    │
│  │ - Roles        │  │ - Voice assistant interface             │    │
│  │ - Contacts     │  │ - User management                       │    │
│  │ - Audit logs   │  │ - Contact management                    │    │
│  └────────────────┘  │ - Audit logs viewer                     │    │
│                      │ - WebSocket client (real-time updates)  │    │
│                      └─────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────┘
```

### Data Flow

**Voice Interaction:**
```
User says "Hey Dita" → Wake word detected → Recording → STT → 
RAG Processing (Elasticsearch + Gemini) → Response → TTS → Audio output
```

**Session Synchronization:**
```
Frontend login → Backend saves session → WebSocket broadcast → 
Voice assistant receives event → Auto-initialize with user context
```

**Text Query (from dashboard):**
```
Frontend text input → Backend writes to ~/.dita/text_query.json → 
Voice assistant monitors file → Processes query → Writes response to 
~/.dita/text_response.json → Backend reads and returns to frontend
```

## Project Structure

```
Dita/
├── voice-assistant/              # Voice I/O and AI processing (runs on host)
│   ├── main.py                   # Main entry point with session monitoring
│   ├── wakeword.py               # Porcupine wake word detection
│   ├── stt.py                    # Google Speech-to-Text
│   ├── rag.py                    # RAG with Gemini AI and Elasticsearch
│   ├── tts.py                    # Google Cloud Text-to-Speech
│   ├── vad_recorder.py           # Voice activity detection
│   ├── auth.py                   # Authentication client
│   ├── session_monitor.py        # WebSocket session listener
│   ├── config_manager.py         # Configuration management
│   ├── fonnte_client.py          # WhatsApp integration
│   ├── config.yaml               # Voice assistant configuration
│   ├── pyproject.toml            # Python dependencies
│   └── models/                   # Porcupine wake word models
│
├── backend/                      # FastAPI REST API and WebSocket server (Docker)
│   ├── main.py                   # FastAPI application
│   ├── broadcaster.py            # WebSocket broadcaster
│   ├── session_manager.py        # Session state management
│   ├── auth/                     # Authentication module
│   │   ├── security.py           # JWT token handling
│   │   ├── dependencies.py       # Auth dependencies
│   │   └── schemas.py            # Pydantic schemas
│   ├── database/                 # Database module
│   │   └── models.py             # SQLAlchemy models
│   ├── services/                 # Business logic
│   │   ├── user_service.py       # User CRUD with role-based scoping
│   │   ├── whatsapp_service.py   # Contact management
│   │   └── audit_service.py      # Audit log service
│   ├── migrations/               # Alembic database migrations
│   ├── Dockerfile                # Backend container definition
│   └── pyproject.toml            # Backend dependencies
│
├── frontend/                     # React web dashboard (Docker)
│   ├── src/
│   │   ├── main.jsx              # React entry point
│   │   ├── App.jsx               # App router
│   │   ├── components/           # Reusable UI components
│   │   │   ├── common/           # Buttons, inputs, modals
│   │   │   ├── layout/           # Sidebar, header, layouts
│   │   │   ├── forms/            # User forms, contact forms
│   │   │   └── tables/           # Data tables
│   │   ├── pages/                # Route pages
│   │   │   ├── LoginPage.jsx     # Authentication
│   │   │   ├── VoiceAssistantPage.jsx  # Voice interface
│   │   │   ├── DashboardPage.jsx       # Main dashboard
│   │   │   ├── UserManagement.jsx      # User CRUD
│   │   │   ├── ContactManagement.jsx   # Contact CRUD
│   │   │   └── AuditLogs.jsx           # Audit viewer
│   │   ├── contexts/             # React contexts
│   │   │   └── AuthContext.jsx   # Authentication state
│   │   ├── services/             # API clients
│   │   │   ├── api.js            # Axios instance
│   │   │   ├── auth.service.js   # Auth API
│   │   │   ├── user.service.js   # User API
│   │   │   └── audit.service.js  # Audit API
│   │   ├── hooks/                # Custom React hooks
│   │   │   └── useVoiceChat.js   # WebSocket hook
│   │   └── routes/               # Route protection
│   │       ├── ProtectedRoute.jsx
│   │       └── KapolriRoute.jsx
│   ├── Dockerfile                # Frontend container definition
│   ├── nginx.conf                # Nginx configuration
│   ├── package.json              # NPM dependencies
│   └── vite.config.js            # Vite build config
│
├── docker-compose.yml            # Multi-container orchestration
├── .env                          # Environment variables (not in repo)
└── README.md                     # This file
```

## Prerequisites

**System Requirements:**
- Docker Engine 20.10+
- Docker Compose 2.0+
- Python 3.13+
- Microphone and speaker (for voice assistant)
- 4GB RAM minimum
- Linux, macOS, or Windows with WSL2

**API Keys Required:**
- Porcupine Access Key (wake word detection)
- Google Gemini API Key (AI processing)
- Google Cloud credentials JSON (Text-to-Speech)
- Elasticsearch instance (optional, for news search)
- Fonnte API token (optional, for WhatsApp)

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd Dita
```

### 2. Environment Configuration

Create `.env` file in root directory:

```env
# Database
POSTGRES_DB=dita_db
POSTGRES_USER=dita_user
POSTGRES_PASSWORD=your_secure_password

# JWT Authentication
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15

# API Keys
PORCUPINE_ACCESS_KEY=your_porcupine_key
GEMINI_API_KEY=your_gemini_key
ES_PASSWORD=your_elasticsearch_password

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/app/gc-tts-credential.json

# Frontend URLs
VITE_WEBSOCKET_URL=ws://localhost:8000/ws/dashboard
VITE_API_BASE_URL=http://localhost:8000

# Optional: WhatsApp Integration
FONNTE_TOKEN=your_fonnte_token
```

### 3. Start Docker Services

```bash
# Build and start all containers
docker compose up -d

# Verify services are running
docker compose ps

# Check logs if needed
docker compose logs -f backend
docker compose logs -f frontend
```

### 4. Database Initialization

The database is automatically initialized with:
- Default roles (KAPOLRI, KAPOLDA, KAPOLRES)
- Admin user (username: `kapolri_admin`, password: `Admin123!`)

### 5. Install Voice Assistant Dependencies

```bash
cd voice-assistant
uv sync
```

### 6. Configure Voice Assistant

Edit `voice-assistant/config.yaml` to customize:
- Wake word sensitivity
- STT/TTS settings
- RAG parameters
- Elasticsearch connection

## Usage

### Starting the System

**Step 1: Start Docker containers**
```bash
docker compose up -d
```

**Step 2: Access web dashboard**
- URL: http://localhost:5173
- Login with default credentials:
  - Username: `kapolri_admin`
  - Password: `Admin123!`

**Step 3: Start voice assistant**
```bash
cd voice-assistant
uv run python main.py
```

The voice assistant will:
- Check for active session from dashboard
- If logged in: Auto-initialize with user context
- If not logged in: Wait for login event from dashboard
- Start listening for "Hey Dita" wake word

### Voice Interaction

1. Say **"Hey Dita"** to activate
2. Speak your question or command
3. Wait for response
4. Voice assistant returns to listening state

**Supported queries:**
- News search: "Berita tentang polisi"
- General questions: "Apa itu RAG?"
- System commands: "Keluar" to stop

### Web Dashboard Features

**All Users:**
- Voice assistant interface with real-time state display
- Fullscreen response view when AI answers
- Session synchronization with terminal

**KAPOLRI (Level 1) - Full Access:**
- User management (create, edit, delete all users)
- Contact management (manage all contacts)
- Audit logs (view all system activities)
- Statistics dashboard (system-wide metrics)

**KAPOLDA (Level 2) - Regional Access:**
- View KAPOLRES users only
- Manage regional contacts
- View regional audit logs
- Regional statistics

**KAPOLRES (Level 3) - Unit Access:**
- View own profile
- View assigned contacts
- View own activity logs
- Unit statistics

## API Documentation

### Access Swagger UI

Open http://localhost:8000/docs for interactive API documentation.

### Key Endpoints

**Authentication:**
- `POST /auth/login` - Login with username/password
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout (broadcasts session event)
- `GET /auth/active-session` - Check active session

**Users:**
- `GET /api/users` - List users (role-based filtering)
- `POST /api/users` - Create user (KAPOLRI only)
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user (KAPOLRI only)

**Contacts:**
- `GET /api/contacts` - List contacts (scoped by role)
- `POST /api/contacts` - Create contact
- `PUT /api/contacts/{id}` - Update contact
- `DELETE /api/contacts/{id}` - Delete contact

**Audit Logs:**
- `GET /api/audit-logs` - List audit logs (filtered by role level)

**WebSocket:**
- `ws://localhost:8000/ws/dashboard` - Real-time updates

## Role-Based Access Control

### Permission Matrix

| Feature | KAPOLRI | KAPOLDA | KAPOLRES |
|---------|---------|---------|----------|
| Manage all users | Yes | No | No |
| Manage KAPOLRES users | Yes | Yes | No |
| Manage all contacts | Yes | No | No |
| Manage regional contacts | Yes | Yes | No |
| View all audit logs | Yes | No | No |
| View regional audit logs | Yes | Yes | No |
| View own audit logs | Yes | Yes | Yes |
| Export data | Yes | Yes | No |
| Send WhatsApp | Yes | Yes | No |

### Data Scoping

**Backend automatically filters data based on user role:**
- KAPOLRI (level 1): Sees all data
- KAPOLDA (level 2): Sees only KAPOLRES users and regional data
- KAPOLRES (level 3): Sees only own profile and assigned contacts

## Session Synchronization

### How It Works

1. **Frontend Login:**
   - User logs in via web dashboard
   - Backend creates JWT tokens
   - Backend saves session to `~/.dita/session.json`
   - Backend broadcasts `session:login` event via WebSocket

2. **Voice Assistant Activation:**
   - SessionMonitor receives `session:login` event
   - Auto-initializes auth client with user context
   - Auto-initializes RAG with user permissions
   - Starts wake word detection

3. **Frontend Logout:**
   - User clicks logout in dashboard
   - Frontend calls `/auth/logout` endpoint
   - Backend clears `~/.dita/session.json`
   - Backend broadcasts `session:logout` event
   - Voice assistant receives event and pauses wake word detection

### Benefits

- Zero manual login in voice assistant
- Automatic context switching when users change
- Synchronized state between frontend and terminal
- Audit trail of all voice interactions

## Development

### Running in Development Mode

**Backend:**
```bash
cd backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

**Voice Assistant:**
```bash
cd voice-assistant
uv run python main.py
```

### Database Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

### Adding New Users

Via API:
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nrp": "1234567890",
    "username": "new_user",
    "password": "SecurePass123!",
    "full_name": "Full Name",
    "role_id": 3
  }'
```

Via Dashboard:
1. Login as KAPOLRI
2. Navigate to User Management
3. Click "Create New User"
4. Fill form and submit
