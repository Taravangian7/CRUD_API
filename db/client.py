#Here I connect the API to my MongoDB Database
from pymongo import MongoClient
import certifi
ca = certifi.where()
#for local database
#db_client=MongoClient().local

#for remote database
db_client=MongoClient("mongodb+srv://YOUR_DB_USER:YOUR_DB_PASSWORD@cluster0.1zk7cvj.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca).test 