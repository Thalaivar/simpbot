import time
import tweepy
import yaml
import logging
import schedule

logging.basicConfig(
                filename="tweepy.log",
                filemode='a',
                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                datefmt='%H:%M:%S',
                level=logging.INFO
            )

KEYS_FILE = "./keys.yaml"
TWEETS_PER_CALL = 100
MAX_TWEETS = 1000

def auth_app():
    with open(KEYS_FILE, "r") as f:
        keys = yaml.load(f, Loader=yaml.FullLoader)
    
    auth = tweepy.OAuthHandler(keys["api_key"], keys["api_key_secret"])
    auth.set_access_token(keys["access_token"], keys["access_token_secret"])
    api = tweepy.API(auth)

    return api

def get_user_data(api: tweepy.API):
    with open(KEYS_FILE, "r") as f:
        keys = yaml.load(f, Loader=yaml.FullLoader)
    screen_name = keys["account"]
    
    return api.get_user(screen_name=screen_name)

def run(api: tweepy.API, user: tweepy.User):
    with open(KEYS_FILE, "r") as f:
        keys = yaml.load(f, Loader=yaml.FullLoader)
    
    curr_tweets = 0
    
    while curr_tweets < MAX_TWEETS:
        kwargs = {
                "user_id": user.id_str, 
                "screen_name": user.screen_name, 
                "exclude_replies": False, 
                "include_rts": False,
                "count": TWEETS_PER_CALL
            }
            
        data = list(api.user_timeline(**kwargs))

        for d in data:
            if (d.in_reply_to_screen_name is None) or (d.in_reply_to_screen_name == keys["account"]):
                if not d.favorited:
                    api.create_favorite(d.id)
                    logging.info(f"Liked tweet with ID: {d.id_str}")
                if not d.retweeted:
                    api.retweet(d.id)
                    logging.info(f"Retweeted tweet with ID: {d.id_str}")
        
        curr_tweets += TWEETS_PER_CALL

def spin():
    api = auth_app()
    user = get_user_data(api)
    schedule.every(5).seconds.do(lambda: run(api, user))

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    spin()