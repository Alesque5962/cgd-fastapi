FROM python:3.12-slim

WORKDIR /app

# Installation de Poetry
RUN pip install poetry

# Copie des fichiers de configuration Poetry
COPY pyproject.toml poetry.lock ./
COPY cgd_backend ./cgd_backend/

# Configuration de Poetry pour créer le venv dans le projet
RUN poetry config virtualenvs.create false

# Installation des dépendances
RUN poetry install --no-root

# Copie du reste des fichiers
COPY . .

# Exposition du port
EXPOSE 8000

# Commande de démarrage
CMD ["poetry", "run", "uvicorn", "cgd_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]