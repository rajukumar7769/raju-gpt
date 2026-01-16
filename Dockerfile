# Stage 1: Base image with dependencies
FROM python:3.9-slim as builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    pkg-config \
    libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements-prod.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements-prod.txt

# Stage 2: Runtime image
FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=raju_gpt_proj.settings

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libcairo2 \
    libcairo2-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /app/staticfiles /app/media /app/django_cache && \
    chown -R appuser:appuser /app

WORKDIR /app

COPY --chown=appuser:appuser . .

COPY --chown=appuser:appuser docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

USER appuser

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/').raise_for_status()" || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]

CMD ["gunicorn", "raju_gpt_proj.wsgi:application", "--bind", "0.0.0.0:7860", "--workers", "2", "--timeout", "120"]
