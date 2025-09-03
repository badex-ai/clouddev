
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1


RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*


RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app


FROM base AS deps


COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt



#DEV
FROM deps AS development

COPY . .
RUN chown -R appuser:appgroup /app

USER appuser

ENV ENVIRONMENT=development \
    DEBUG=true \
    LOG_LEVEL=debug

EXPOSE 8000


HEALTHCHECK --interval=60s --timeout=30s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]



# PROD
FROM deps AS builder

COPY . .

RUN python -m compileall .

FROM base AS production

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


COPY --from=builder /app .


RUN chown -R appuser:appgroup /app

USER appuser


ENV ENVIRONMENT=production \
    DEBUG=false \
    LOG_LEVEL=info

EXPOSE 8000

# Health check (stricter for production)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Production command (using gunicorn for better performance)
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]