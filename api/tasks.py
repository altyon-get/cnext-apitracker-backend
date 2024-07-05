from celery import shared_task
from .models import APIList
from .utils import make_api_call, handle_api_response

@shared_task
def hit_apis_and_log():
    # apis = APIList.objects.all()
    print('hit_apis_and_log called')
    apis = APIList.get_all()
    for api_entry in apis:
        print(api_entry, ' -for')
        response_data = make_api_call(api_entry)
        handle_api_response(api_entry, response_data)
