# Stage 1: Build Stage
FROM python:3.12.8-slim AS builder
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/root/.local/bin:$PATH"

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock ./
COPY cgd_backend ./cgd_backend/

# Poetry installation
RUN pip install poetry --no-cache

# Dependancies installation
RUN poetry install --no-cache --no-root

# Stage 2: Production Stage
FROM python:3.12.8-slim
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

# Copy dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the rest of the files
COPY . .

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "cgd_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]