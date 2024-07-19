from celery import shared_task
from .models import APIList
from .utils.api_calls import make_api_call, handle_api_response
import logging

logger = logging.getLogger(__name__)
@shared_task
def hit_apis_and_log():
    apis = APIList.get_all()
    for api_entry in apis:
        try:
            response_data = make_api_call(api_entry)
            handle_api_response(api_entry, response_data)
        except Exception as e:
            logger.error(f"Error hitting API endpoint {api_entry.endpoint}: {e}")