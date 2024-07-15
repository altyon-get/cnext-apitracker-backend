import requests
from django.http import JsonResponse
from django.utils import timezone
from .models import APIList, APICallLog
import json
from decouple import config


def make_api_call(api_entry):
    start_time = timezone.now()
    if api_entry.params and api_entry.params.strip() and api_entry.params.lower() != 'none':
        try:
            params = json.loads(api_entry.params)
        except json.JSONDecodeError:
            params = {}
    else:
        params = {}
    method = api_entry.request_type.upper()

    headers = {
        'x-api-key': config('X_API_KEY')
    }

    try:
        response = requests.request(method, api_entry.api_endpoint, params=params, headers=headers)
        status_value = 1 if response.status_code in [200, 201, 202, 203] else 0
    except requests.RequestException as e:
        response = None
        status_value = 0
        print(f"Request failed: {e}")

    end_time = timezone.now()
    response_time = (end_time - start_time).total_seconds()
    return {
        'response': response,
        'start_time': start_time,
        'status_value': status_value,
        'response_time': response_time,
    }

def handle_api_response(api_entry, response_data):
    if response_data:
        api_entry.status = response_data['status_value']
        api_entry.code = response_data['response'].status_code if response_data['response'] else None
        api_entry.updated_at = response_data['start_time']
        api_entry.save()

        api_log = APICallLog(
            api_id=api_entry._id,
            timestamp=response_data['start_time'],
            response_time=response_data['response_time']
        )
        api_log.save()

        return JsonResponse({
            'api_endpoint': api_entry.api_endpoint,
            'status': 'Ok' if response_data['status_value'] == 1 else 'Not Ok',
            'response_code': response_data['response'].status_code,
            'response_time': response_data['response_time']
        })

    return JsonResponse({'error': 'Invalid response data'}, status=500)


import jwt
from datetime import datetime, timedelta
from django.conf import settings

def generate_jwt(payload, expiry_minutes=600):
    payload['exp'] = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def decode_jwt(token):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError as e:
        return None
    except jwt.InvalidTokenError as e:
        return None
