import requests as req
from bs4 import BeautifulSoup

class Settings:
    def __init__(self):
        self.expand = False
        self.hide_titles = False
        self.allow_colors = True

class EpisodeNumersList:
    def __init__(self):
        self.list = []
        self.ranges = []

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

        self.manga_canon = EpisodeNumersList()
        self.mixed_canon = EpisodeNumersList()
        self.filler = EpisodeNumersList()
        self.anime_canon = EpisodeNumersList()

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

    def __scrap_list_of_eps(self, soup, class_name, collection: EpisodeNumersList):
        s = soup.find('div',  { 'class': class_name })

        content = s.find_all('a')

        for child in content:
            episode = child.text

            if "-" in episode:
                collection.ranges.append(episode)

                if  self.settings.expand == True:
                    ep_list = expand_range(episode)
                    for ep in ep_list:
                        collection.list.append(ep)
                    continue

                collection.list.append(episode)
            else:
                if episode.isdigit() == True:
                    episode = int(episode)

                collection.list.append(episode)

    def __episode_list(self, soup):
        table = soup.find('table', { 'class': 'EpisodeList' })

        for i in table.find_all('th'):
            title = i.text
            self.episode_list.headers.append(title)

        for j in table.find_all('tr')[1:]:
            row_data = j.find_all('td')
            row = [i.text for i in row_data]

            if self.settings.allow_colors == True:
                ep_type = row[2]

                if self.settings.hide_titles == True:
                    row[1] = 'x'*len(row[1])

                if ep_type == "Manga Canon":
                    color_row(row, "green")
                elif ep_type == "Mixed Canon/Filler":
                    color_row(row, "orange3")
                elif ep_type == "Filler":
                    color_row(row, "red")
                elif ep_type == "Anime Canon":
                    color_row(row, "cyan")

            self.episode_list.body.append(row)

    def check_type(self, ep):
        # Check list
        if ep in self.manga_canon.list: return "Manga canon"
        elif ep in self.mixed_canon.list: return "Mixed canon"
        elif ep in self.filler.list: return "Filler"
        elif ep in self.anime_canon.list: return "Anime Canon"

        # Check ranges
        if check_ranges(ep, self.manga_canon.ranges) == True: return "Manga canon"
        elif check_ranges(ep, self.mixed_canon.ranges) == True: return "Mixed canon"
        elif check_ranges(ep, self.filler.ranges) == True: return "Filler"
        elif check_ranges(ep, self.anime_canon.ranges) == True: return "Anime canon"

    def print_list(self, list):
        for i in list:
            print(i)

def check_ranges(ep, ranges):
    for r in ranges:
        start, end = map(int, r.split("-"))

        if start <= ep <= end:
            return True

def get_color_by_type(ep_type):
    if ep_type == "Manga canon":
        return "green"
    elif ep_type == "Mixed canon":
        return "orange3"
    elif ep_type == "Filler":
        return "red"
    elif ep_type == "Anime canon":
        return "cyan"

def expand_range(string: str) -> list[int]:
    result = []

    if "-" in string:
        start, end = string.split("-")

        if start.isdigit() == False or end.isdigit() == False: return []

        start = int(start)
        end = int(end)

        for j in range(start, end+1):
            result.append(j)

    return result

def color_row(row, color):
    row[0] = f"[{color}]{row[0]}[/ {color}]"
    row[1] = f"[{color}]{row[1]}[/ {color}]"
    row[2] = f"[{color}]{row[2]}[/ {color}]"
    row[3] = f"[{color}]{row[3]}[/ {color}]"
