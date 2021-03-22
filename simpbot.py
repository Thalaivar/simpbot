import tweepy
import yaml

KEYS_FILE = "./keys.yaml"

def auth_app():
    with open(KEYS_FILE, "r") as f:
        keys = yaml.load(f, Loader=yaml.FullLoader)
    
    auth = tweepy.OAuthHandler(keys["api_key"], keys["api_key_secret"])
    auth.set_access_token(keys["access_token"], keys["access_token_secret"])
    api = tweepy.API(auth)

    return api