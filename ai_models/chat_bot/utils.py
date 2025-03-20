import subprocess
import json
from .constants import OLLAMA_MODELS
from ollama import chat
from ollama import ChatResponse
from .constants import OLLAMA_MODELS
from .schemas import ChatMessage
import requests
import os


def get_gpt4_response(_, prompt: list[ChatMessage]) -> str:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        json={
            "model": "gpt-4",
            "messages": [p.model_dump() for p in prompt],
            "temperature": 1,
            "max_tokens": 100,
        },
    )
    if not response.ok:
        return f"OpenAI API'den yanıt alınamadı. Hata kodu: {response.status_code}"

    data = response.json()
    return data["choices"][0]["message"]["content"]


MODEL_FUNCTION_MAPPING = {"gpt-4": get_gpt4_response}


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


def get_ollama_response(model: OLLAMA_MODELS, prompt: str) -> str:
    response: ChatResponse = chat(
        model=model,
        messages=[msg.model_dump() for msg in prompt],
    )

    return response.message.content


def get_response_from_model(model: OLLAMA_MODELS, prompt: list[ChatMessage]) -> str:
    func = MODEL_FUNCTION_MAPPING.get(model) or get_ollama_response
    return func(model, prompt)
