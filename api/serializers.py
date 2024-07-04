from rest_framework import serializers
from .models import APIList, APICallLog
class APIListSerializer(serializers.Serializer):
    id = serializers.CharField(source='_id', required=False)
    api_endpoint = serializers.CharField(max_length=255)
    request_type = serializers.ChoiceField(choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE')])
    params = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    status = serializers.IntegerField(default=0)
    code = serializers.IntegerField(default=0)
    updated_at = serializers.DateTimeField()

    def create(self, validated_data):
        api = APIList(**validated_data)
        api.save()
        return api

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class APICallLogSerializer(serializers.Serializer):
    id = serializers.CharField(source='_id', required=False)
    api_id = serializers.CharField()
    timestamp = serializers.DateTimeField()
    response_time = serializers.FloatField()

    def create(self, validated_data):
        log = APICallLog(**validated_data)
        log.save()
        return log

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
