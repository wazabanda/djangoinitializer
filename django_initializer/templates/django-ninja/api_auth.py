from ninja.security import HttpBearer
from core.models import ExpirableToken

class GlobalAuth(HttpBearer):
    def authenticate(self, request, token):
        print(token)
        from django.contrib.auth.models import User
        # from rest_framework.authtoken.models import Token
        
        try:
            token_obj = ExpirableToken.objects.get(token=token)
            if token_obj.is_expired:
                return None
            return token_obj.user
        except ExpirableToken.DoesNotExist:
            return None

def add_authenticated_user(request, call_next):
    user, token = request.auth
    if user is not None:
        request.auth = user
    response = call_next(request)
    return response

from ninja.security import HttpBearer
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            user = User.objects.get(auth_token=token)
            return user
        except User.DoesNotExist:
            return None
