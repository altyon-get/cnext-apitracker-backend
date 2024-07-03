import requests
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from .models import APIList, APICallLog
from .serializers import APIListSerializer, APICallLogSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import make_api_call, handle_api_response


class APIListView(APIView):
    def get(self, request):
        apis = APIList.objects.all()
        serializer = APIListSerializer(apis, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = APIListSerializer(data=request.data)
        if serializer.is_valid():
            api_entry = serializer.save()
            response_data = make_api_call(api_entry)
            handle_api_response(api_entry, response_data)


class APIDetailView(APIView):

    def get_object(self, pk):
        return get_object_or_404(APIList, pk=pk)

    def get(self, request, pk):
        api_entry = self.get_object(pk)
        serializer = APIListSerializer(api_entry)
        return Response(serializer.data)

    def put(self, request, pk):
        api_entry = self.get_object(pk)
        serializer = APIListSerializer(api_entry, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = make_api_call(api_entry)
            handle_api_response(api_entry, response_data)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        api_entry = self.get_object(pk)
        serializer = APIListSerializer(api_entry, data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            response_data = make_api_call(api_entry)
            handle_api_response(api_entry, response_data)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, pk):
        api_entry = self.get_object(pk)
        api_entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class APICallLogListView(APIView):
    def get(self, request, api_pk):
        try:
            api = APIList.objects.get(pk=api_pk)
            call_logs = APICallLog.objects.filter(api=api)
            serializer = APICallLogSerializer(call_logs, many=True)
            return Response(serializer.data)
        except APIList.DoesNotExist:
            return Response({'error': 'APIList not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def hit_api_and_log(request, api_id):
    api_entry = get_object_or_404(APIList, id=api_id)
    print(api_entry , ' -XXX')

    start_time = timezone.now()
    response = requests.get(api_entry.api_endpoint)
    end_time = timezone.now()

    response_time = (end_time - start_time).total_seconds()
    print(response_time, ' -XXX')

    if response.status_code in [200, 201, 202, 203]:
        status = 1
    else:
        status = 0

    api_entry.status = status
    api_entry.code = response.status_code
    api_entry.updated_at = timezone.now()
    api_entry.save()

    api_log = APICallLog(
        api=api_entry,
        timestamp=start_time,
        response_time=response_time
    )
    api_log.save()

    # Return a JSON response
    return JsonResponse({
        'api_endpoint': api_entry.api_endpoint,
        'status': 'Ok' if status == 1 else 'Not Ok',
        'response_code': response.status_code,
        'response_time': response_time
    })






