import traceback
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from .models import User
from utils.pagination import paginate
from utils.common import BaseAPIView
from .serializer import UserTokenObtainPairSerializer, UserSerializer  

class UserLoginAPIView(BaseAPIView, TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = UserTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return self._format_response(True, 'Login successful', serializer.validated_data)
        except (AuthenticationFailed, ValidationError) as e:
            return self._format_response(False, str(e), status_code=status.HTTP_400_BAD_REQUEST)
        except InvalidToken as e:
            return self._format_response(False, "Invalid token", status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            traceback.print_exc()
            return self._format_response(False, "An error occurred during login", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class UserLogoutAPIView(BaseAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return self._format_response(True, "Logout successful", status_code=status.HTTP_205_RESET_CONTENT)
        except KeyError:
            return self._format_response(False, "Refresh token is required", status_code=status.HTTP_400_BAD_REQUEST)
        except TokenError:
            return self._format_response(False, "Invalid or expired token", status_code=status.HTTP_400_BAD_REQUEST)

class UserAPIView(BaseAPIView):
    def get(self, request, pk=None):
        user = request.user
        if user.is_superuser:
            users = User.objects.exclude(id=user.id)
        elif user.is_staff:
            users = User.objects.filter(created_by=user)
        else:
            users = User.objects.filter(id=user.id)

        if pk:
            user_instance = get_object_or_404(users, id=pk)
            serializer   = UserSerializer(user_instance)
            return self._format_response(True, data=serializer.data)
        paginated_data = paginate(users, request)
        serializer     = UserSerializer(paginated_data['data'], many=True)
        return self._format_response(True, serializer.data, status_code = status.HTTP_200_OK, pagination = paginated_data)

    def post(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return self._format_response(False, "Only admins can create users", status_code=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            new_user = serializer.save(parent_id=request.user)
            return self._format_response(True, "User created successfully", UserSerializer(new_user).data, status_code=status.HTTP_201_CREATED)
        return self._format_response(False, "Validation error", serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        user_instance = get_object_or_404(User, id=pk)
        user = request.user
        if not (user.is_superuser or (user.is_staff and user_instance.created_by == user) or user_instance == user):
            return self._format_response(False, "Permission denied", status_code=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(user_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self._format_response(True, "User updated successfully", serializer.data)
        return self._format_response(False, "Validation error", serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user_instance = get_object_or_404(User, id=pk)
        user = request.user
        if not (user.is_superuser or (user.is_staff and user_instance.created_by == user)):
            return self._format_response(False, "Permission denied", status_code=status.HTTP_403_FORBIDDEN)

        user_instance.delete()
        return self._format_response(True, "User deleted successfully")
