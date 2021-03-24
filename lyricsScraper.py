import requests
from bs4 import BeautifulSoup

class LyricScraperException(Exception):
    """ Handles all LyricsScraper exceptions"""

class LyricsScraper():
    # scraper_list = {
    #     "jiosaavn": self.jiosaavn_scraper,
        
    # }
    def __init__(self, google_cse_api: str, google_cse_id: str):
        self.api_key = google_cse_api
        self.id = google_cse_id
    
    def raw_data(self, song_name):
        url = "https://www.googleapis.com/customsearch/v1/siterestrict"
        params = {
            'key': self.api_key,
            'cx': self.id,
            'q': '{} lyrics'.format(song_name),
        }

        response = requests.get(url, params=params)
        data = response.json()
        if response.status_code != 200:
            raise LyricScraperException(data)

        return data
        
    def scrape(self, song_name):
        data = self.raw_data(song_name)
        spell = data.get('spelling', {}).get('correctedQuery')
        data = (spell and self.raw_data(spell)) or data
        query_results = data.get('items', [])
        
        for result in query_results:
            link  = result.get("link")


    
    def jiosaavn_scraper(self, raw):
        pass

    def geetmanjusha(self, raw):
        pass
