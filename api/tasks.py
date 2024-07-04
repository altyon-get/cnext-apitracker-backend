from celery import shared_task
from django.utils import timezone
from .models import APIList, APICallLog
from .utils import make_api_call, handle_api_response

@shared_task
def hit_apis_and_log():
    apis = APIList.get_all()
    for api_entry in apis:
        print(api_entry, ' -for')
        response_data = make_api_call(api_entry)
        handle_api_response(api_entry, response_data)