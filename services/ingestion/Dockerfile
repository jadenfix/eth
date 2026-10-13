FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH=/app PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY services/ingestion/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && useradd --uid 10001 --create-home app
COPY services/__init__.py services/__init__.py
COPY services/ingestion services/ingestion
USER app
# This is a worker, not an HTTP server. Requires explicit RPC and Pub/Sub config.
CMD ["python", "-m", "services.ingestion.ethereum_ingester"]
