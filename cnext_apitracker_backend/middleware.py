from django.http import JsonResponse
from api.utils.jwt_util import decode_jwt
from django.urls import resolve

class User:
    def __init__(self, username):
        self.username = username
        self.is_active = True
    def __str__(self):
        return self.username


class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.public_urls = ['login']

    def __call__(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        current_url = resolve(request.path_info).url_name

        if current_url in self.public_urls:
            return self.get_response(request)

        if token:
            token = token.split(' ')[1]
            decoded_token = decode_jwt(token)
            if decoded_token:
                request.user.username = decoded_token['username']
            else:
                return JsonResponse({'error': 'Invalid or expired token'}, status=401)
        else:
            return JsonResponse({'error': 'Authentication credentials were not provided.'}, status=401)

        response = self.get_response(request)
        return response
