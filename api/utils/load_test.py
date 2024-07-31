import time
import requests
from datetime import datetime
from api.models import APIList
from concurrent.futures import ThreadPoolExecutor

def send_request(api_id):
    group_start_time = datetime.now().isoformat()
    api_entry = APIList.get_by_id(api_id)
    start_time = time.time()
    response = requests.request(
            method=api_entry.method,
            url=api_entry.endpoint,
            params=api_entry.params,
            json=api_entry.body,
            headers=api_entry.headers,
            verify=False
            )
    end_time = time.time()
    response_time = end_time - start_time
    return {
        'status_code': response.status_code,
        'response_time': response_time,
        'group_start_time': group_start_time,
    }


def request_group_thread(api_id, num_requests):
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = [executor.submit(send_request, api_id) for i in range(num_requests)]
        results = [future.result() for future in futures]
    return results


def load_test_api(num_requests, duration, api_id='66a2477337bdf59fba04727d'):
    responses = []

    start_time = time.time()
    end_time = start_time + duration
    tasks = []

    while time.time() < end_time:
        task = request_group_thread(api_id, num_requests)
        tasks.append(task)
        elapsed_time = time.time() - start_time
        remaining_time = end_time - time.time()
        if remaining_time > 0:
            time.sleep(min(1, remaining_time))
    
    for task in tasks:
        result = task
        responses.extend(result)

    min_response_time = min(responses, key=lambda x: x['response_time'])['response_time']
    max_response_time = max(responses, key=lambda x: x['response_time'])['response_time']
    avg_response_time = sum(res['response_time'] for res in responses) / len(responses)

        
    return responses, min_response_time, max_response_time, avg_response_time
