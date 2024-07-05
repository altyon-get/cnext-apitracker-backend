import requests
from django.http import JsonResponse
from django.utils import timezone
from cnext_apitracker_backend.mongodb import mongodb

def make_api_call(api_entry):
    start_time = timezone.now()
    if api_entry['request_type'] == 'GET':
        response = requests.get(api_entry['api_endpoint'], params=eval(api_entry['params']) if api_entry['params'] else {})
    elif api_entry['request_type'] == 'POST':
        response = requests.post(api_entry['api_endpoint'], data=eval(api_entry['params']) if api_entry['params'] else {})
    elif api_entry['request_type'] == 'PUT':
        response = requests.put(api_entry['api_endpoint'], data=eval(api_entry['params']) if api_entry['params'] else {})
    elif api_entry['request_type'] == 'DELETE':
        response = requests.delete(api_entry['api_endpoint'], data=eval(api_entry['params']) if api_entry['params'] else {})
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
        api_collection = mongodb.get_collection('apilist')
        api_entry['status'] = response_data['status_value']
        api_entry['code'] = response_data['response'].status_code
        api_entry['updated_at'] = timezone.now()
        api_collection.update_one({'_id': api_entry['_id']}, {'$set': api_entry})

        call_logs_collection = mongodb.get_collection('apicalllog')
        api_log = {
            'api': api_entry['_id'],
            'timestamp': timezone.now(),
            'response_time': response_data['response_time']
        }
        print(api_log,)
        call_logs_collection.insert_one(api_log)

        return JsonResponse({
            'api_endpoint': api_entry['api_endpoint'],
            'status': 'Ok' if response_data['status_value'] == 1 else 'Not Ok',
            'response_code': response_data['response'].status_code,
            'response_time': response_data['response_time']
        })
