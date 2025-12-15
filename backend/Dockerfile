# =============================================================================
# Dita AI Assistant - Backend Dockerfile (Multi-stage)
# Python 3.13 + FastAPI + LangChain + Elasticsearch
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies with uv
# -----------------------------------------------------------------------------
FROM python:3.13-slim AS builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies with uv (creates .venv)
# Increase timeout for large packages (tokenizers, torch, transformers)
ENV UV_HTTP_TIMEOUT=600
ENV UV_CONCURRENT_DOWNLOADS=1
ENV UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
RUN uv sync --no-dev --frozen || uv sync --no-dev --frozen

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Slim production image
# -----------------------------------------------------------------------------
FROM python:3.13-slim

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    # Audio libraries for PyAudio
    portaudio19-dev \
    libportaudio2 \
    alsa-utils \
    # Network tools for health checks
    curl \
    # Other utilities
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 dita && \
    mkdir -p /app /app/data /app/models && \
    chown -R dita:dita /app

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=dita:dita . .

# Ensure models directory exists and has correct permissions
RUN chown -R dita:dita /app/models /app/data

# Set Python path and use venv
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app:$PYTHONPATH" \
    PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER dita

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command: Run FastAPI backend
CMD ["python", "backend/main.py"]

# Alternative commands (can override in docker-compose.yml):
# - Terminal mode with wake word: ["python", "main.py"]
# - Streamlit demo: ["streamlit", "run", "streamlit_demo.py"]
# - Custom command: specify in docker-compose.yml command: override
