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




