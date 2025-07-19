FROM python:3.11-slim AS base

# ---- System dependencies --------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential curl git \
    && rm -rf /var/lib/apt/lists/*

# ---- Poetry installation --------------------------------------------------------
ENV POETRY_VERSION=1.6.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

WORKDIR /app

# ---- Dependencies layer (highly cacheable) ---------------------------------
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root --only main && rm -rf $POETRY_CACHE_DIR

# ---- Application layer --------------------------------------------------------
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

COPY . .
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Use exec form for better signal handling
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]