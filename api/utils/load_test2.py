# import asyncio
# import aiohttp
# import time
# from datetime import datetime
# from api.models import APIList
#
# async def send_request(session, api_entry, group_start_time, results_queue):
#     start_time = time.time()
#     async with session.request(
#         method=api_entry.method,
#         url=api_entry.endpoint,
#         params=api_entry.params,
#         json=api_entry.body,
#         headers=api_entry.headers,
#     ) as response:
#         response_time = time.time() - start_time
#         result = {
#             'status_code': response.status,
#             'response_time': response_time,
#             'group_start_time': group_start_time,
#         }
#         await results_queue.put(result)
#
# async def request_group_async(num_requests, api_id, results_queue):
#     api_entry = APIList.get_by_id(api_id)
#     group_start_time = datetime.now().isoformat()
#     async with aiohttp.ClientSession() as session:
#         tasks = [send_request(session, api_entry, group_start_time, results_queue) for _ in range(num_requests)]
#         await asyncio.gather(*tasks)
#
# async def load_test_api2(num_requests, duration, api_id):
#     duration_seconds = duration * 60
#
#     if num_requests <= duration_seconds:
#         interval = duration_seconds / num_requests
#         requests_per_interval = 1
#     else:
#         interval = 1
#         requests_per_interval = num_requests / duration_seconds
#     print(f"will send {requests_per_interval} req in each {interval}s")
#
#     results_queue = asyncio.Queue()
#     tasks = []
#
#     async def schedule_requests():
#         total_requests_sent = 0
#         start_time = time.time()
#         while time.time() < start_time + duration_seconds:
#             loop_start_time = time.time()
#             num_requests_to_send = min(int(requests_per_interval), num_requests - total_requests_sent)
#             if num_requests_to_send <= 0:
#                 break
#             task = asyncio.create_task(request_group_async(num_requests_to_send, api_id, results_queue))
#             tasks.append(task)
#             total_requests_sent += num_requests_to_send
#
#             loop_end_time = time.time()
#             processing_time = loop_end_time - loop_start_time
#             sleep_time = max(0, interval - processing_time)
#
#             print(f"Total requests sent: {total_requests_sent}")
#             print(f"Processing time {processing_time}")
#             print(f"sleeping for {sleep_time}")
#
#             await asyncio.sleep(sleep_time)
#         print(f"Total requests sent: {total_requests_sent}")
#
#     async def process_results():
#         print('Final Processing started...')
#         results = []
#         while len(results) < num_requests:
#             result = await results_queue.get()
#             results.append(result)
#             results_queue.task_done()
#         return results
#
#     await asyncio.gather(schedule_requests(), process_results())
#     await asyncio.gather(*tasks)
#     await results_queue.join()
#
#     return await process_results()
#
# def run_test(num_requests, duration, api_id):
#     print('Testing for num_requests:', num_requests, '& duration:', duration)
#     print('Starting test for asyncio...')
#     results = asyncio.run(load_test_api2(num_requests, duration, api_id))
#     for result in results:
#         print(result)
# a

import asyncio
import aiohttp
import time
from datetime import datetime
from api.models import APIList


async def send_request(session, api_entry, results):
    start_time = time.time()
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
            'timestamp': datetime.now().isoformat(),
        }
        results.append(result)

async def request_group_async(num_requests, api_id):
    # print('Requesting group')
    api_entry = APIList.get_by_id(api_id)
    group_start_time = datetime.now().isoformat()
    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, api_entry, group_start_time) for _ in range(num_requests)]
        await asyncio.gather(*tasks)

async def load_test_api(num_requests, duration, api_id):
    duration_seconds = duration * 60
    print('STARTING...')
    print(num_requests, ' -num_req')
    print(duration_seconds, ' -duration_seconds')

    if num_requests <= duration_seconds:
        interval = duration_seconds / num_requests
        requests_per_interval = 1
    else:
        interval = 1
        requests_per_interval = num_requests * interval / duration_seconds

    print(f"will send {requests_per_interval} req in each {interval}s")

    # results = []
    # start_time = time.time()
    # rest = 0
    results_queue = asyncio.Queue()
    tasks = []

    async def schedule_requests():
        total_requests_sent = 0
        start_time = time.time()

        while time.time() < start_time + duration_seconds:
            loop_start_time = time.time()
            num_requests_to_send = min(int(requests_per_interval), num_requests - total_requests_sent)
            if num_requests_to_send <= 0:
                break

            task = asyncio.create_task(request_group_async(num_requests_to_send, api_id))
            tasks.append(task)
            total_requests_sent += num_requests_to_send

            print(f"Total requests sent: {total_requests_sent}")
            loop_end_time = time.time()
            processing_time = loop_end_time - loop_start_time
            print(f"Processing time {processing_time}")
            sleep_time = max(0, interval - processing_time)
            print(f"sleeping for {sleep_time}")
            await asyncio.sleep(sleep_time)

        print(f"Total requests sent: {total_requests_sent}")

    async def process_results():
        results = []
        while len(results) < num_requests:
            result = await results_queue.get()
            results.append(result)
            results_queue.task_done()
        return results

    await asyncio.gather(schedule_requests(), process_results())
    await asyncio.gather(*tasks)
    await results_queue.join()

    return await process_results()

def run_test():
    num_requests = 1000
    duration = 2 #minute
    api_id = '66a5f7bac158f8f1e822b376'
    print('Testing for num_requests:', num_requests, '& duration:', duration)
    results = asyncio.run(load_test_api(num_requests, duration, api_id))
    for result in results:
        print(result)


if __name__ == "__main__":
    run_test()