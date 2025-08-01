# Stage 1: Build Stage
FROM python:3.12.8-slim AS builder
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/root/.local/bin:$PATH"

# Copie des fichiers de configuration Poetry
COPY pyproject.toml poetry.lock ./
COPY cgd_backend ./cgd_backend/

# Installation de Poetry
RUN pip install poetry --no-cache

# Installation des dépendances
RUN poetry install --no-cache --no-root

# Stage 2: Production Stage
FROM python:3.12.8-slim
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

# Installation de ffmpeg pour Whisper
RUN apt-get -y update \
    && apt-get -y upgrade \
    # && apt-get install -y --no-install-recommends ffmpeg \
    && apt-get clean

# Copy dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copie du reste des fichiers
COPY . .

# Exposition du port
EXPOSE 8000

# Commande de démarrage
CMD ["poetry", "run", "uvicorn", "cgd_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]