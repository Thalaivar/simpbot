import time
import tweepy
import yaml
import logging
import schedule
import random
import pandas as pd

from lyricsScraper import LyricsScraper

logging.basicConfig(
                filename="tweepy.log",
                filemode='a',
                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                datefmt='%H:%M:%S',
                level=logging.INFO
            )

# BASE_DIR = "/home/dhruvlaad"
BASE_DIR = "."
KEYS_FILE = f"{BASE_DIR}/keys.yaml"
SONGS_FILE = f"{BASE_DIR}/songsfile.csv"
MAX_LEN = 280

class Simpbot():
    def __init__(self, keys_file: str, lyrics_freq=1, check_freq=30):
        self.keys_file = keys_file
        with open(keys_file, "r") as f:
            keys = yaml.load(f, Loader=yaml.FullLoader)
        self.keys = keys

        auth = tweepy.OAuthHandler(keys["api_key"], keys["api_key_secret"])
        auth.set_access_token(keys["access_token"], keys["access_token_secret"])
        self.api = tweepy.API(auth)
        self.user_data = self.api.get_user(keys["account"])

        self.scraper = LyricsScraper(keys["google_cse_api"], keys["google_cse_id"])
        self.lyrics_freq = lyrics_freq
        self.check_freq = check_freq

    def rt_and_like(self):
        kwargs = {
                "user_id": self.user_data.id_str,
                "screen_name": self.user_data.screen_name,
                "exclude_replies": False,
                "include_rts": False,
                "count": 20
            }
        last_id = None

        while True:
            if last_id:
                kwargs["max_id"] = last_id
            data = list(self.api.user_timeline(**kwargs))

            found = False
            for d in data:
                if d.in_reply_to_screen_name == self.keys["account"]:
                    if not d.favorited:
                        self.api.create_favorite(d.id)
                        logging.info(f"Liked tweet with ID: {d.id_str} ; text: {d.text}")
                    if not d.retweeted:
                        self.api.retweet(d.id)
                        logging.info(f"Retweeted tweet with ID: {d.id_str} ; text: {d.text}")
                    if d.retweeted and d.favorited:
                        found = True

            if found:
                break
            last_id = data[-1].id
    
    def tweet_lyrics(self, songsfile: str):
        songs = pd.read_csv(songsfile)
        idx = random.randint(0, songs.shape[0]-1)        
        lyrics = self.scraper.scrape(songs["Track Name"][idx] + " " + songs["Arist(s) Name"][idx]) 
        return random.sample(lyrics, 1)

def spin():
    bot = Simpbot(KEYS_FILE)
    # schedule.every(self.lyrics_freq).hour.do(self.tweet_lyrics, songsfile=SONGS_FILE)
    schedule.every(bot.check_freq).seconds.do(bot.rt_and_like)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    spin()