import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import threading
import asyncio


def get_episodes_url(link,num_of_episodes,category_url,db,prog):
    link = 'https://www1.gogoanime.ai' + link
    episode_links = []
    for a in range(1,num_of_episodes+1):
        html_content = requests.get(link+str(a))
        soup = BeautifulSoup(html_content.text, 'html.parser')
        iframe = soup.find('div', class_="play-video").iframe
        src = iframe['src']
        src = "https:" + src
        iframe['src'] = src
        episode_links.append(iframe['src'])
    data = {'href': link,'category_url': category_url, 'number_ep': num_of_episodes, 'epsidoes_list':episode_links}
    db.anime_episodesURL_data.insert_one(data)
    prog+=1
    print(prog, "done")


client = MongoClient('mongodb+srv://admin:admin12345@cluster0.lnm7l.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.animes
db.anime_episodesURL_data.drop()

url_list = []
for a in db.anime_list.find():
    url_list.append(a)

prog = 0
for a in url_list:
    try:
        t = threading.Thread(target=get_episodes_url, args=(a['href'], int(a['number_ep']),a['category_url'], db,prog))
        t.start()
    except:
        print("Error equrred")



