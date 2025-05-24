from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except AuthenticationFailed as e:
            raise AuthenticationFailed("Incorrect username or password")

        user = self.user
        
        if not user.is_active:
            raise serializers.ValidationError("Your account is inactive. Please contact admin.")
        
        if user.is_superuser:
            role = "super_admin"
        elif user.is_staff:
            role = "admin"
        else:
            role = "user"
        
        data['user_id'] = user.id
        data['name']    = f"{user.first_name} {user.last_name}"
        data['role']    = role

        return data
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)