# =============================================================================
# Dita AI Assistant - Backend Dockerfile
# FastAPI WebSocket Server
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies
# -----------------------------------------------------------------------------
FROM python:3.13-slim AS builder

# Install uv package manager
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies directly without building wheel
RUN uv pip install --system --no-cache fastapi uvicorn[standard] python-multipart

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Slim production image
# -----------------------------------------------------------------------------
FROM python:3.13-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 dita && \
    mkdir -p /app && \
    chown -R dita:dita /app

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# Copy application code
COPY --chown=dita:dita . .

# Set environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app:$PYTHONPATH"

# Switch to non-root user
USER dita

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run FastAPI server
CMD ["python", "main.py"]
# - Terminal mode with wake word: ["python", "main.py"]
# - Streamlit demo: ["streamlit", "run", "streamlit_demo.py"]
# - Custom command: specify in docker-compose.yml command: override
