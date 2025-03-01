

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..manager import ChatBotManager


@api_view(["GET"])
def get_chat_message(request):
    message = request.data.get("message") or request.GET.get("message") 
    model = request.data.get("model") or request.GET.get("model")
    
    return Response(
        {
            "message": ChatBotManager.get_response(message, **({"model": model} if model else {})) if message else None,
        },
        status=status.HTTP_200_OK
    )