# import asyncio
# import aiohttp
# import time
# from datetime import datetime
# from concurrent.futures import ThreadPoolExecutor
# from queue import Queue
# import threading
# import os
#
# from api.models import APIList
#
# # Queue for storing results
# # result_queue = Queue()
#
# async def send_request(session, api_entry):
#     # print('Hello boss')
#     start_time = time.time()
#     group_start_time = datetime.now().isoformat()
#     async with session.request(
#             method=api_entry.method,
#             url=api_entry.endpoint,
#             params=api_entry.params,
#             json=api_entry.body,
#             headers=api_entry.headers,
#     ) as response:
#         response_time = time.time() - start_time
#         result = {
#             'status_code': response.status,
#             'response_time': response_time,
#             'timestamp': group_start_time,
#         }
#         print(result['timestamp'][17:],  result)
#         return result
#
# async def process_group(requests_per_interval, api_entry):
#     async with aiohttp.ClientSession() as session:
#         tasks = [send_request(session, api_entry) for _ in range(int(requests_per_interval))]
#         responses = await asyncio.gather(*tasks)
#         # for response in responses:
#         #     result_queue.put(response)  # Put result in queue for background printing
#
#
# # def print_results():
# #     while True:
# #         result = result_queue.get()
# #         if result is None:
# #             break
# #         print('Response:', result)
#
# async def load_test_api(num_requests, duration, api_id):
#     requests_per_interval = 100
#     interval = 5
#     num_of_group = 10
#     api_entry = APIList.get_by_id(api_id)
#
#     tasks = []
#     for i in range(int(num_of_group)):
#         print(f'XProcessing group {i}')
#         task = asyncio.create_task(process_group(requests_per_interval, api_entry))
#         tasks.append(task)
#         print(f'Waiting for {interval} seconds')
#         await asyncio.sleep(interval)
#
#     await asyncio.gather(*tasks)
#
# def run_test():
#     num_requests = 1200
#     duration = 2  # in minutes
#     api_id = '66a5f7bac158f8f1e822b376'
#
#     # Start background thread for printing results
#     # print_thread = threading.Thread(target=print_results, daemon=True)
#     # print_thread.start()
#
#     # Run asynchronous load test
#     asyncio.run(load_test_api(num_requests, duration, api_id))
#
#     # Stop the print thread after the load test completes
#     # result_queue.put(None)
#     # print_thread.join()
#
# if __name__ == "__main__":
#     run_test()


import asyncio
import aiohttp
import time
from datetime import datetime
from queue import Queue
import threading
from concurrent.futures import ThreadPoolExecutor

from api.models import APIList

# Results container
results = []


async def send_request(session, api_entry):
    start_time = time.time()
    group_start_time = datetime.now().isoformat()
    async with session.request(
            method=api_entry.method,
            url=api_entry.endpoint,
            params=api_entry.params,
            json=api_entry.body,
            headers=api_entry.headers,
    ) as response:
        response_time = time.time() - start_time
        result = {
            'status_code': response.status,
            'response_time': response_time,
            'timestamp': group_start_time,
        }
        print(result['timestamp'][17:], result)
        return result


def request_group_thread(num_requests, api_entry):
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = [executor.submit(send_request, api_entry) for i in range(num_requests)]
        results = [future.result() for future in futures]
    return results


async def process_group(requests_per_interval, api_entry):
    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, api_entry) for _ in range(int(requests_per_interval))]
        responses = await asyncio.gather(*tasks)

        # Calculate min, max, and average response time
        response_times = [r['response_time'] for r in responses]
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        avg_response_time = sum(response_times) / len(response_times)

        # Store results
        results.append({
            'responses': responses,
            'min_response_time': min_response_time,
            'max_response_time': max_response_time,
            'avg_response_time': avg_response_time,
        })


async def load_test_api(num_requests, duration, api_id):
    requests_per_interval = 10
    interval = 10
    num_of_group = 1
    api_entry = APIList.get_by_id(api_id)

    tasks = []
    for i in range(int(num_of_group)):
        print(f'Processing group {i}')
        # task = asyncio.create_task(process_group(requests_per_interval, api_entry))
        task = request_group_thread(num_requests, api_entry)
        tasks.append(task)
        print(f'Waiting for {interval} seconds')
        await asyncio.sleep(interval)

    await asyncio.gather(*tasks)


def run_test():
    num_requests = 1200
    duration = 2  # in minutes
    api_id = '66bb32720ab0f02818d5a19b'

    # Run asynchronous load test
    asyncio.run(load_test_api(num_requests, duration, api_id))

    # Print overall results
    print(f'Overall Results:')
    print(f'Requests per Interval: 100')
    print(f'Interval (seconds): 5')
    print(f'Number of Groups: 10')

    for i, result in enumerate(results):
        print(f'Group {i + 1}:')
        print(f'  Number of Responses: {len(result["responses"])}')
        print(f'  Min Response Time: {result["min_response_time"]:.2f} seconds')
        print(f'  Max Response Time: {result["max_response_time"]:.2f} seconds')
        print(f'  Average Response Time: {result["avg_response_time"]:.2f} seconds')


if __name__ == "__main__":
    run_test()
