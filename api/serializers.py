from rest_framework import serializers
from .models import APIList, APICallLog


class APIListSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIList
        fields = '__all__'


class APICallLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = APICallLog
        fields = '__all__'