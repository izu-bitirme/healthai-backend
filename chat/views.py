# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import os
import jwt
from rest_framework.permissions import IsAuthenticated
from .serializers import VideoCallSerializer
from .models import VideoCall


class StartCallView(APIView):
    serializer_class = VideoCallSerializer
    permission_classes = [IsAuthenticated]


    def get(self, request):
        try:
            receiver_id = request.query_params.get("receiver_id")
            if not receiver_id:
                return Response(
                    {"error": "Receiver ID is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Create consistent call ID by sorting user IDs alphabetically
            user_ids = sorted([str(request.user.id), receiver_id])
            call_id = f"call_{user_ids[0]}_{user_ids[1]}"

            # Create or get the call record
            VideoCall.objects.get_or_create(
                call_id=call_id,
                defaults={
                    "caller": request.user,
                    "receiver_id": receiver_id,
                    "status": "initiated",
                },
            )
            return Response(
                {
                    "app_id": int(os.getenv("ZEGO_APP_ID")),
                    "app_sign": os.getenv("ZEGO_APP_SIGN"),
                    "user_id": str(request.user.id),
                    "user_name": request.user.username,
                    "call_id": call_id,
                    "other_user_id": receiver_id,
                }
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



