from rest_framework.generics import CreateAPIView, RetrieveAPIView
from django.contrib.auth import get_user_model 
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny

User = get_user_model()  

class RegisterUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  

class UserProfileView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user  
