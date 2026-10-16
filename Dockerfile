FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    HF_HOME=/models

COPY requirements.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

COPY rag ./rag
COPY agent ./agent
COPY frontend ./frontend
COPY ops ./ops

EXPOSE 8501

# Supervision : endpoint de santé de Streamlit (le démarrage initial peut durer plusieurs minutes)
HEALTHCHECK --interval=30s --timeout=5s --start-period=600s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health', timeout=3)"

# Initialisation automatique (idempotente) puis lancement de l'interface
CMD python ops/init.py && exec streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
