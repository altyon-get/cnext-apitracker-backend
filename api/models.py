import pytz
from django.conf import settings
from pymongo import ReturnDocument, DESCENDING
from bson.objectid import ObjectId
from cnext_apitracker_backend.mongodb import mongodb

ist = pytz.timezone('Asia/Kolkata')


class APIList:
    collection = mongodb.get_collection(settings.API_LIST_COLLECTION_NAME)

    def __init__(self, endpoint, method, params=None, headers=None, body=None, status=0, code=0, updated_at=None, _id=None):
        self.endpoint = endpoint
        self.method = method
        self.params = params or {}
        self.headers = headers or {}
        self.body = body
        self.status = status
        self.code = code
        self.updated_at = updated_at
        self._id = _id

    def save(self, data=None):

        if data is None:
            data = {
                'endpoint': self.endpoint,
                'method': self.method,
                'params': self.params,
                'headers': self.headers,
                'body': self.body,
                'status': self.status,
                'code': self.code,
                'updated_at': self.updated_at,
            }

        if self._id:
            result = self.collection.find_one_and_update(
                {'_id': ObjectId(self._id)},
                {'$set': data},
                return_document=ReturnDocument.AFTER,
            )
            self._id = str(result['_id'])
        else:
            result = self.collection.insert_one(data)
            self._id = str(result.inserted_id)
            result = data

        return APIList(**result)

    @staticmethod
    def get_all():
        apis = list(APIList.collection.find())
        api_instances = []
        for api in apis:
            api['_id'] = str(api['_id'])
            if api['updated_at']: api['updated_at'] = api['updated_at'].replace(tzinfo=pytz.UTC).astimezone(ist)
            api_instance = APIList(**api)
            api_instances.append(api_instance)
        return api_instances

    @staticmethod
    def get_apis_with_pagination(query, page=1, page_size=10):
        skips = page_size * (page - 1)
        apis = list(APIList.collection.find(query).skip(skips).limit(page_size))
        total_apis = APIList.collection.count_documents(query)
        for api in apis:
            api['_id'] = str(api['_id'])
            latest_log = APICallLog.collection.find_one({'api_id': api['_id']},sort=[('_id', DESCENDING)], projection={'response_time': 1})
            response_time = latest_log.get('response_time') if latest_log else None
            api['response_time'] = response_time
            if api['updated_at']: api['updated_at'] = api['updated_at'].replace(tzinfo=pytz.UTC).astimezone(ist)
        return apis, total_apis, page, page_size

    @staticmethod
    def get_by_id(api_id):
        api_data = APIList.collection.find_one({'_id': ObjectId(api_id)})
        if api_data:
            api_data['_id'] = str(api_data['_id'])
            if api_data['updated_at']: api_data['updated_at'] = api_data['updated_at'].replace(tzinfo=pytz.UTC).astimezone(ist)
            return APIList(**api_data)
        return None

    @staticmethod
    def delete(api_id):
        try:
            result = APIList.collection.delete_one({'_id': ObjectId(api_id)})
            if result.deleted_count == 0:
                return False
            APICallLog.delete(api_id)
            return True
        except Exception as e:
            return False

class APICallLog:
    collection = mongodb.get_collection(settings.API_CALL_LOG_COLLECTION_NAME)

    def __init__(self, api_id, timestamp, response_time, _id=None, status_code=None):
        self.api_id = api_id
        self.timestamp = timestamp
        self.status_code = status_code
        self.response_time = response_time
        self._id = _id

    def save(self):
        if self._id:
            data = self.__dict__.copy()
            result = self.collection.find_one_and_update(
                {'_id': self._id},
                {'$set': data},
                return_document=ReturnDocument.AFTER,
            )
            self._id = result['_id']
        else:
            data = {
                'api_id': self.api_id,
                'timestamp': self.timestamp,
                'status_code': self.status_code,
                'response_time': self.response_time,
            }
            result = self.collection.insert_one(data)
            self._id = result.inserted_id
            result = data

    @staticmethod
    def get_by_api(api_id, page=1, page_size=10):
        skips = page_size * (page - 1)
        cursor = (APICallLog.collection.find({'api_id': api_id})
                  .sort('timestamp', DESCENDING) 
                  .skip(skips)
                  .limit(page_size))
        total_logs = APICallLog.collection.count_documents({'api_id': api_id})
        call_logs = list(cursor)
        for log in call_logs:
            log['_id'] = str(log['_id'])
            log['api_id'] = str(log['api_id'])
            log['timestamp'] = log['timestamp'].replace(tzinfo=pytz.UTC).astimezone(ist)
        return call_logs, total_logs

    @staticmethod
    def delete(api_id):
        APICallLog.collection.delete_many({'api_id': api_id})
