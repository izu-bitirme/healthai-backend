# base/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from ai_models.chat_bot.constants import AVAILABLE_MODELS

class ChatRequestSerializer(serializers.Serializer):
    model = serializers.ChoiceField(choices=["deepseek", "llama3"])
    prompt = serializers.CharField()


class ChatBotAPIView(APIView):
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if serializer.is_valid():
            model = serializer.validated_data["model"]
            prompt = serializer.validated_data["prompt"]

            bot = ChatBotManager(model=model)
            response_text = bot.get_response(prompt)

            return Response({"response": response_text}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppDataView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response(
            {
                "latest_version": "1.0.0",
                "ai_models": list(AVAILABLE_MODELS)
            }
        )
