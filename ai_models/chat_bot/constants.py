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
    deepseek: str = "deepseek-r1:latest"
    gemma: str = "gemma3:latest"
    qwq: str = "qwq:latest"
    ollama_turkish: str = "erdiari/llama3-turkish:latest"

AVAILABLE_MODELS = [
    ChatModels.llama3,
    ChatModels.deepseek,
    ChatModels.gemma,
    ChatModels.qwq,
    ChatModels.ollama_turkish
]

OLLAMA_MODELS = Literal[
    ChatModels.llama3,
    ChatModels.deepseek,
    ChatModels.gemma,
    ChatModels.qwq,
    ChatModels.ollama_turkish
]

ROLES = Literal[Role.user]


# from ai_models.chat_bot.utils import get_response_from_model
