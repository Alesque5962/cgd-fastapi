# cgd-backend (C'est Grave Docteur)

Description :
-------------

API permettant à un utilisateur de poser une question, écrite ou vocale, à l'API Mistral (Chat ou Voxtral)  
Déploiement effectué sur Render, projet accessible [ici](https://cgd-svelte.onrender.com)  

Lancement du projet en mode developement :
------------------------------------------

Le gestionnaire de dépendances utilisé est Poetry => `backend/pyproject.toml`    
`poetry run uvicorn cgd_backend.main:app`  
Se rendre à l'adresse localhost:8000 (serveur FastAPI).  

Lancement des tests unitaires côté backend avec le framework Pytest :
----------------------------------------------------

* Exécution de tous les tests  
`pytest`  

Construction du projet :
------------------------

Utilisation de Dagger pour gérer CI/CD  
Lancer les tests avec pytest => Builder une image docker => Push sur Dockerhub => Image utilisable avec docker-compose  

