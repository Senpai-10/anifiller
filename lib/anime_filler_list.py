import requests as req
from bs4 import BeautifulSoup
from dataclasses import dataclass
from enum import Enum
from difflib import get_close_matches

def did_you_mean(query) -> list[str]:
    url = 'https://www.animefillerlist.com/shows'

    response = req.get(url)

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    s = soup.find('div',  { 'id': 'ShowList' })

    assert s != None

    links = s.find_all('a', href=True)

    shows: list[str] = []

    for link in links:
        show_name: str = link['href'].split('/')[-1]

        shows.append(show_name)

    return get_close_matches(query, shows)

class EpType(Enum):
    Manga_canon = "Manga canon"
    Mixed_canon = "Mixed Canon/Filler"
    Filler = "Filler"
    Anime_canon = "Anime Canon"
    Unknown = "Unknown"

@dataclass
class Row:
    episode_number: int
    title: str
    episode_type: EpType
    airdate: str

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
        self.headers: list[str] = []
        self.body: list[Row] = []

class AnimeFillerList:
    def __init__(self, anime_name):
        self.__anime_name = anime_name
        self.__url = f"https://www.animefillerlist.com/shows/{self.__anime_name}"
        self.settings = Settings()
        self.connection_failure = False
        t = req.get(self.__url)

        if t.status_code != 200:
            self.connection_failure = True

        self.soup = BeautifulSoup(t.content, 'html.parser')

    def manga_canon(self) -> EpisodeNumersList:
        return self.__build_quick_list("manga_canon")

    def mixed_canon(self) -> EpisodeNumersList:
        return self.__build_quick_list("mixed_canon/filler")

    def filler(self) -> EpisodeNumersList:
        return self.__build_quick_list("filler")

    def anime_canon(self) -> EpisodeNumersList:
        return self.__build_quick_list("anime_canon")

    def __build_quick_list(self, class_name: str) -> EpisodeNumersList:
        s = self.soup.find('div',  { 'class': class_name })

        assert s != None

        content = s.find_all('a')

        quick_list: EpisodeNumersList = EpisodeNumersList()

        for child in content:
            episode = child.text

            if "-" in episode:
                quick_list.ranges.append(episode)

                if  self.settings.expand == True:
                    ep_list = expand_range(episode)
                    for ep in ep_list:
                        quick_list.list.append(ep)
                    continue

                quick_list.list.append(episode)
            else:
                if episode.isdigit() == True:
                    episode = int(episode)

                quick_list.list.append(episode)

        return quick_list

    def episode_list(self) -> EpisodeList:
        table = self.soup.find('table', { 'class': 'EpisodeList' })

        ep_list: EpisodeList = EpisodeList()

        for i in table.find_all('th'):
            title = i.text
            ep_list.headers.append(title)

        for j in table.find_all('tr')[1:]:
            row_data = j.find_all('td')
            tmp_row = [i.text for i in row_data]
            row = Row(episode_number=tmp_row[0], title=tmp_row[1], episode_type=convert_ep_type(tmp_row[2]), airdate=tmp_row[3])

            if self.settings.allow_colors == True:
                if self.settings.hide_titles == True:
                    row.title = 'x'*len(row.title)

            ep_list.body.append(row)

        return ep_list

    def print_list(self, list: list[str]) -> None:
        for i in list:
            print(i)

def get_color_by_type(ep_type: EpType) -> str:
    result = "white"

    if ep_type == EpType.Manga_canon:
        result = "green"
    elif ep_type == EpType.Mixed_canon:
        result = "orange3"
    elif ep_type == EpType.Filler:
        result = "red"
    elif ep_type == EpType.Anime_canon:
        result = "cyan"

    return result

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

def colored(color: str, v: str) -> str:
    return f"[{color}]{v}[/ {color}]"

def convert_ep_type(s: str) -> EpType:
    if s == "Manga Canon":
        return EpType.Manga_canon
    elif s == "Mixed Canon/Filler":
        return EpType.Mixed_canon
    elif s == "Filler":
        return EpType.Filler
    elif s == "Anime Canon":
        return EpType.Anime_canon

    return EpType.Unknown

