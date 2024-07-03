# api/utils.py
import requests
from django.utils import timezone
from .models import APICallLog


def make_api_call(api_entry):
    start_time = timezone.now()
    if api_entry.request_type == 'GET':
        response = requests.get(api_entry.api_endpoint, params=eval(api_entry.params) if api_entry.params else {})
    elif api_entry.request_type == 'POST':
        response = requests.post(api_entry.api_endpoint, data=eval(api_entry.params) if api_entry.params else {})
    elif api_entry.request_type == 'PUT':
        response = requests.put(api_entry.api_endpoint, data=eval(api_entry.params) if api_entry.params else {})
    elif api_entry.request_type == 'DELETE':
        response = requests.delete(api_entry.api_endpoint, data=eval(api_entry.params) if api_entry.params else {})
    else:
        response = None

    end_time = timezone.now()
    response_time = (end_time - start_time).total_seconds()
    status_value = 1 if response and response.status_code in [200, 201, 202, 203] else 0

    return {
        'response': response,
        'status_value': status_value,
        'response_time': response_time,
    }

def handle_api_response(api_entry, response_data):
    if response_data:
        api_entry.status = response_data['status_value']
        api_entry.code = response_data['response'].status_code
        api_entry.updated_at = timezone.now()
        api_entry.save()

        api_log = APICallLog(
            api=api_entry,
            timestamp=timezone.now(),
            response_time=response_data['response_time']
        )
        api_log.save()
