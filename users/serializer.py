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
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)