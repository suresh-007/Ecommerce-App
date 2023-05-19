import pymongo
import json
from bson.objectid import ObjectId

def connection():
    try:
        mongocli = pymongo.MongoClient(
                host = 'localhost',
                port = 27017,
                serverSelectionTimeoutMS = 1000
            )
        print("DB Cionnection Established")
        db = mongocli.marvelDB #connect to mongodb1
        mongocli.server_info() #trigger exception if cannot connect to db
        return db
    except:
        print("Error -connect to db")