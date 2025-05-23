from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed

from .models import User
from .serializer import UserTokenObtainPairSerializer, UserSerializer  

class UserLoginAPIView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = UserTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            token_data = serializer.validated_data
            response_data = {
                'status': True,
                'message': 'Login successful',
                'data': token_data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except AuthenticationFailed as e:
            return Response({
                "status": False,
                "message": "Incorrect username or password"
            }, status=status.HTTP_400_BAD_REQUEST)

        except InvalidToken as e:
            return Response({
                "status": False,
                "message": "Invalid token"
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": False,
                "message": "An error occurred during login"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class UserLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Logout successful.", "status":True}, status=status.HTTP_205_RESET_CONTENT)
        except KeyError:
            return Response({"error": "Refresh token is required.", "status":False}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError:
            return Response({"error": "Invalid or expired token.", "status":False}, status=status.HTTP_400_BAD_REQUEST)


class UserAPIView(APIView):
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
            serializer = UserSerializer(user_instance)
        else:
            serializer = UserSerializer(users, many=True)
        
        return Response({
            "data": serializer.data,
            "status": True
        }, status=status.HTTP_200_OK)

    def post(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({
                "error": "Only admins can create users",
                "status": False
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            new_user = serializer.save(created_by=request.user)
            return Response({
                "data": UserSerializer(new_user).data,
                "status": True
            }, status=status.HTTP_201_CREATED)
        return Response({
            "error": serializer.errors,
            "status": False
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        user = request.user
        user_instance = get_object_or_404(User, id=pk)

        if not (user.is_superuser or 
               (user.is_staff and user_instance.created_by == user) or 
               user_instance == user):
            return Response({
                "error": "Permission denied",
                "status": False
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(user_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "data": serializer.data,
                "status": True
            }, status=status.HTTP_200_OK)
        return Response({
            "error": serializer.errors,
            "status": False
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = request.user
        user_instance = get_object_or_404(User, id=pk)

        if not (user.is_superuser or 
               (user.is_staff and user_instance.created_by == user)):
            return Response({
                "error": "Permission denied",
                "status": False
            }, status=status.HTTP_403_FORBIDDEN)

        user_instance.delete()
        return Response({
            "message": "User deleted successfully",
            "status": True
        }, status=status.HTTP_200_OK)