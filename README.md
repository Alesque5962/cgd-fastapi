# cgd-backend (C'est Grave Docteur)

Description :
-------------

API permettant à un utilisateur de poser une question, écrite ou vocale, à l'API Mistral (Chat ou Voxtral)  
Déploiement effectué sur Render, projet accessible [ici](https://cgd-svelte.onrender.com)  

Lancement du projet en mode developement :
------------------------------------------
Exécuter `poetry run uvicorn cgd_backend.main:app`  
Se rendre à l'adresse localhost:8000 (serveur FastAPI).  
Le gestionnaire de dépendances utilisé est Poetry => `backend/pyproject.toml`  


