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
            if isinstance(value, list):
                value = json.dumps(value)
            try:
                decoded_file = base64.b64decode(value)
            except (TypeError, ValueError):
                raise ValueError(f"Invalid base64 encoding for file in key '{key}'")

            filename = item.get('filename', 'uploaded_file')
            files[key] = (filename, decoded_file)
        else:
            body[key] = value

    return body, files

def prepare_body(body, content_type):
    if not body:
        return {}, {}

    if content_type == 'application/json':
        body = json.loads(body) #"body": "{", <- got 1 input we can raise error here
        return body, {}
    elif content_type == 'application/x-www-form-urlencoded':
        body = {k: v for k, v in json.loads(body).items()}
        return body, {}
    elif content_type == 'multipart/form-data':
        body, files = prepare_multipart_body(body)
        return body,files
    elif content_type == 'text/plain':
        return body, {}
    elif content_type == 'application/xml':
        return body, {}  #need to verify
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

    # TODO: need to handle ? is active?  Also using strip as kch headers me spaces h
    headers = {h['key']: h['value'] for h in data['headers'] if h['key'].strip() and h['value'].strip()}
    params = {p['key']: p['value'] for p in data['params'] if p['key'].strip() and p['value'].strip()}

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
    try:
        request_data = validate_and_prepare_request(data)
        api_entry = APIList(
            endpoint=request_data['endpoint'],
            method=request_data['method'],
            headers=request_data['headers'],
            params=request_data['params'],
            body=request_data['body']
        )
        api_entry.save()
        response_data = make_api_call(api_entry)
        if response_data['response'] is None:
            raise ConnectionError(f"API call failed for group '{group_name}'")
        response = handle_api_response(api_entry, response_data)
        return response
    except ValueError as ve:
        print(f"Validation error for group '{group_name}', '{data.get('endpoint', '')}': {ve}")
        raise ve
    except (ConnectionError, HTTPError, Timeout) as ce:
        print(f"API call error for group '{group_name}', '{data.get('endpoint', '')}': {ce}")
        raise ce
    except Exception as e:
        print(f"Unexpected error for group '{group_name}', '{data.get('endpoint', '')}': {e}")
        raise e



def process_requests(group_name, requests):
    for request in requests:
        try:
            store_request(group_name, request)
        except Exception as e:
            print(f"Error processing request for group '{group_name}': {e}")


def extract_requests(folders):
    try:
        for folder in folders:
            name = folder['name']
            requests = folder['requests']
            process_requests(name, requests)
            sub_folders = folder.get('folders', [])
            if sub_folders:
                extract_requests(sub_folders)
    except KeyError as ke:
        print(f"Missing key in folder: {ke}")
        raise ke
    except Exception as e:
        print(f"Unexpected error extracting requests: {e}")
        raise e