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
        self.updated_at = updated_at
        self._id = _id

    def save(self):
        data = self.__dict__.copy()
        if self._id:
            data['_id'] = ObjectId(self._id)
            result = self.collection.find_one_and_update(
                {'_id': self._id},
                {'$set': data},
                return_document=ReturnDocument.AFTER,
            )
            self._id = result['_id']
        else:
            result = self.collection.insert_one(data)
            self._id = result.inserted_id

    @staticmethod
    def get_all():
        apis = list(APIList.collection.find())
        for api in apis:
            api['_id'] = str(api['_id'])
        return apis

    @staticmethod
    def get_by_id(api_id):
        api = APIList.collection.find_one({'_id': ObjectId(api_id)})
        if api:
            api['_id'] = str(api['_id'])
        return api

    @staticmethod
    def delete(api_id):
        return APIList.collection.delete_one({'_id': ObjectId(api_id)})


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
            result = self.collection.find_one_and_update(
                {'_id': self._id},
                {'$set': data},
                return_document=ReturnDocument.AFTER,
            )
            self._id = result['_id']
        else:
            result = self.collection.insert_one(data)
            self._id = result.inserted_id

    @staticmethod
    def get_by_api(api_id, page=1, page_size=10):
        skips = page_size * (page - 1)
        cursor = (APICallLog.collection
                  .find({'api_id': ObjectId(api_id)})
                  .skip(skips)
                  .limit(page_size))
        total_logs = APICallLog.collection.count_documents({'api_id': ObjectId(api_id)})
        call_logs = list(cursor)
        for log in call_logs:
            log['_id'] = str(log['_id'])
            log['api_id'] = str(log['api_id'])
        return call_logs, total_logs

    @staticmethod
    def delete(api_id):
        APICallLog.collection.delete_many({'api_id': ObjectId(api_id)})
