import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import threading

class store_info_in_database:
    def get_Episodes_Urls(self, link, num_Of_Episodes):

        episode_links = []
        for a in range(1,num_Of_Episodes+1):
            html_content = requests.get(link+str(a))
            soup = BeautifulSoup(html_content.text, 'html.parser')
            iframe = soup.find('div', class_="play-video").iframe
            src = iframe['src']
            src = "https:" + src
            iframe['src'] = src
            episode_links.append(iframe['src'])

        return episode_links

    def get_info_per_anime(self, link,number_of_episodes):
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


        data = {'title': title,'number_of_episodes':number_of_episodes,'url':link,'thumbnail': thumbnail,'type':type,'plot': plot,'genre':genre,'realease':realease,'status':status,'othernames':other_names}
        return data

    def return_data(self, a):
        url = "https://ajax.gogo-load.com/ajax/load-list-episode?ep_start=0&ep_end=100000&id="
        #geting episode url
        episode_url = url + str(a)
        web_page = requests.get(episode_url)
        soup = BeautifulSoup(web_page.text, 'html.parser')
        try:
            li = soup.find('ul', attrs={'id':'episode_related'}).find_all('li')[0]
        except:
            return
        #geting numbers of episodes
        number_ep = li.find('div').text[3:]
        href = li.a['href'][1:-1 *(len(number_ep))]


        #getting category url
        web_page = requests.get('https://www1.gogoanime.ai' + href + '1')
        soup = BeautifulSoup(web_page.text, 'html.parser')
        try:
            category_href = soup.find('div', {'class': 'anime-info'}).a['href']
        except:
            return

        data = self.get_info_per_anime(category_href, number_ep)

        episode_url_array = self.get_Episodes_Urls('https://www1.gogoanime.ai' + href, int(number_ep))
        data['episodes_url_array'] = episode_url_array
        return data

    def store_data_in_database(self,a, db):

        try:
            #Getting info
            anime_data = self.return_data(a)
            #Store data in database
            try:
                db.anime_data_list.insert_one(anime_data)
            except:
                print("An error occurred.")
        except NameError:
            print('Error equred at index: ', str(a), " ", NameError)


    def get_anime_watch_url(self):
        client = MongoClient('mongodb+srv://admin:admin12345@cluster0.lnm7l.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
        db = client.animes
        db.anime_data_list.drop()

        for a in range(1,10801):
            t = threading.Thread(target=self.store_data_in_database, args=(a,db))
            t.start()

test = store_info_in_database()
test.get_anime_watch_url()