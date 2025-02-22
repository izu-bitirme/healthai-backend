
from pydantic import BaseModel
from typing import Literal
from user_profile.models import UserProfile


class Role:
    user: str = "user"

class ChatModels:
    llama3: str = "llama3.2"

OLLAMA_MODELS  = Literal[ChatModels.llama3]
ROLES = Literal[Role.user]



# from ai_models.chat_bot.utils import get_response_from_model