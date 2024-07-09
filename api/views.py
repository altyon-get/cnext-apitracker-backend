from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import APIList, APICallLog
from .utils import make_api_call, handle_api_response


class APIListView(APIView):
    def get(self, request):
        apis = APIList.get_all()
        api_dicts = [api.__dict__ for api in apis]
        for api in api_dicts:
            api['_id'] = str(api['_id'])
        return Response(api_dicts)

    def post(self, request):
        data = request.data
        required_fields = ['api_endpoint', 'request_type']

        for field in required_fields:
            if field not in data:
                return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)

        #TODO: Validate data before saving

        api_entry = APIList(**data)
        try:
            api_entry.save()
            response_data = make_api_call(api_entry)
            handle_api_response(api_entry, response_data)
            return Response(api_entry.__dict__)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class APIDetailView(APIView):
    def get_object(self, api_id):
        return APIList.get_by_id(api_id)

    def get(self, request, api_id):
        api_entry = self.get_object(api_id)
        if not api_entry:
            return Response({'error': 'APIList not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(api_entry.__dict__)

    def put(self, request, api_id):
        api_entry = self.get_object(api_id)
        if not api_entry:
            return Response({'error': 'APIList not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        required_fields = ['api_endpoint', 'request_type']
        for field in required_fields:
            if field not in data:
                return Response({'error': 'Missing required field'}, status=status.HTTP_400_BAD_REQUEST)

        #TODO: validate data before saving

        try:
            api_entry = api_entry.save(data)
            response_data = make_api_call(api_entry)
            handle_api_response(api_entry, response_data)
            api_entry._id = str(api_entry._id)
            return Response(api_entry.__dict__)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def patch(self, request, api_id):
    #     api_entry = self.get_object(api_id)
    #     if not api_entry:
    #         return Response({'error': 'APIList not found'}, status=status.HTTP_404_NOT_FOUND)
    #
    #     for key, value in request.data.items():
    #         setattr(api_entry, key, value)
    #
    #     ##validate data before saving
    #     data = request.data
    #
    #     try:
    #         api_entry = api_entry.save(data)
    #         response_data = make_api_call(api_entry)
    #         handle_api_response(api_entry, response_data)
    #         api_entry._id = str(api_entry._id)
    #         return Response(api_entry.__dict__)
    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #

    def delete(self, request, api_id, *args, **kwargs):
        api_entry = self.get_object(api_id)
        if not api_entry:
            return Response({'error': 'APIList not found'}, status=status.HTTP_404_NOT_FOUND)
        APIList.delete(api_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class APICallLogListView(APIView):
    def get(self, request, api_id):
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        try:
            page = int(page)
            page_size = int(page_size)
        except ValueError:
            return Response({'error': 'page and page_size must be integers'}, status=status.HTTP_400_BAD_REQUEST)

        if page < 1 and page_size < 1:
            return Response({'error': 'page and page size must be greater than 1'})

        api = APIList.get_by_id(api_id)
        if not api:
            return Response({'error': 'APIList not found'}, status=status.HTTP_404_NOT_FOUND)

        call_logs, total_logs = APICallLog.get_by_api(api_id, page, page_size)
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
