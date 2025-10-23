# cgd-backend (C'est Grave Docteur)

Description :
-------------

API backend permettant à un utilisateur de poser une question, écrite ou vocale, à l'API Mistral (Chat ou Voxtral).  
Déploiement de l'application complète effectué sur Render, accessible [ici](https://cgd-svelte.onrender.com)  

Run le projet en mode développement :
-------------------------------------

Le gestionnaire de dépendances utilisé est uv => `pyproject.toml`    
`uv run uvicorn cgd_backend.main:app`  
Se rendre à l'adresse localhost:8000 (serveur FastAPI).  

Tests unitaires côté backend avec le framework Pytest :
-------------------------------------------------------

* Exécution de tous les tests unitaires  
`uv run pytest`  

* Exécution d'un seul test unitaire  
`uv run pytest tests/test_api.py`  

Pipeline CI/CD :
----------------

Utilisation de Dagger.  

* Exécution des tests unitaires  
`dagger call run-tests`  

* Exécution du pipeline complet  
`dagger call docker-build-publish`  
Lance les tests avec pytest, build une image docker, publie l'image sur Dockerhub.  
