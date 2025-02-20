from rest_framework import serializers
from user_profile.models import User  
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])  

    class Meta:
        model = User
        fields = [
            'first_name',        
            'last_name',         
            'password',          
            'username',          
            'email',             
            'phone',             
            'address',           
            'birth_date',        
            'profile_picture',   
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')  
        user = super().create(validated_data)  
        user.set_password(password)  
        user.save()  
        return user
