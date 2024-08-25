from ninja import NinjaAPI, Swagger
from .api_auth import GlobalAuth,add_authenticated_user,AuthBearer
from core.models import ExpirableToken,User,UserProfile
from core.decorators import groups_required

from ninja.openapi.schema import OpenAPISchema

api = NinjaAPI(docs=Swagger(settings={"persistAuthorization": True}),version='1.0.0',auth=GlobalAuth(),docs_decorator=groups_required(['Developer']))
api.add_router('/core','core.api.router')
# api.add_middleware(add_authenticated_user)


@api.get('/login',auth=None)
def login(request, username: str, password: str):
    from django.contrib.auth import authenticate
    from django.http import JsonResponse
    # from rest_framework.authtoken.models import Token
    user = authenticate(username=username, password=password)
    if user:
        token, _ = ExpirableToken.objects.get_or_create(user=user)
        if token or token.is_expired():
            token.token = token.generate_token()
            token.set_expiration(0, 2, 0)
        profile,_ = UserProfile.objects.get_or_create(user=user)
        return JsonResponse({"token": token.token,
                             'expires':token.expiration_date.strftime('%Y-%m-%d %H:%M:%S'),
                             "user_id":user.id,
                             "username":user.username
                             })
    else:
        return JsonResponse({"error": "Invalid credentials"}, status=401)
