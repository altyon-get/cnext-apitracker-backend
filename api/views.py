import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import APIList, APICallLog
from .utils.json_file_handler import extract_requests
from api.utils.api_calls import make_api_call, handle_api_response
from api.utils.load_test import load_test_api
from api.utils.request_validators import (
    validate_url,
    validate_method,
    validate_headers,
    validate_body,
    validate_params
)

class APIListView(APIView):
    def get(self, request):
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)
        search_term = request.query_params.get('search_term', None)
        method = request.query_params.get('method', '')
        status_filter = request.query_params.get('status')
        code = request.query_params.get('code', '')
        print(page, page_size, search_term, method, status_filter, code, ' -XXX')


        try:
            page = int(page)
            page_size = int(page_size)
            if page < 1 or page_size < 1:
                raise ValueError
        except ValueError:
            return Response({'error': 'page and page_size must be positive integers greater than 0'},
                            status=status.HTTP_400_BAD_REQUEST)

        query = {}
        if search_term:
            query['endpoint'] = {'$regex': search_term, '$options': 'i'}
        if method:
            query['method'] = method
        if status_filter:
            if status_filter.lower() == 'success':
                query['status'] = 1
            else:
                query['status'] = 0
        if code:
            query['code'] = int(code)

        apis, total_apis, page, page_size = APIList.get_apis_with_pagination(query, page, page_size)

        return Response({
            'data': apis,
            'total': total_apis,
            'page': page,
            'page_size': page_size
        }, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data

        endpoint = data.get('endpoint')
        method = data.get('method')
        headers = data.get('headers', {})
        params = data.get('params', {})
        body = data.get('body', {})

        headers = {h['key'].strip(): h['value'].strip() for h in headers if h['key'].strip() and h['value'].strip()}
        params = {p['key'].strip(): p['value'].strip() for p in params if p['key'].strip() and p['value'].strip()}
        try:
            body = json.loads(body) if body else {}
        except json.JSONDecodeError:
            return Response({'error': "Invalid JSON body"}, status=status.HTTP_400_BAD_REQUEST)

        required_fields = ['endpoint', 'method']
        for field in required_fields:
            if field not in data:
                return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not validate_url(endpoint):
            return Response({'error': 'Invalid URL'}, status=status.HTTP_400_BAD_REQUEST)

        if not validate_method(method):
            return Response({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)

        if not validate_headers(headers):
            return Response({'error': 'Invalid headers format'}, status=status.HTTP_400_BAD_REQUEST)

        if not validate_params(params):
            return Response({'error': 'Invalid parameters format'}, status=status.HTTP_400_BAD_REQUEST)

        if not validate_body(body):
            return Response({'error': 'Invalid body format'}, status=status.HTTP_400_BAD_REQUEST)

        api_entry = APIList(
            endpoint=endpoint,
            method=method,
            headers=headers,
            params=params,
            body=body
        )

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
        endpoint = data.get('endpoint')
        method = data.get('method')
        headers = data.get('headers', {})
        params = data.get('params', {})
        body = data.get('body', {})
        headers = {h['key'].strip(): h['value'].strip() for h in headers if
                   h['key'].strip() and h['value'].strip()}
        params = {p['key'].strip(): p['value'].strip() for p in params if
                  p['key'].strip() and p['value'].strip()}

        try:
            body = json.loads(body) if body else {}
        except json.JSONDecodeError:
            return Response({'error': "Invalid JSON body"}, status=status.HTTP_400_BAD_REQUEST)

        required_fields = ['endpoint', 'method']
        for field in required_fields:
            if field not in data:
                return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not validate_url(endpoint):
            return Response({'error': 'Invalid URL'}, status=status.HTTP_400_BAD_REQUEST)
        if not validate_method(method):
            return Response({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)
        if not validate_headers(headers):
            return Response({'error': 'Invalid headers format'}, status=status.HTTP_400_BAD_REQUEST)
        if not validate_params(params):
            return Response({'error': 'Invalid parameters format'}, status=status.HTTP_400_BAD_REQUEST)
        if not validate_body(body):
            return Response({'error': 'Invalid body format'}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'endpoint': endpoint,
            'method': method,
            'params': params,
            'headers': headers,
            'body': body
        }

        try:
            api_entry = api_entry.save(data)
            response_data = make_api_call(api_entry)
            handle_api_response(api_entry, response_data)
            api_entry._id = str(api_entry._id)
            return Response(api_entry.__dict__)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            if page < 1 or page_size < 1:
                raise ValueError
        except ValueError:
            return Response({'error': 'page and page_size must be positive integers greater than 0'}, status=status.HTTP_400_BAD_REQUEST)

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


class HitApiAndLogView(APIView):
    def post(self, request, api_id):
        api_entry = APIList.get_by_id(api_id)
        if not api_entry:
            return Response({'error': 'APIList not found'}, status=status.HTTP_404_NOT_FOUND)

        response_data = make_api_call(api_entry)
        return handle_api_response(api_entry, response_data)

class UploadJSONView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            if not isinstance(data, list):
                raise ValueError("Expected a list of folders")
            extract_requests(data)
            return Response({'message': 'JSON data processed successfully'}, status=status.HTTP_200_OK)
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON format'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as ke:
            return Response({'error': f'Missing key: {ke}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

     
class LoadTestApiView(APIView):
    def get(self, request, api_id, *args, **kwargs):
        user_count = int(request.GET.get('numUsers', 10))
        duration = int(request.GET.get('duration', 10))
        try:
            responses, min_response_time, max_response_time, avg_response_time = load_test_api(user_count, duration, api_id)
            return Response({
                 'user_count': user_count,
                 'duration': duration,
                 'responses': responses,
                 'min_response_time':min_response_time,
                 'max_response_time': max_response_time,
                 'avg_response_time': avg_response_time },
                status=status.HTTP_200_OK)
        except  Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        