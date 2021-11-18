import anime_list
from pymongo import MongoClient

#Storing the data the in mangodb
client = MongoClient('mongodb+srv://admin:admin12345@cluster0.lnm7l.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.animes

try:
    db.anime_list.insert_many(anime_list.anime_list)
except:
    db.anime_list.drop()
    db.anime_list.insert_many(anime_list.anime_list)

