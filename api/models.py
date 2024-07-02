from django.db import models
from djongo import models as djongo_models

# Create your models here.
class APIList(djongo_models.Model):
    index_number = djongo_models.IntegerField()
    api_endpoint = djongo_models.CharField(max_length=255)
    status = djongo_models.IntegerField(choices=[(0, 'Not Ok'), (1, 'Ok')])
    code = djongo_models.IntegerField()
    updated_at = djongo_models.DateTimeField(auto_now=True)
    
class APICallLog(djongo_models.Model):
    api = djongo_models.ForeignKey(APIList, on_delete=djongo_models.CASCADE)
    timestamp = djongo_models.DateTimeField()
    response_time = djongo_models.FloatField()