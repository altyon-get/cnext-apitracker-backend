from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import APIList, APICallLog
from .utils import make_api_call, handle_api_response


class APIListView(APIView):
    def get(self, request):
        apis = APIList.get_all()
        for api in apis:
            api['_id'] = str(api['_id'])
        return Response(apis)

    def post(self, request):
        data = request.data
        api_entry = APIList(**data)
        api_entry.save()
        response_data = make_api_call(api_entry)
        handle_api_response(response_data)
        api_entry._id = str(api_entry._id)
        return Response(api_entry.__dict__)


class APIDetailView(APIView):
    def get_object(self, api_id):
        return APIList.get_by_id(api_id)

    def get(self, request, api_id):
        api_entry = self.get_object(api_id)
        if not api_entry:
            return Response({'error': 'APIList not found'}, status=status.HTTP_404_NOT_FOUND)
        api_entry['_id'] = str(api_entry['_id'])
        return Response(api_entry)

    def put(self, request, api_id):
        api_entry = self.get_object(api_id)
        if not api_entry:
            return Response({'error': 'APIList not found'}, status=status.HTTP_404_NOT_FOUND)
        for key, value in request.data.items():
            setattr(api_entry, key, value)
        api_entry.save()
        response_data = make_api_call(api_entry)
        handle_api_response(api_entry, response_data)
        api_entry._id = str(api_entry._id)
        return Response(api_entry.__dict__)

    def patch(self, request, api_id):
        api_entry = self.get_object(api_id)
        if not api_entry:
            return Response({'error': 'APIList not found'}, status=status.HTTP_404_NOT_FOUND)
        for key, value in request.data.items():
            setattr(api_entry, key, value)
        api_entry.save()
        response_data = make_api_call(api_entry)
        handle_api_response(api_entry, response_data)
        api_entry._id = str(api_entry._id)
        return Response(api_entry)

    def delete(self, request, api_id, *args, **kwargs):
        api_entry = self.get_object(api_id)
        if not api_entry:
            return Response({'error': 'APIList not found'}, status=status.HTTP_404_NOT_FOUND)
        APIList.delete(api_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class APICallLogListView(APIView):
    def get(self, request, api_id):
        page= request.GET.get('page')
        page_size= request.GET.get('page_size')

        if page and page_size:
            return Response({'error': 'page and page size must be greater than 1'})
        api = APIList.get_by_id(api_id)
        if not api:
            return Response({'error': 'APIList not found'}, status=status.HTTP_404_NOT_FOUND)

        call_logs, total_logs = APICallLog.get_by_api(api_id, page, page_size)
        for log in call_logs:
            log['_id'] = str(log['_id'])
            log['api_id'] = str(log['api_id'])
        return Response({
            'call_logs': call_logs,
            'page': page,
            'page_size': page_size,
            'total_logs': total_logs,
        })


def hit_api_and_log(request, api_id):
    api_entry = APIList.get_by_id(api_id)
    if not api_entry:
        return JsonResponse({'error': 'APIList not found'}, status=404)

    response_data = make_api_call(api_entry)
    return handle_api_response(api_entry, response_data)