from pydantic import BaseModel
from typing import Literal
from user_profile.models import UserProfile


class Role:
    user: str = "user"


class ChatModel(BaseModel):
    display_name: str
    code: str


class ChatModels:
    llama3: str = "llama3.2"
    deepseek: str = "deepseek-r1"
    gemma: str = "gemma3"
    ollama_turkish: str = "erdiari/llama3-turkish"
    open_ai_gpt4: str = "gpt-4"


AVAILABLE_MODELS = [
    ChatModels.ollama_turkish,
    ChatModels.deepseek,
    ChatModels.llama3,
    ChatModels.gemma,
    ChatModels.open_ai_gpt4,
]

OLLAMA_MODELS = Literal[
    ChatModels.ollama_turkish,
    ChatModels.deepseek,
    ChatModels.llama3,
    ChatModels.gemma,
    ChatModels.open_ai_gpt4,
]

ROLES = Literal[Role.user]


# from ai_models.chat_bot.utils import get_response_from_model
