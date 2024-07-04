# from django.db import models
# from djongo import models as djongo_models
#
# # Create your models here.
# class APIList(djongo_models.Model):
#     api_endpoint = djongo_models.CharField(max_length=255)
#     request_type = djongo_models.CharField(max_length=10, choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE')])
#     params = djongo_models.TextField(null=True, blank=True)
#     status = djongo_models.IntegerField(choices=[(0, 'Not Ok'), (1, 'Ok')], default=0)
#     code = djongo_models.IntegerField(default=0)
#     updated_at = djongo_models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return self.api_endpoint
#
# class APICallLog(djongo_models.Model):
#     api = djongo_models.ForeignKey(APIList, on_delete=djongo_models.CASCADE)
#     timestamp = djongo_models.DateTimeField()
#     response_time = djongo_models.FloatField()
#
#     def __str__(self):
#         return str(self.timestamp)

# models.py (redefined as plain classes)
import datetime
from pymongo import ReturnDocument
from bson.objectid import ObjectId
from cnext_apitracker_backend.mongodb import mongodb

class APIList:
    collection = mongodb.get_collection('apilist')

    def __init__(self, api_endpoint, request_type, params=None, status=0, code=0, updated_at=None, _id=None):
        self.api_endpoint = api_endpoint
        self.request_type = request_type
        self.params = params
        self.status = status
        self.code = code
        self.updated_at = updated_at or datetime.datetime.utcnow()
        self._id = _id

    def save(self):
        data = self.__dict__.copy()
        if self._id:
            data['_id'] = ObjectId(self._id)
            self.collection.find_one_and_update(
                {'_id': ObjectId(self._id)},
                {'$set': data},
                return_document=ReturnDocument.AFTER
            )
        else:
            result = self.collection.insert_one(data)
            self._id = result.inserted_id

    @staticmethod
    def get_all():
        return list(APIList.collection.find())

    @staticmethod
    def get_by_id(api_id):
        return APIList.collection.find_one({'_id': ObjectId(api_id)})

    @staticmethod
    def delete(api_id):
        APIList.collection.delete_one({'_id': ObjectId(api_id)})


class APICallLog:
    collection = mongodb.get_collection('apicalllog')

    def __init__(self, api_id, timestamp, response_time, _id=None):
        self.api_id = api_id
        self.timestamp = timestamp
        self.response_time = response_time
        self._id = _id

    def save(self):
        data = self.__dict__.copy()
        if self._id:
            data['_id'] = ObjectId(self._id)
            self.collection.find_one_and_update(
                {'_id': ObjectId(self._id)},
                {'$set': data},
                return_document=ReturnDocument.AFTER
            )
        else:
            result = self.collection.insert_one(data)
            self._id = result.inserted_id

    @staticmethod
    def get_by_api(api_id, page=1, page_size=10):
        skips = page_size * (page - 1)
        cursor = APICallLog.collection.find({'api_id': ObjectId(api_id)}).skip(skips).limit(page_size)
        total_logs = APICallLog.collection.count_documents({'api_id': ObjectId(api_id)})
        return list(cursor), total_logs

    @staticmethod
    def delete(api_id):
        APICallLog.collection.delete_many({'api_id': ObjectId(api_id)})
