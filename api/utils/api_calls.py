import requests
from django.utils import timezone
from django.http import JsonResponse
from api.models import APICallLog
from requests.exceptions import ConnectionError, HTTPError, Timeout


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
            'response': None,
            'start_time': None,
            'response_time': None,
        }

    end_time = timezone.now()
    response_time = (end_time - start_time).total_seconds()
    return {
        'response': response,
        'start_time': start_time,
        'response_time': response_time,
    }


def handle_api_response(api_entry, response_data):
    if response_data:
        api_entry.status = 1 if response_data['response'].status_code == 200 else 0
        api_entry.code = response_data['response'].status_code if response_data['response'] else None
        api_entry.updated_at = response_data['start_time']
        api_entry.save()

        api_log = APICallLog(
            response = response_data['response'],
            api_id=api_entry._id,
            timestamp=response_data['start_time'],
            response_time=response_data['response_time']
        )
        api_log.save()

        return JsonResponse({
            'api_endpoint': api_entry.endpoint,
            'status': 'Ok' if response_data['response'].status_code == 200 else 'Not Ok',
            'response_code': response_data['response'].status_code,
            'response_time': response_data['response_time']
        })
    raise ValueError("Invalid response data")
    # return JsonResponse({'error': 'Invalid response data'}, status=500)

