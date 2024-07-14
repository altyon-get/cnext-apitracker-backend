import jwt
from datetime import datetime, timedelta
from django.conf import settings

def generate_jwt(payload, expiry_minutes=30):
    payload['exp'] = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def decode_jwt(token):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
