from pydantic import BaseModel
from .constants import ROLES


class ChatMessage(BaseModel):
    role: ROLES
    content: str