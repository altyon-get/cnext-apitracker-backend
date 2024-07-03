from django.db import models
from djongo import models as djongo_models

# Create your models here.
class APIList(djongo_models.Model):
    api_endpoint = djongo_models.CharField(max_length=255)
    request_type = djongo_models.CharField(max_length=10, choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE')])
    params = djongo_models.TextField(null=True, blank=True)
    status = djongo_models.IntegerField(choices=[(0, 'Not Ok'), (1, 'Ok')], default=0)
    code = djongo_models.IntegerField(default=0)
    updated_at = djongo_models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.api_endpoint
    
class APICallLog(djongo_models.Model):
    api = djongo_models.ForeignKey(APIList, on_delete=djongo_models.CASCADE)
    timestamp = djongo_models.DateTimeField()
    response_time = djongo_models.FloatField()

    def __str__(self):
        return str(self.timestamp)