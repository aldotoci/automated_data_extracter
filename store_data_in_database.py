import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import threading

class store_info_in_database:

    def get_info_per_anime(self, title, number_of_episodes, link):
        anime_data = []
        anime_list_link = 'https://gogoanime.ai/category/' + link

        #Getting the anime_list page
        anime_page = requests.get(anime_list_link)
        anime_soup = BeautifulSoup(anime_page.text, 'html.parser')

        #Getting info about the anime
        data = anime_soup.find('div', class_="anime_info_body_bg")
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

        data = {'title': title,'number_of_episodes':number_of_episodes,'url':link,'thumbnail': thumbnail,'type':type,'plot': plot,'genre':genre,'realease':realease,'status':status,'othernames':other_names}
        return data

    def store_data(self, anime, prog, anime_list,db):
        data = self.get_info_per_anime(anime['original_title'],anime['episodes number'],anime['url'])
        prog += 1
        try:
            db.anime_data_list.insert_one(data)
        except:
            print("An error occurred")
        print('Progress: ' + str(prog) + " out of " + str(len(anime_list)))

    def store_data_in_database(self):
        client = MongoClient('mongodb+srv://admin:admin12345@cluster0.lnm7l.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
        db = client.animes
        anime_list = []
        prog = 0
        db.anime_data_list.drop()

        for anime in db.anime_list.find():
            anime_list.append(anime)

        for anime in anime_list: #Fix latter
            t = threading.Thread(target=self.store_data, args=(anime,prog,anime_list,db))
            t.start()


test = store_info_in_database()
test.store_data_in_database()