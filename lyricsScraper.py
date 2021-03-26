import re
import requests
from bs4 import BeautifulSoup

class LyricsNotFoundError(Exception):
    def __init__(self, song_name):
        self.message = f"lyrics for {song_name} was not found in any of the specified sites"
        super().__init__(self.message)

class LyricsScraper():
    def __init__(self, google_cse_api: str, google_cse_id: str, genius_access_token: str=None):
        self.api_key = google_cse_api
        self.id = google_cse_id
        self.genius_access_token = genius_access_token
    
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
            raise LyricsNotFoundError(song_name)

        return data
    
    def scrape(self, song_name):
        print(f"Scraping: {song_name}")
        data = self.raw_data(song_name)
        spell = data.get('spelling', {}).get('correctedQuery')
        data = (spell and self.raw_data(spell)) or data
        query_results = data.get('items', [])
        
        for result in query_results:
            url = result.get("link")
            scraper = self.choose_scraper(url)
            raw = requests.get(url)
            if raw.status_code == 200 and scraper:
                name, scraper = scraper                 
                lyrics = scraper(raw)
                if lyrics:
                    return lyrics
            
        raise LyricsNotFoundError(song_name)

    def genius_scraper(self, raw):
        parsed = BeautifulSoup(raw.content, "html.parser").find("div", class_=re.compile("^lyrics$|Lyrics__Root"))
        for br in parsed.find_all("br"):
            br.replace_with("\n")
        lyrics = parsed.get_text()

        i = 0
        while i < len(lyrics):
            if lyrics[i] == '[':
                lyrics = lyrics[:i] + lyrics[i + lyrics[i+1:].find(']') + 2:]
                i = 0
            i += 1
        
        lyrics = lyrics[lyrics.find(next(filter(str.isalpha, lyrics))):]
        lyrics = lyrics.replace("\n\n\n", "\n\n")
        return lyrics.split("\n\n")

    def ilyrics_hub_scraper(self, raw):
        parsed = BeautifulSoup(raw.content, "html.parser").find_all("div", attrs={"class": "song_lyrics"})[0]
        lyrics = parsed.find_all('p')
        for i, l in enumerate(lyrics):
            for br in l.find_all("br"):
                br.replace_with("\r\n")
            lyrics[i] = l.get_text()
        return lyrics

    def lyricsmint_scraper(self, raw):
        parsed = BeautifulSoup(raw.content, "html.parser").select("section", attrs={"id": "lyrics"})[1].select('p')[:-1]
        for p in parsed:
            for x in p.find_all("small"):
                x.decompose()
        lyrics = [p.get_text().replace("\n", "\r\n") for p in parsed]
        for k, s in enumerate(lyrics):
            # filter out "(x{n})"
            remove_idx = []
            for i, ch in enumerate(s):
                if ch.isdigit():
                    remove_idx.append(i)
                    if s[i-1] == 'x':
                        remove_idx.append(i-1)
                    if s[i-2] == '(':
                        remove_idx.append(i-2)
                    if s[i+1] == ')':
                        remove_idx.append(i+1)
                
                if ch == "(" or ch == ")":
                    remove_idx.append(i)
                    
            s = list(s)
            s = [s[i] for i in range(len(s)) if i not in remove_idx]
            lyrics[k] = "".join(s)
        return lyrics

    def jiosaavn_scraper(self, raw):
        parsed = BeautifulSoup(raw.content, "html.parser").select('p')[7]
        for br in parsed.find_all("br"):
            br.replace_with("\r\n")
        lyrics = parsed.get_text().split("\r\n\r\n")
        return lyrics

    def geetmanjusha_scraper(self, raw):
        parsed = BeautifulSoup(raw.content, "html.parser").select("pre")
        lyrics = parsed[0].get_text()
        lyrics = lyrics.split("\r\n\r\n")
        return lyrics

    def choose_scraper(self, url):
        scrapers = {
            "geetmanjusha": self.geetmanjusha_scraper,
            "jiosaavn": self.jiosaavn_scraper,
            "lyricsmint": self.lyricsmint_scraper,
            "ilyricshub": self.ilyrics_hub_scraper,
            "genius": self.genius_scraper,
        }

        for name, scraper in scrapers.items():
            if name in url:
                return (name, scraper)
        
        return None