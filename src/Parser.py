import re
import os
from typing import Tuple
import requests
from requests import RequestException
from bs4 import BeautifulSoup
from bs4.element import ResultSet
from numbers import Real
from time import sleep

class Parser:
    def __init__(self, n_repeats: int = 3, time_wait: Real = 3) -> None:
        self._n_repeats = n_repeats
        self._time_wait = time_wait

    def request(self, url: str) -> bytes:
        for i in range(self._n_repeats):
            response = requests.get(url)
            if 200 <= response.status_code < 300:
                break
            else:
                print(f'Bad response: {response.status_code}\n'
                f'Request will be repeated in 3 seconds. Attempts left: {self._n_repeats - i - 1}')
                sleep(3)
        
        if not 200 <= response.status_code < 300:
            raise RequestException(f'Bad response: {response.status_code}')
        return response.content
    
    def search_song(self, artist: str, song: str) -> bytes:
        query = artist.split(' ') + song.split(' ')
        query = '+'.join(query)
        url = f'https://amdm.ru/search/?q={query}'
        return self.request(url)
        
    def _print_song_names(self, songs_list: ResultSet) -> None:
        for i, r in enumerate(songs_list):
            print(i, r.contents[0].contents[0], ' - ', r.contents[2].contents[0])

    def parse_search_page(self, page_content: bytes) -> ResultSet:
        page = BeautifulSoup(page_content, 'html.parser')
        songs_list = page.table.find_all('td', {'class': 'artist_name'})
        print(f'Found {len(songs_list)} songs:')
        self._print_song_names(songs_list)
        return songs_list

    def get_song_url_by_index(self, songs_list: ResultSet, index: int) -> str:
        song_url = songs_list[index].contents[2].get('href')
        if song_url.startswith('//'):
            song_url = 'https:' + song_url
        return song_url

    def get_song_fullname(self, song_page: ResultSet) -> str:
        full_name = ' - '.join([head_text.contents[0] for head_text in song_page.h1.find_all('span')])
        return full_name
    
    def get_song_text(self, song_page: ResultSet) -> str:
        raw_text = song_page.find_all('pre', {'itemprop': 'chordsBlock'})
        lines = [str(line) for line in raw_text[0].contents]
        lines = [re.sub('<[^<]+?>', '', line) for line in lines]
        text = ''.join(lines)
        return text

    def parse_song_page(self, song_url: str) -> Tuple[str]:
        song_page = BeautifulSoup(self.request(song_url), 'html.parser')
        full_name = self.get_song_fullname(song_page)
        song_text = self.get_song_text(song_page)
        return full_name, song_text

    def save_to_file(self, folder: str, song_name: str, song_text: str) -> None:
        filename = folder + '/' + song_name + '.md'
        with open(filename, 'w') as f:
            f.write(song_text)

    def get_songs_list(self, artist: str, song: str) -> ResultSet:
        page_content = self.search_song(artist, song)
        songs_list = self.parse_search_page(page_content)
        return songs_list

    def __call__(self, artist: str, song: str, folder: str) -> None:
        songs_list = self.get_songs_list(artist, song)
        song_url = self.get_song_url_by_index(songs_list, 0)
        song_name, song_text = self.parse_song_page(song_url)
        self.save_to_file(folder=folder, song_name=song_name, song_text=song_text)
        
        