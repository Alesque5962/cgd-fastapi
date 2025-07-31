from functools import lru_cache
from fastapi import Depends, FastAPI, HTTPException, UploadFile
from typing_extensions import Annotated
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from mistralai import Mistral
import whisper
import uvicorn
import os
from . import config

app = FastAPI()


@lru_cache
def get_settings():
    return config.Settings()


# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.Settings().allow_origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    prompt: str


@app.post("/chatOpenAI")
async def chat(
    request: ChatRequest, settings: Annotated[config.Settings, Depends(get_settings)]
):
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Le prompt ne peut pas être vide")

    client_openai = OpenAI(api_key=settings.openai_api_key)
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
async def chat(
    request: ChatRequest, settings: Annotated[config.Settings, Depends(get_settings)]
):
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Le prompt ne peut pas être vide")

    client_mistral = Mistral(api_key=settings.mistral_api_key)
    try:
        print("coucou chat mistal")
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
        """ print("settings.mistral_api_key = ", settings.mistral_api_key) """
        return {"response": "coucou de l'API Mistral !!"}

    except Exception as e:
        print(f"Erreur Mistral AI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/whisper")
async def speechToText(audioFile: UploadFile | None = None):
    if not audioFile:
        return {"message": "No upload audioFile sent"}
    else:
        try:
            print("coucou de l'API Whisper")
            thisdir = os.path.abspath(os.path.dirname(__file__))
            outFilePath = os.path.join(thisdir, "whisper_mp3", audioFile.filename)
            # Si le dossier n'existe pas, on le crée
            os.makedirs(os.path.dirname(outFilePath), exist_ok=True)
            # On supprime le fichier s'il existe déjà
            if os.path.exists(outFilePath):
                os.remove(outFilePath)

            """ contents = audioFile.file.read()
            with open(outFilePath, "wb") as f:
                f.write(contents) """

            with open(outFilePath, "wb") as f:
                while contents := audioFile.file.read(1024 * 1024):
                    f.write(contents)

            print("outFilePath = ", outFilePath)

            # Utilisation de Hugging face pour la transcription
            """ transcriber = pipeline(
                "automatic-speech-recognition", model="openai/whisper-small"
            )
            result = transcriber(outFilePath) """
            # Utilisation de Whisper pour la transcription
            """ model = whisper.load_model("small") """
            model = whisper.load_model("tiny")
            result = model.transcribe(outFilePath, language="fr")

            return {"response": result["text"]}

        except Exception as e:
            print(f"Erreur Whisper: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# This is important for Vercel
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
