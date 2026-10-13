FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH=/app PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY services/ingestion/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && useradd --uid 10001 --create-home app
COPY services/__init__.py services/__init__.py
COPY services/ingestion services/ingestion
COPY services/agents services/agents
USER app
# Read-only heuristic worker; missing project/credentials must fail explicitly.
CMD ["python", "-m", "services.agents.mev_watch.agent"]
