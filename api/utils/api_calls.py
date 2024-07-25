import requests
from django.utils import timezone
from api.models import APICallLog
from requests.exceptions import ConnectionError, HTTPError, Timeout
from rest_framework.response import Response
from rest_framework import status

def make_api_call(api_entry):
    start_time = timezone.now()
    try:
        response = requests.request(
            method=api_entry.method,
            url=api_entry.endpoint,
            params=api_entry.params,
            json=api_entry.body,
            headers=api_entry.headers,
            verify=False
        )
    except (ConnectionError, HTTPError, Timeout) as e:
        print(f"Request failed: {e}")
        return {
            'status_code': 0,
            'start_time': None,
            'response_time': None,
        }

    end_time = timezone.now()
    response_time = (end_time - start_time).total_seconds()
    return {
        'status_code': response.status_code,
        'start_time': start_time,
        'response_time': response_time,
    }


def handle_api_response(api_entry, response_data):
    if response_data:
        api_entry.status = 1 if response_data['status_code'] < 400 else 0
        api_entry.code = response_data['status_code']
        api_entry.updated_at = response_data['start_time']
        api_entry.save()

        api_log = APICallLog(
            api_id=api_entry._id,
            timestamp=response_data['start_time'],
            status_code=response_data['status_code'],
            response_time=response_data['response_time']
        )
        api_log.save()

        return Response({
            'api_endpoint': api_entry.endpoint,
            'status': 'Ok' if api_entry.status < 400 else 'Not Ok',
            'response_code': api_entry.code,
            'response_time': response_data['response_time']
        }, status=status.HTTP_200_OK)
    # raise ValueError("Invalid response data")
    return Response({'error': 'Internal API Call Failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

