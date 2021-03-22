import time
import tweepy
import yaml
import logging

logging.basicConfig(
                filename="tweepy.log",
                filemode='a',
                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                datefmt='%H:%M:%S',
                level=logging.INFO
            )

KEYS_FILE = "./keys.yaml"

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
    last_id = keys["last"]
    
    if not last_id:
        last_id = -1
    
    data = list(api.user_timeline(
                    user_id=user.id_str, 
                    screen_name=user.screen_name, 
                    exclude_replies=False, 
                    include_rts=False,
                    count=10
                    )
                )

    for d in data[::-1]:
        if (d.id > last_id) and (d.in_reply_to_screen_name is None or d.in_reply_to_screen_name == keys["account"]):
            if not d.favorited:
                api.create_favorite(d.id)
                logging.info("Liked tweet with ID: {d.id_str}")
            if not d.retweeted:
                api.retweet(d.id)
                logging.info(f"Retweeted tweet with ID: {d.id_str}")
            last_id = int(d.id_str)
    
    keys["last"] = last_id
    with open(KEYS_FILE, "w") as f:
        yaml.dump(keys, f, default_flow_style=False)    

def spin(freq=120):
    freq = 60 * 60 // freq
    api = auth_app()
    user = get_user_data(api)
    while True:
        run(api, user)
        time.sleep(freq)

if __name__ == "__main__":
    spin()