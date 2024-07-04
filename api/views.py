import requests
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson.objectid import ObjectId
from cnext_apitracker_backend.mongodb import mongodb
from .serializers import APIListSerializer, APICallLogSerializer
from .utils import make_api_call, handle_api_response


class APIListView(APIView):
    def get(self, request):
        apis = list(mongodb.get_collection('apilist').find())
        for api in apis:
            api['_id'] = str(api['_id'])
        return Response(apis)

    def post(self, request):
        data = request.data
        collection = mongodb.get_collection('apilist')
        api_id = collection.insert_one(data).inserted_id
        api_entry = collection.find_one({'_id': api_id})
        response_data = make_api_call(api_entry)
        handle_api_response(api_entry, response_data)
        api_entry['_id'] = str(api_entry['_id'])
        return Response(api_entry)


class APIDetailView(APIView):
    def get_object(self, pk):
        return mongodb.get_collection('apilist').find_one({'_id': ObjectId(pk)})

    def get(self, request, pk):
        api_entry = self.get_object(pk)
        if not api_entry:
            return Response({'error': 'APIList not found'}, status=status.HTTP_404_NOT_FOUND)
        api_entry['_id'] = str(api_entry['_id'])
        return Response(api_entry)

    def put(self, request, pk):
        collection = mongodb.get_collection('apilist')
        api_entry = self.get_object(pk)
        if not api_entry:
            return Response({'error': 'APIList not found'}, status=status.HTTP_404_NOT_FOUND)
        collection.update_one({'_id': ObjectId(pk)}, {'$set': request.data})
        api_entry = collection.find_one({'_id': ObjectId(pk)})
        response_data = make_api_call(api_entry)
        handle_api_response(api_entry, response_data)
        api_entry['_id'] = str(api_entry['_id'])
        return Response(api_entry)

    def patch(self, request, pk):
        collection = mongodb.get_collection('apilist')
        api_entry = self.get_object(pk)
        if not api_entry:
            return Response({'error': 'APIList not found'}, status=status.HTTP_404_NOT_FOUND)
        collection.update_one({'_id': ObjectId(pk)}, {'$set': request.data})
        api_entry = collection.find_one({'_id': ObjectId(pk)})
        response_data = make_api_call(api_entry)
        handle_api_response(api_entry, response_data)
        api_entry['_id'] = str(api_entry['_id'])
        return Response(api_entry)

    def delete(self, request, pk, *args, **kwargs):
        collection = mongodb.get_collection('apilist')
        api_entry = self.get_object(pk)
        if not api_entry:
            return Response({'error': 'APIList not found'}, status=status.HTTP_404_NOT_FOUND)
        collection.delete_one({'_id': ObjectId(pk)})
        return Response(status=status.HTTP_204_NO_CONTENT)


class APICallLogListView(APIView):
    def get(self, request, api_pk):
        try:
            api_collection = mongodb.get_collection('apilist')
            api = api_collection.find_one({'_id': ObjectId(api_pk)})
            if not api:
                return Response({'error': 'APIList not found'}, status=status.HTTP_404_NOT_FOUND)

            call_logs_collection = mongodb.get_collection('apicalllog')
            call_logs = list(call_logs_collection.find({'api': ObjectId(api_pk)}))
            for log in call_logs:
                log['_id'] = str(log['_id'])
                log['api'] = str(log['api'])
            return Response(call_logs)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def hit_api_and_log(request, api_id):
    api_collection = mongodb.get_collection('apilist')
    call_logs_collection = mongodb.get_collection('apicalllog')

    api_entry = api_collection.find_one({'_id': ObjectId(api_id)})
    if not api_entry:
        return JsonResponse({'error': 'APIList not found'}, status=404)

    start_time = timezone.now()
    response = requests.get(api_entry['api_endpoint'])
    end_time = timezone.now()

    response_time = (end_time - start_time).total_seconds()
    status_value = 1 if response.status_code in [200, 201, 202, 203] else 0

    api_entry['status'] = status_value
    api_entry['code'] = response.status_code
    api_entry['updated_at'] = timezone.now()

    update_data = {
        'status': api_entry['status'],
        'code': api_entry['code'],
        'updated_at': api_entry['updated_at']
    }

    api_collection.update_one({'_id': ObjectId(api_id)}, {'$set': update_data})

    api_log = {
        'api': ObjectId(api_id),
        'timestamp': start_time,
        'response_time': response_time
    }
    call_logs_collection.insert_one(api_log)

    return JsonResponse({
        'api_endpoint': api_entry['api_endpoint'],
        'status': 'Ok' if status_value == 1 else 'Not Ok',
        'response_code': response.status_code,
        'response_time': response_time
    })
