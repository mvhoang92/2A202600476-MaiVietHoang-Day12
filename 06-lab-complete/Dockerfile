# ============================================================
# Production Dockerfile — Multi-stage, < 500 MB, non-root
# ============================================================

# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# Stage 2: Runtime
FROM python:3.11-slim AS runtime

# Create user with real home directory
RUN groupadd -r agent && useradd -m -r -g agent agent

WORKDIR /app

# Copy packages from builder to agent's home
COPY --from=builder /root/.local /home/agent/.local

# Copy application and utils
COPY app/ ./app/
COPY utils/ ./utils/

# Correct ownership
RUN chown -R agent:agent /app /home/agent/.local

USER agent

# Set paths for user install
ENV PATH="/home/agent/.local/bin:${PATH}"
ENV PYTHONPATH="/app:/home/agent/.local/lib/python3.11/site-packages"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c \
    "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" \
    || exit 1

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2
