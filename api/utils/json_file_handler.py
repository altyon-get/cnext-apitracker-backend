import json
from requests.exceptions import ConnectionError, HTTPError, Timeout
from api.models import APIList
from .api_calls import make_api_call, handle_api_response
import base64
from .request_validators import validate_url, validate_method


def prepare_multipart_body(body_list):
    body = {}
    files = {}
    for item in body_list:
        key = item['key']
        value = item['value']
        is_file = item['isFile']
        if is_file:
            filename = item.get('filename', 'uploaded_file')
            decoded_file = base64.b64decode(value)
            files[key] = (filename, decoded_file)
        else:
            body[key] = value
    return body, files


def prepare_body(body, content_type):
    if body is None:
        return {}, {}

    if content_type == 'application/json':
        body = json.loads(body)
        return body, {}
    elif content_type == 'application/x-www-form-urlencoded':
        body = {k: v for k, v in json.loads(body).items()}
        return body, {}
    elif content_type == 'multipart/form-data':
        body, files = prepare_multipart_body(body)
        return body,files
    else:
        print('Found new content type:', content_type)
        return {}, {}


def validate_and_prepare_request(data):
    endpoint = data['endpoint']
    if not validate_url(endpoint):
        raise ValueError(f"Invalid endpoint: {endpoint}")

    method = data['method']
    if not validate_method(method):
        raise ValueError(f"Invalid method: {method}")

    # TODO: need to handle ? is active?
    headers = {h['key']: h['value'] for h in data['headers']}
    params = {p['key']: p['value'] for p in data['params']}

    content_type = data['body']['contentType']
    body = data['body']['body']
    body, files = prepare_body(body, content_type)

    return {
        'endpoint': endpoint,
        'method': method,
        'headers': headers,
        'params': params,
        'body': body,
        'files': files
    }


def store_request(group_name, data):
    print('Storing request for ', group_name )
    try:
        request_data = validate_and_prepare_request(data)
        api_entry = APIList(
            endpoint=request_data['endpoint'],
            method=request_data['method'],
            headers=request_data['headers'],
            params=request_data['params'],
            body=request_data['body']
        )
        print(api_entry.__dict__)
        api_entry.save()
        response_data = make_api_call(api_entry)
        # print(response_data)
        if response_data['response'] is None:
            print(f"API call failed for group '{group_name}'")
            return False
        response = handle_api_response(api_entry, response_data)
        return response
    except (ValueError, ConnectionError, HTTPError, Timeout, Exception) as e:
        print(f"Error processing request for group '{group_name}': {e}")
        return False


def process_requests(group_name, requests):
    for request in requests:
        store_request(group_name, request)


def extract_requests(folders):
    for folder in folders:
        name = folder['name']
        requests = folder['requests']
        process_requests(name, requests)
        sub_folders = folder.get('folders', [])
        if sub_folders:
            extract_requests(sub_folders)