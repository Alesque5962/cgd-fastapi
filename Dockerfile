# Stage 1: Build Stage
FROM python:3.12.8-slim AS builder

WORKDIR /app

# uv installation
RUN pip install uv

# Copy uv project and configuration files
COPY pyproject.toml uv.lock README.md ./
COPY cgd_backend ./cgd_backend/

# Copy .env file
COPY .env ./

# Dependancies installation
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -e .

# Stage 2: Production Stage
FROM python:3.12.8-slim

WORKDIR /app

# Copy application from builder
COPY --from=builder /app/cgd_backend ./cgd_backend
# Copie system dependancies from builder
COPY --from=builder /usr/local /usr/local
# Copy .env file
COPY --from=builder /app/.env ./

# Configuration
ENV PYTHONPATH=/app
ENV PRODUCTION=true

# Création d'un utilisateur non-root
RUN groupadd -r app && \
    useradd -r -g app app && \
    chown -R app:app /app

USER app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "cgd_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]