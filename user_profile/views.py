from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from .models import UserProfile
from .serializers import ProfileSerializer, UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser


class RegisterView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        request.data["first_name"] = request.data.get("username")
        request.data['username'] = request.data.get('email', '').split('@')[0]
        request.data['email'] = request.data.get('email', '')

        return super().create(request, *args, **kwargs)


class ProfileView(CreateAPIView, RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            serializer = self.get_serializer(user_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, *args, **kwargs):
        try:
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)

            serializer = self.get_serializer(
                user_profile, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
                return Response(serializer.data, status=status_code)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PasswordUpdateView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
