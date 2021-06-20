from simpbot import auth_app, get_user_data

TWEETS_PER_CALL = 100

def get_tweet_reply_pairs(n=100000):
    tweet_data = {"tweet": [], "reply": []}
    count, last_id = 0, -1

    api = auth_app()
    user = get_user_data(api)

    while count < n:
        kwargs = {
            "user_id": user.id_str,
            "screen_name": user.screen_name,
            "exclude_replies": False,
            "include_rts": False,
            "count": TWEETS_PER_CALL
        }
        
        if last_id > 0:
            kwargs["max_id"] = last_id
        
        data = list(api.user_timeline(**kwargs))

        for d in data:
            
    