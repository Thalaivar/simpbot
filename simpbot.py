import time
import yaml
import torch
import tweepy
import random
import schedule
import logging
from transformers import GPT2LMHeadModel, GPT2Tokenizer

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

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')

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

def tweet(api: tweepy.API):
    prompts = [
        "she is the",
        "she is",
        "she has",
        "she can",
        "she will"
    ]

    inputs = tokenizer.encode(random.sample(prompts, 1)[0], return_tensors='pt')
    outputs = model.generate(inputs, max_length=10, do_sample=True)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    end_marks = [',', '.', '?']
    for mark in end_marks:
        if mark in text:
            text = text.split(mark)[0]
            break
    
    text = text.replace("she ", "anaita ")
    api.update_status(text)
    
def spin():
    api = auth_app()
    user = get_user_data(api)
    schedule.every(5).seconds.do(lambda: run(api, user))
    schedule.every(4).hours.do(lambda: tweet(api))
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    spin()