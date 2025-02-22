import subprocess
import json
from .constants import OLLAMA_MODELS
from ollama import chat
from ollama import ChatResponse
from .constants import OLLAMA_MODELS
from .schemas import ChatMessage


def query_ollama(model: str, prompt: str) -> str:
    if model not in OLLAMA_MODELS:
        return "Geçersiz model seçildi."

    model_name = OLLAMA_MODELS[model]
    command = ["ollama", "run", model_name, prompt]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Hata oluştu: {e.stderr}"


def get_response_from_model(model: OLLAMA_MODELS, prompt: list[ChatMessage]) -> str:
    response: ChatResponse = chat(
        model=model,
        messages=[msg.model_dump() for msg in prompt],
    )
    
    return response.message.content
