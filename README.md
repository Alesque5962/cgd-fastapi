# cgd-backend (C'est Grave Docteur)

Description :
-------------

Backend permettant à un utilisateur de poser une question, écrite ou vocale, à l'API Mistral (Chat ou Voxtral).  
Déploiement de l'application complète effectué sur Render, projet accessible [ici](https://cgd-svelte.onrender.com)  

Lancement du projet en mode développement :
-------------------------------------------

Le gestionnaire de dépendances utilisé est uv => `pyproject.toml`    
`uv run uvicorn cgd_backend.main:app`  
Se rendre à l'adresse localhost:8000 (serveur FastAPI).  

Lancement des tests unitaires côté backend avec le framework Pytest :
---------------------------------------------------------------------

* Exécution de tous les tests unitaires  
`uv run pytest`  

* Exécution d'un seul test unitaire  
`uv run pytest tests/test_api.py`  

Pipeline CI/CD :
----------------

Utilisation de Dagger.  

* Exécution des tests unitaires  
`dagger call run_tests`  

* Exécution du pipeline complet  
`dagger call docker-build-publish`  
Lance les tests avec pytest, build une image docker, push sur Dockerhub.  

Construction de l'application complète (frontend + backend) localement :
---------------------------------------------------

`docker compose up -d`
Se rendre à l'adresse localhost:8080 (serveur Nginx).  
