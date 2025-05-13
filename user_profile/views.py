from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from .models import UserProfile, Doctor, Patient, Therapist
from .serializers import ProfileSerializer, UserSerializer,DoctorSerializer,PatientSerializer,TherapistSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.db.models import F, Sum, CharField, Value
from django.db.models.functions import Concat




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
            serializer = self.get_serializer(user_profile, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                role = serializer.validated_data.get("role") or user_profile.role
                if created:
                    if role == UserProfile.DOCTOR:
                        Doctor.objects.get_or_create(profile=user_profile)
                    elif role == UserProfile.PATIENT:
                        Patient.objects.get_or_create(profile=user_profile)
                    elif role == UserProfile.THERAPIST:
                        Therapist.objects.get_or_create(profile=user_profile)

                status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
                return Response(serializer.data, status=status_code)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class PatientProfileView(APIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_profile = Patient.objects.get(profile__user=request.user)
            serializer = PatientSerializer(user_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response(
                {"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

class GetDoctorsView(APIView):
     def get(self, request):
        doctors = Doctor.objects.annotate(
            full_name=Concat(
                F("profile__user__first_name"),
                Value(" "),
                F("profile__user__last_name"),
                output_field=CharField(),
            ),
            email=F("profile__user__email"),
            user_id=F("profile__user__id"),
        )
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
        