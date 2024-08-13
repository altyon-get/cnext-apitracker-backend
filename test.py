from celery import Celery, group, chord
from celery import shared_task

app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@shared_task
def simple_task(x):
    return x * 2

@shared_task
def simple_callback(results):
    print("Results: ", results)

def test_chord():
    task_group = group(simple_task.s(i) for i in range(10))
    callback = simple_callback.s()
    chord(task_group)(callback)

if __name__ == "__main__":
    test_chord()
