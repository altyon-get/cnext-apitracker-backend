from django.http import JsonResponse
from django.views import View
from django.conf import settings
from api.utils.jwt_util import generate_jwt
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username == settings.USERNAME and password == settings.PASSWORD:
            payload = {
                'username': username,
            }
            token = generate_jwt(payload)
            return JsonResponse({'token': token})
        return JsonResponse({'error': 'Invalid credentials'}, status=401)