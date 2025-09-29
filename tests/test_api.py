from fastapi.testclient import TestClient
import pytest
from unittest.mock import Mock, patch
from cgd_backend.main import app

client = TestClient(app)
""" os.environ["PRODUCTION"] = "true" """


# Fixtures for mocks
@pytest.fixture
def mock_openai():
    with patch("cgd_backend.main.OpenAI") as mock:
        # OpenAI response mock
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response OpenAI"))]
        mock_instance = mock.return_value
        mock_instance.chat.completions.create.return_value = mock_response
        yield mock


@pytest.fixture
def mock_mistral():
    with patch("cgd_backend.main.Mistral") as mock:
        # Mistral response mock
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response Mistral"))]
        mock_instance = mock.return_value
        mock_instance.chat.complete.return_value = mock_response
        yield mock


@pytest.fixture
def mock_whisper():
    with patch("cgd_backend.main.OpenAI") as mock:
        mock_instance = mock.return_value
        mock_instance.audio.transcriptions.create.return_value = (
            "Test transcription Whisper"
        )
        yield mock


@pytest.fixture
def mock_voxtral():
    with patch("cgd_backend.main.Mistral") as mock:
        mock_instance = mock.return_value
        mock_instance.audio.transcriptions.complete.return_value = Mock(
            text="Test transcription Voxtral"
        )
        yield mock


@pytest.fixture
def audio_file():
    # Fake audio file for testing
    content = b"fake audio content"
    filename = "test.mp3"
    return {"content": content, "filename": filename}


# Endpoints tests
def test_chat_openai(mock_openai):
    response = client.post("/chatOpenAI", json={"prompt": "test question"})
    assert response.status_code == 200
    assert response.json() == {"response": "Test response OpenAI"}


def test_chat_mistral(mock_mistral):
    response = client.post("/chatMistral", json={"prompt": "test question"})
    assert response.status_code == 200
    assert response.json() == {"response": "Test response Mistral"}


def test_whisper(mock_whisper, audio_file):
    files = {"audioFile": (audio_file["filename"], audio_file["content"], "audio/mpeg")}
    response = client.post("/whisper", files=files)
    assert response.status_code == 200
    assert response.json() == {"response": "Test transcription Whisper"}


def test_voxtral(mock_voxtral, audio_file):
    files = {"audioFile": (audio_file["filename"], audio_file["content"], "audio/mpeg")}
    response = client.post("/voxtral", files=files)
    assert response.status_code == 200
    assert response.json() == {"response": "Test transcription Voxtral"}


# Errors tests
def test_chat_openai_empty_prompt():
    response = client.post("/chatOpenAI", json={"prompt": ""})
    assert response.status_code == 400
    assert response.json() == {"detail": "Prompt cannot be empty"}


def test_chat_mistral_empty_prompt():
    response = client.post("/chatMistral", json={"prompt": ""})
    assert response.status_code == 400
    assert response.json() == {"detail": "Prompt cannot be empty"}


def test_whisper_no_file():
    response = client.post("/whisper")
    assert response.status_code == 200
    assert response.json() == {"message": "No uploaded audioFile"}


def test_voxtral_no_file():
    response = client.post("/voxtral")
    assert response.status_code == 200
    assert response.json() == {"message": "No upload audioFile sent"}
