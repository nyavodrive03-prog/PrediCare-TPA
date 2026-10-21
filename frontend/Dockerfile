FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/root/.cache/huggingface

WORKDIR /app

# Dépendances système minimales (psycopg2, healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 1. PyTorch CPU EN PREMIER (évite le téléchargement des paquets CUDA lourds)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# 2. Dépendances Python (hors sentence-transformers)
COPY frontend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 3. sentence-transformers APRÈS torch CPU
RUN pip install --no-cache-dir sentence-transformers

# Code applicatif
COPY frontend/ /app/frontend/
COPY rag/ /app/rag/
COPY agent/ /app/agent/

# Streamlit écoute sur 8501
EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --retries=5 \
    CMD curl -fsS http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]