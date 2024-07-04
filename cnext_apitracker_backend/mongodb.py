from pymongo import MongoClient
from django.conf import settings


class MongoDB:
    def __init__(self):
        self.client = MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB_NAME]

    def get_collection(self, collection_name):
        return self.db[collection_name]


mongodb = MongoDB()
