from functools import lru_cache
import logging
from fastapi import Depends, FastAPI, HTTPException, UploadFile
from typing_extensions import Annotated
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from mistralai import Mistral
import uvicorn
import os
from . import config

app = FastAPI()


@lru_cache
def get_settings():
    return config.Settings()


# Production mode or not
isProd = config.Settings().production.lower()

# Configure logging
level = logging.WARNING if isProd == "true" else logging.DEBUG
logging.basicConfig(level=level)
logger = logging.getLogger(__name__)

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
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    else:
        client_openai = OpenAI(api_key=settings.openai_api_key)
        if isProd == "true":
            try:
                response = client_openai.chat.completions.create(
                    # Availables models = "gpt-4o-mini", "gpt-4.1"
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": request.prompt}],
                    temperature=0.7,
                    max_tokens=1000,
                )
                return {"response": response.choices[0].message.content}

            except Exception as e:
                logger.error(f"Erreur OpenAI: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        else:
            logger.info("request sent to OpenAI API")
            logger.info(f"request = {request}")
            return {
                "response": "OpenAI Chat API is working but not connected in development mode"
            }


@app.post("/chatMistral")
async def chatMistral(
    request: ChatRequest, settings: Annotated[config.Settings, Depends(get_settings)]
):
    if not request.prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    else:
        client_mistral = Mistral(api_key=settings.mistral_api_key)
        if isProd == "true":
            try:
                response = client_mistral.chat.complete(
                    # Availables models = "mistral-tiny", "mistral-small", "mistral-medium", "mistral-large-latest"
                    model="mistral-small",
                    messages=[{"role": "user", "content": request.prompt}],
                )
                return {"response": response.choices[0].message.content}

            except Exception as e:
                logger.error(f"Erreur Mistral AI: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        else:
            logger.info("request sent to Mistral AI API")
            logger.info(f"request = {request}")
            return {
                "response": "Mistral Chat API is working but not connected in development mode"
            }


@app.post("/whisper")
async def speechToTextWhisper(
    settings: Annotated[config.Settings, Depends(get_settings)],
    audioFile: UploadFile | None = None,
):
    if not audioFile:
        return {"message": "No uploaded audioFile"}

    else:
        if isProd == "true":
            try:
                client_whisper = OpenAI(api_key=settings.whisper_api_key)
                transcript = client_whisper.audio.transcriptions.create(
                    model="whisper-1",
                    file=audioFile.file,
                    response_format="text",
                    language="fr",
                )
                return {"response": transcript}

            except Exception as e:
                logger.error(f"Erreur Whisper: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        else:
            logger.info("request sent to OpenAI Whisper API")
            return {
                "response": "OpenAI Whisper API is working but not connected in development mode"
            }


@app.post("/voxtral")
async def speechToTextVoxtral(
    settings: Annotated[config.Settings, Depends(get_settings)],
    audioFile: UploadFile | None = None,
):
    if not audioFile:
        return {"message": "No upload audioFile sent"}
    else:
        if isProd == "true":
            try:
                thisdir = os.path.abspath(os.path.dirname(__file__))
                mp3FilePath = os.path.join(thisdir, "mp3_folder", audioFile.filename)
                os.makedirs(os.path.dirname(mp3FilePath), exist_ok=True)
                if os.path.exists(mp3FilePath):
                    os.remove(mp3FilePath)

                with open(mp3FilePath, "wb") as f:
                    while contents := audioFile.file.read(1024 * 1024):
                        f.write(contents)

                client_mistral = Mistral(api_key=settings.mistral_api_key)
                with open(mp3FilePath, "rb") as f:
                    # Get the transcription
                    transcription = client_mistral.audio.transcriptions.complete(
                        model="voxtral-mini-latest",
                        file={
                            "content": f,
                            "file_name": audioFile.filename,
                        },
                        language="fr",
                    )
                return {"response": transcription.text}

            except Exception as e:
                logger.error(f"Erreur Whisper: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        else:
            logger.info("request sent to Voxtral API")
            return {
                "response": "Voxtral API is working but not connected in development mode"
            }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Important for Vercel deployment
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
