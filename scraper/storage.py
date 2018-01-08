import json
import pymongo

class Storage:
    def __init__(self, uri):
        self._client = pymongo.MongoClient(uri)
        self._db = None
        self._collection = None

    def connect_db(self, db_name):
        self._db = self._client[db_name]

    def set_collection(self, col_name):
        self._collection = getattr(self._db, col_name)

    def find(self, obj):
        return self._collection.find_one(obj)

    def find_all(self, obj):
        return self._collection.find(obj)

    def insert(self, docs):
        if isinstance(docs, list):
            self._collection.insert_many(docs)
        else:
            self._collection.insert(docs)
