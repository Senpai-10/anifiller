import requests as req
from bs4 import BeautifulSoup

class Settings:
    def __init__(self):
        self.expand = False
        self.hide_titles = False

class EpisodeList:
    def __init__(self):
        self.headers = []
        self.body = []

class AnimeFillerList:
    def __init__(self, anime_name) -> None:
        self.__anime_name = anime_name
        self.__url = f"https://www.animefillerlist.com/shows/{self.__anime_name}"
        self.__page_found = True
        self.settings = Settings()

        self.manga_canon = []
        self.mixed_canon = []
        self.filler = []
        self.anime_canon = []

        # Table of filler list
        #(index) | Title | Type(Mixed Canon/Filler/Manga Canon/Anime Canon) | Airdate
        self.episode_list = EpisodeList()

    def start(self):
        self.__scrap()
        self.__check_if_page_exists()

    def __check_if_page_exists(self):
        if self.__page_found == False:
            print(f"'{self.__url}': Page not found!")

    def __scrap(self):
        t = req.get(self.__url)

        if t.status_code != 200:
            self.__page_found = False
            return

        soup = BeautifulSoup(t.content, 'html.parser')

        self.__scrap_list_of_eps(soup, "manga_canon", self.manga_canon)
        self.__scrap_list_of_eps(soup, "mixed_canon/filler", self.mixed_canon)
        self.__scrap_list_of_eps(soup, "filler", self.filler)
        self.__scrap_list_of_eps(soup, "anime_canon", self.anime_canon)

        self.__episode_list(soup)

    def __scrap_list_of_eps(self, soup, class_name, list):
        s = soup.find('div',  { 'class': class_name })

        content = s.find_all('a')

        for child in content:
            episode = child.text

            if "-" in episode and self.settings.expand == True:
                ep_list = expand_range(episode)
                for ep in ep_list:
                    list.append(ep)
            else:
                if episode.isdigit() == True:
                    episode = int(episode)

                list.append(episode)

    def __episode_list(self, soup):
        table = soup.find('table', { 'class': 'EpisodeList' })

        for i in table.find_all('th'):
            title = i.text
            self.episode_list.headers.append(title)

        for j in table.find_all('tr')[1:]:
            row_data = j.find_all('td')
            row = [i.text for i in row_data]

            self.episode_list.body.append(row)

def expand_range(s: str) -> list[int]:
    result = []

    if "-" in s:
        start, end = s.split("-")

        if start.isdigit() == False or end.isdigit() == False: return []

        start = int(start)
        end = int(end)

        for j in range(start, end+1):
            result.append(j)

    return result

