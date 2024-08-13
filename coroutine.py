import asyncio

async def fetch_data(delay, id):
    print(f'Coroutine {id} starting to fetch data')
    await asyncio.sleep(delay)
    return {'id': id, 'data': f'sample data from coroutine {id}'}


# coroutine function
async def main():
    print("Start of main coroutine")
    # task = fetch_data(2) # we just created , will excute when awaited
    # print("End of main coroutine")
    # Await the fetch_data coroutine, pausing excexution of main until fetch_data completes

    # task1 = fetch_data(2,1)
    # task2 = fetch_data(2,2)
    # result1 = await task1
    # print(f'Received data: {result1}')
    # result2 = await task2
    # print(f'Received data: {result2}')


    # Create tasks for running coroutines concurrently
    # task1 = asyncio.create_task(fetch_data(2,1))
    # task2 = asyncio.create_task(fetch_data(2,2))
    # task3 = asyncio.create_task(fetch_data(2,3))
    #
    # result1 = await task1
    # result2 = await task2
    #
    #
    # print(result1)
    # print(result2)
    # #pehle 1,2 parallel then ye chlega
    # result3 = await task3
    # print(result3)

    # run coroutines concurrenlty and gather their return values
    # gather -> not great at error heandling, will not stop others if one fail
    results = await asyncio.gather(fetch_data(2,1), fetch_data(2,2), fetch_data(2,3))
    for result in results:
        print(f"Received results: {result}")

    # TaskGroup -> provides builtin error handling
    # tasks = []
    # async with asyncio.TaskGroup() as tg:
    #     for i, sleep_time in enumerate([2,1,3], start=1):
    #         task = tg.create_task(fetch_data(sleep_time, i))
    #         tasks.append(task)
    # # After the Task Group block, all tasks have completed
    # results = [task.result() for task in tasks]
    # for result in results:
    #     print(f"Received results: {result}")



#to run main coroutine
asyncio.run(main())
# main()  -> returns coroutine objects


# Event loop -> asynio creats a eventloop
# Context managers -> use to handle groups of coroutine
#   ex: async with lock, asycn with asyncio.TaskGroup
# synchronization tool:
#   Lock -> used to lock shared_resource for one coroutine
#   semaphore -> multiple coroutine can access

