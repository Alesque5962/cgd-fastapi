from functools import lru_cache
from fastapi import Depends, FastAPI, HTTPException, UploadFile
from typing_extensions import Annotated
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from mistralai import Mistral

""" import whisper """
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
async def chatOpenAI(
    request: ChatRequest, settings: Annotated[config.Settings, Depends(get_settings)]
):
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Le prompt ne peut pas être vide")

    client_openai = OpenAI(api_key=settings.openai_api_key)
    try:
        print("requête envoyée à l'API OpenAI")
        """ response = client_openai.chat.completions.create(
            # model à tester ="gpt-4o-mini", "gpt-4.1"
            model="gpt-3.5-turbo",  # Utilisation du modèle stable
            messages=[{"role": "user", "content": request.prompt}],
            temperature=0.7,
            max_tokens=1000,
        ) """
        # Affichage de la réponse générée par le modèle
        """ return {"response": response.choices[0].message.content} """
        print("request = ", request)
        return {"response": "coucou de l'API OpenAI !!"}

    except Exception as e:
        print(f"Erreur OpenAI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chatMistral")
async def chatMistral(
    request: ChatRequest, settings: Annotated[config.Settings, Depends(get_settings)]
):
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Le prompt ne peut pas être vide")

    client_mistral = Mistral(api_key=settings.mistral_api_key)
    try:
        print("requête envoyée à l'API Mistral AI")

        """ # Envoi d'une requête de complétion de chat au modèle spécifié
        # model="mistral-tiny", ou "mistral-small" ou "mistral-medium" ou "mistral-large-latest"
        response = client_mistral.chat.complete(
            model="mistral-small",  # Spécification du modèle à utiliser
            messages=[{"role": "user", "content": request.prompt}],
        )
        # Affichage de la réponse générée par le modèle
        return {"response": response.choices[0].message.content} """

        print("request = ", request)
        return {"response": "coucou de l'API Chat Mistral !!"}

    except Exception as e:
        print(f"Erreur Mistral AI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/whisper")
async def speechToTextWhisper(
    settings: Annotated[config.Settings, Depends(get_settings)],
    audioFile: UploadFile | None = None,
):
    if not audioFile:
        return {"message": "No upload audioFile sent"}
    else:
        try:
            """thisdir = os.path.abspath(os.path.dirname(__file__))
            outFilePath = os.path.join(thisdir, "whisper_mp3", audioFile.filename)
            # Si le dossier n'existe pas, on le crée
            os.makedirs(os.path.dirname(outFilePath), exist_ok=True)
            # On supprime le fichier s'il existe déjà
            if os.path.exists(outFilePath):
                os.remove(outFilePath)

            with open(outFilePath, "wb") as f:
                while contents := audioFile.file.read(1024 * 1024):
                    f.write(contents)

            print("outFilePath = ", outFilePath)

            # Utilisation de Whisper pour la transcription
            model = whisper.load_model("small")
            result = model.transcribe(outFilePath, language="fr")
            return {"response": result["text"]}"""

            print("requête envoyée à l'API Whisper")

            """ client_whisper = OpenAI(api_key=settings.whisper_api_key)
            transcript = client_whisper.audio.transcriptions.create(
                model="whisper-1",
                file=audioFile.file,
                response_format="text",
                language="fr",
            )
            return {"response": transcript} """

            return {"response": "coucou de l'API Whisper !!"}

        except Exception as e:
            print(f"Erreur Whisper: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/voxtral")
async def speechToTextVoxtral(
    settings: Annotated[config.Settings, Depends(get_settings)],
    audioFile: UploadFile | None = None,
):
    if not audioFile:
        return {"message": "No upload audioFile sent"}
    else:
        try:
            print("requête envoyée à l'API Voxtral")

            """ thisdir = os.path.abspath(os.path.dirname(__file__))
            mp3FilePath = os.path.join(thisdir, "mp3_folder", audioFile.filename)
            # Si le dossier n'existe pas, on le crée
            os.makedirs(os.path.dirname(mp3FilePath), exist_ok=True)
            # On supprime le fichier s'il existe déjà
            if os.path.exists(mp3FilePath):
                os.remove(mp3FilePath)

            with open(mp3FilePath, "wb") as f:
                while contents := audioFile.file.read(1024 * 1024):
                    f.write(contents)

            print("mp3FilePath = ", mp3FilePath)

            client_mistral = Mistral(api_key=settings.mistral_api_key)
            # Get the transcription
            with open(mp3FilePath, "rb") as f:
                transcription = client_mistral.audio.transcriptions.complete(
                    model="voxtral-mini-latest",
                    file={
                        "content": f,
                        "file_name": audioFile.filename,
                    },
                    language="fr",
                )

            print(transcription.text)
            return {"response": transcription.text} """

            return {"response": "coucou de l'API Voxtral !!"}

        except Exception as e:
            print(f"Erreur Whisper: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# This is important for Vercel
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
