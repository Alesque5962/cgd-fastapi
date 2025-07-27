from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from mistralai import Mistral
import os

load_dotenv()

# Vérification de la configuration
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise Exception("OPENAI_API_KEY non trouvée dans le fichier .env")

mistral_api_key = os.getenv("MISTRAL_API_KEY")
if not mistral_api_key:
    raise Exception("MISTRAL_API_KEY non trouvée dans le fichier .env")


app = FastAPI()
client_openai = OpenAI(api_key=openai_api_key)
client_mistral = Mistral(api_key=mistral_api_key)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    prompt: str


@app.post("/chatOpenAI")
async def chat(request: ChatRequest):
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Le prompt ne peut pas être vide")

    try:
        response = client_openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Utilisation du modèle stable
            messages=[{"role": "user", "content": request.prompt}],
            temperature=0.7,
            max_tokens=1000,
        )
        return {"response": response.choices[0].message.content}

    except Exception as e:
        print(f"Erreur OpenAI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chatMistral")
async def chat(request: ChatRequest):
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Le prompt ne peut pas être vide")

    try:
        # Envoi d'une requête de complétion de chat au modèle spécifié
        # model="mistral-tiny", ou "mistral-small" ou "mistral-medium" ou "mistral-large-latest"
        response = client_mistral.chat.complete(
            model="mistral-small",  # Spécification du modèle à utiliser
            messages=[{"role": "user", "content": request.prompt}],
        )

        # Affichage de la réponse générée par le modèle
        """ return {"response": "Réponse de test Mistral"} """
        """ return {"response": response.choices[0].message.content} """
        print("request = ", request)
        return {"response": "coucou de l'API Mistral !!"}

    except Exception as e:
        print(f"Erreur Mistral AI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "ok"}
