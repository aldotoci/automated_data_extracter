import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import threading
import asyncio

def return_data(a,db):
    url = "https://ajax.gogo-load.com/ajax/load-list-episode?ep_start=0&ep_end=100000&id="
    #geting episode url
    episode_url = url + str(a)
    web_page = requests.get(episode_url)
    soup = BeautifulSoup(web_page.text, 'html.parser')
    try:
        li = soup.find('ul', attrs={'id':'episode_related'}).find_all('li')[0]
        #geting numbers of episodes
        number_ep = li.find('div').text[3:]
        href = li.a['href'][1:-1 *(len(number_ep))]

        #getting category_anime_url
        web_page = requests.get('https://www1.gogoanime.ai' + href + '1')
        soup = BeautifulSoup(web_page.text, 'html.parser')
        category_url = soup.find('div', {'class':'anime-info'}).a['href']

        data = {'href':href,'number_ep':number_ep,"category_url":category_url}
        db.anime_list.insert_one(data)

    except:
        print("Error")


prog = 0
client = MongoClient('mongodb+srv://admin:admin12345@cluster0.lnm7l.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.animes
db.anime_list.drop()
for a in range(1,10801):
    prog += 1
    t = threading.Thread(target=return_data, args=(a,db))
    t.start()
    print(prog)



