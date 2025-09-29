# Stage 1: Build Stage
FROM python:3.12.8-slim AS builder

# uv installation
COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /uvx /bin/
WORKDIR /app

# Set environment variables
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy uv configuration files and project
COPY pyproject.toml uv.lock README.md ./
COPY cgd_backend ./cgd_backend/

# Dependancies installation
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Stage 2: Production Stage
FROM python:3.12.8-slim

# Copy the application from the builder
COPY --from=builder --chown=app:app /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Copy the rest of the files
COPY . .

EXPOSE 8000

CMD ["fastapi", "run", "cgd_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]