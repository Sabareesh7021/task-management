import jwt
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response            = get_response
        self.jwt_user_authenticator = UserJWTAuthentication()

        self.unprotected_paths = [
            '/auth/login',
            '/auth/refresh-token',
            '/admin'
        ]
    
    def decode_jwt(self, token):
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return decoded_token
        except jwt.ExpiredSignatureError:
            return "expired"
        except jwt.InvalidTokenError:
            return None

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        if request.path in self.unprotected_paths:
            return self.get_response(request)

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authorization header is missing or invalid'}, status=401)

        token = auth_header.split(' ')[1]
        decoded_token = self.decode_jwt(token)

        if decoded_token == "expired":
            return JsonResponse({'error': 'Token expired', 'refresh_required': True, 'status':False}, status=401)

        if not decoded_token:
            return JsonResponse({'error': 'Invalid token', 'status':False}, status=401)

        try:
            validated_token = self.jwt_user_authenticator.get_validated_token(token)
            user = self.jwt_user_authenticator.get_user(validated_token)
            request.user = user
        except (InvalidToken, TokenError):
            return JsonResponse({'error': 'Invalid token', 'status':False}, status=401)
        except Exception as e:
            return JsonResponse({'error': 'An error occurred', 'status':False, 'details': str(e)}, status=500)

        return self.get_response(request)



class UserJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Override get_user method to authenticate an User (CustomUser).
        """
        user_id = validated_token.get("user_id")
        User = get_user_model()

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("No active user found")
        return user