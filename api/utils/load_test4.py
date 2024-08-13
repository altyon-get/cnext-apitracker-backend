from celery import Celery
import threading
import requests
import time
from api.models import APIList

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def run_load_test(api_id, num_requests, duration):
    api_entry = APIList.get_by_id(api_id)
    requests_per_interval = 100
    interval = 10
    num_of_group = 1

    for i in range(int(num_of_group)):
        print(f'Processing group {i}')
        process_group(requests_per_interval, api_entry)
        print(f'Waiting for {interval} seconds')
        time.sleep(interval)

    # You can now return or log the results as needed
    print('Load test completed')

def send_request(api_entry):
    start_time = time.time()
    response = requests.request(
        method=api_entry.method,
        url=api_entry.endpoint,
        params=api_entry.params,
        json=api_entry.body,
        headers=api_entry.headers,
    )
    response_time = time.time() - start_time
    print(f'Response time: {response_time} seconds, Status Code: {response.status_code}')

def process_group(requests_per_interval, api_entry):
    threads = []

    for _ in range(requests_per_interval):
        thread = threading.Thread(target=send_request, args=(api_entry,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    # Trigger the Celery task
    run_load_test.delay(api_id='66bb32720ab0f02818d5a19b', num_requests=1200, duration=2)
