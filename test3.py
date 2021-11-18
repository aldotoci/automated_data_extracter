import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import threading
import asyncio

def get_info_per_anime(href,link,num_ep, epsidoes_list,db):
    anime_data = []
    anime_list_link = 'https://gogoanime.ai' + link

    #Getting the anime_list page
    anime_page = requests.get(anime_list_link)
    anime_soup = BeautifulSoup(anime_page.text, 'html.parser')

    #Getting info about the anime
    data = anime_soup.find('div', class_="anime_info_body_bg")

    title = data.h1.text
    thumbnail = data.find('img').get('src')
    data = data.find_all('p')
    type = data[1].find('a').get_text()
    plot = data[2].get_text()[14:]
    genre = []
    for gen in data[3].find_all('a'):
        genre.append(gen.get('title'))
    realease = data[4].get_text()[10:]
    status = data[5].get_text()[9:len(data[5].get_text())-1]
    other_names = []
    names = data[6].get_text()[12:]
    name = ""
    for char in names:
        if char == ",":
            other_names.append(name)
            name = ""
            continue
        elif name == "":
            if char == " ":
                continue
            else:
                name += char
        else:
            name += char
            if char == names[len(names)-1]:
                other_names.append(name)


    data = {'title': title,'number_of_episodes':num_ep,'url':link,'thumbnail': thumbnail,'type':type,'plot': plot,'genre':genre,'realease':realease,'status':status,'othernames':other_names,'href':href,'epsidoes_list':epsidoes_list}
    db.database_test.insert_one(data)


client = MongoClient('mongodb+srv://admin:admin12345@cluster0.lnm7l.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.animes
db.database_test.drop()

url_list = []
for a in db.anime_episodesURL_data.find():
    url_list.append(a)

prog = 0
for a in url_list:
    try:
        t = threading.Thread(target=get_info_per_anime, args=(a['href'], a['category_url'], int(a['number_ep']),a['epsidoes_list'], db))
        t.start()
    except:
        print("Error equrred")