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

class Connection(Enum):
    Success = 1
    Failure = 2

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

        self.manga_canon = EpisodeNumersList()
        self.mixed_canon = EpisodeNumersList()
        self.filler = EpisodeNumersList()
        self.anime_canon = EpisodeNumersList()

        # Table of filler list
        #(index) | Title | Type(Mixed Canon/Filler/Manga Canon/Anime Canon) | Airdate
        self.episode_list = EpisodeList()

    def start(self) -> Connection:
        return self.__scrap()

    def __scrap(self) -> Connection:
        t = req.get(self.__url)

        if t.status_code != 200:
            return Connection.Failure

        soup = BeautifulSoup(t.content, 'html.parser')

        self.__scrap_list_of_eps(soup, "manga_canon", self.manga_canon)
        self.__scrap_list_of_eps(soup, "mixed_canon/filler", self.mixed_canon)
        self.__scrap_list_of_eps(soup, "filler", self.filler)
        self.__scrap_list_of_eps(soup, "anime_canon", self.anime_canon)

        self.__episode_list(soup)

        return Connection.Success

    def __scrap_list_of_eps(self, soup, class_name: str, collection: EpisodeNumersList) -> None:
        s = soup.find('div',  { 'class': class_name })

        if s == None: return None
        assert s != None

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

    def __episode_list(self, soup) -> None:
        table = soup.find('table', { 'class': 'EpisodeList' })

        for i in table.find_all('th'):
            title = i.text
            self.episode_list.headers.append(title)

        for j in table.find_all('tr')[1:]:
            row_data = j.find_all('td')
            tmp_row = [i.text for i in row_data]
            row = Row(episode_number=tmp_row[0], title=tmp_row[1], episode_type=convert_ep_type(tmp_row[2]), airdate=tmp_row[3])

            if self.settings.allow_colors == True:
                if self.settings.hide_titles == True:
                    row.title = 'x'*len(row.title)

                # MAYNOT WORK! CHECK THE EPISODE_TYPE INSIDE THE FUNCTION
                # if row.episode_type == EpType.Manga_canon:
                #     color_row(row, "green")
                # elif row.episode_type == EpType.Mixed_canon:
                #     color_row(row, "orange3")
                # elif row.episode_type == EpType.Filler:
                #     color_row(row, "red")
                # elif row.episode_type == EpType.Anime_canon:
                #     color_row(row, "cyan")

            self.episode_list.body.append(row)

    def check_type(self, ep) -> EpType:
        # Check list
        if ep in self.manga_canon.list: return EpType.Manga_canon
        elif ep in self.mixed_canon.list: return EpType.Mixed_canon
        elif ep in self.filler.list: return EpType.Filler
        elif ep in self.anime_canon.list: return EpType.Anime_canon

        # Check ranges
        if check_ranges(ep, self.manga_canon.ranges) == True: return EpType.Manga_canon
        elif check_ranges(ep, self.mixed_canon.ranges) == True: return EpType.Mixed_canon
        elif check_ranges(ep, self.filler.ranges) == True: return EpType.Filler
        elif check_ranges(ep, self.anime_canon.ranges) == True: return EpType.Anime_canon

        # Can't Find ep Type
        return EpType.Unknown

    def print_list(self, list: list[str]) -> None:
        for i in list:
            print(i)

def check_ranges(ep: int, ranges: list[str]):
    for r in ranges:
        start, end = map(int, r.split("-"))

        if start <= ep <= end:
            return True

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

