FROM python:3.11-slim AS base

# ---- tooling --------------------------------------------------------
# No virtual environment at runtime - install directly to system site-packages
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.6.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential curl git \
    && pip install --no-cache-dir "poetry==$POETRY_VERSION" \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ---- install deps first (cacheable) ---------------------------------
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root --only main        # uvicorn is included here

# ---- copy source & create non‑root user -----------------------------
COPY . .
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]