from .utils import get_response_from_model
from .prompts import generate_user_chat_prompt
from .constants import OLLAMA_MODELS, Role, ChatModels
from .schemas import ChatMessage

class ChatBotManager:
    @classmethod
    def get_response(cls, prompt: str, model: OLLAMA_MODELS = ChatModels.llama3) -> str:
        return get_response_from_model(
            model=model,
            prompt=[
                ChatMessage(role=Role.user, content=generate_user_chat_prompt(prompt)),
            ]
        )