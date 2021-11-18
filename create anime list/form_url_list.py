import requests
from bs4 import BeautifulSoup
import threading

class get_anime_list:
    def __init__(self):
        self.url = "https://gogoanime.ai/anime-list.html?page=",
        self.num_pages = 65
        self.py_list = {}
        self.progress = 0
        self.t1 = None

    def get_anime_list_for_page(self, url):
        #Getting the html
        page = requests.get(url)

        #Getting the unordered list
        soup = BeautifulSoup(page.text, 'html.parser')
        html_list = soup.find('ul', class_='listing')

        py_list = []

        #Adding key to the dictionary for every anime list page
        for link in html_list.find_all('a'):
            #Getting the title and the episodes url
            anime_list_link = link.get('href')
            anime_link = link.get('href')[10:]
            anime_title = link.get_text()

            #Removing ' in the title
            anime_title_no_comma = ''
            for x in anime_title:
                if x == "'" or x == "\"" :
                    anime_title_no_comma += "\\'"
                else:
                    anime_title_no_comma += x
            anime_title = anime_title_no_comma

            #Creating an acceptle key
            acc_title = ''
            for a in anime_link:
                if a == '-':
                    acc_title += ' '
                elif a == '\'':
                    acc_title += '\\\''
                elif a == '\"':
                    acc_title += '\\\"'
                else:
                    acc_title += a

            #Getting the numbers of episode
            page = requests.get('https://gogoanime.ai' + anime_list_link)
            soup = BeautifulSoup(page.text, 'html.parser')
            html_list = soup.find('ul', {"id": "episode_page"})

            for li in html_list.find_all('a'):
                last_list = ''
                for a in li:
                    last_list += a
                if len(last_list) - 3 == 0 or len(last_list) % 4 == 0:
                    num_of_episodes = last_list[2:]
                elif len(last_list) - 6 == 0:
                    num_of_episodes = last_list[3:]
                elif len(last_list) - 7 == 0:
                    num_of_episodes = last_list[4:]
                elif len(last_list) - 8 == 0:
                    num_of_episodes = last_list[4:]
                elif len(last_list) - 9 == 0:
                    num_of_episodes = last_list[5:]

            #Storing the data in dictionary
            if '.' or '?' in anime_title:
                py_list.append({"url": anime_link,'episodes number': int(num_of_episodes), "original_title": anime_title})
            else:
                beta_title = ''
                for a in anime_title:
                    if a == '\'':
                        beta_title += '\\\''
                    elif a == '\"':
                        beta_title += '\\\"'
                    else:
                        beta_title += a
                    anime_title = beta_title
                py_list.append({"url": anime_link,"episodes number": int(num_of_episodes), "original_title": anime_title})
            self.progress += 1
            print(self.progress)

        anime_list = open('create anime list/anime_list.py', 'a', encoding='utf-8')
        py_list = str(py_list)
        py_list = py_list[1:len(str(py_list))-1]
        print(py_list)

        anime_list.write(py_list + ',')
        anime_list.close()

    def join_all_pages_in_one_list(self):
        self.url = ''.join(self.url)
        #searcing for every anime
        for num in range(self.num_pages):
            new_url = self.url + str(num+1)

            self.t1 = threading.Thread(target=self.get_anime_list_for_page, args=(new_url,))
            self.t1.start()

            self.progress += 10000

    #Sotring data in py lists
    def store_data(self):
        #Deleting previous list from the anime list
        anime_list = open('create anime list/anime_list.py', 'w', encoding='utf-8')
        anime_list.write('anime_list = ')
        anime_list.close()

        #Waiting for the data to process
        self.join_all_pages_in_one_list()
        self.t1.join()
        return self.py_list

gogoanime = get_anime_list()
py_list = gogoanime.store_data()

'''
#Storing the data the in mangodb
client = MongoClient('mongodb+srv://admin:admin12345@cluster0.lnm7l.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.animes

try:
    db.anime_list.insert_one(py_list)
except:
    db.anime_list.drop()
    db.anime_list.insert_one(py_list)
'''