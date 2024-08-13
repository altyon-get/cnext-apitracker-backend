from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from api.utils.jwt_util import generate_jwt
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
import time

@permission_classes([AllowAny])
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if username == settings.USERNAME and password == settings.PASSWORD:
            payload = {
                'username': username,
            }
            token = generate_jwt(payload)
            return Response({'token': token}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

from datetime import datetime


class TestView(APIView):    
    def get(self, request):
        print('Time:', datetime.now().isoformat())
        return Response({'data': 'sucess'})
