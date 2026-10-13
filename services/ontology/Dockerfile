FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH=/app PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 GRAPH_DB_PATH=/data/ontology.sqlite
COPY services/ontology/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && useradd --uid 10001 --create-home app && mkdir /data && chown app:app /data
COPY services/__init__.py services/__init__.py
COPY services/ontology services/ontology
COPY services/graph_api services/graph_api
USER app
VOLUME ["/data"]
EXPOSE 8000
HEALTHCHECK --interval=5s --timeout=3s --start-period=15s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"
CMD ["python", "-m", "uvicorn", "services.ontology.graph_api:app", "--host", "0.0.0.0", "--port", "8000"]
