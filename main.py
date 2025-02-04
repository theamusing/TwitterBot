import configparser
import tweepy
import tweepy.client

config = configparser.ConfigParser(interpolation = None)
config.read('config.ini')

CONSUMER_KEY = config['twitter']['consumer_key']
CONSUMER_SECRET = config['twitter']['consumer_secret']
ACCESS_TOKEN = config['twitter']['access_token']
ACCESS_TOKEN_SECRET = config['twitter']['access_token_secret']
BEARER_TOKEN = config['twitter']['bearer_token']
CLIENT_ID = config['twitter']['client_id']
CLIENT_SECRET = config['twitter']['client_secret']

oauth2_user_handler = tweepy.OAuth2UserHandler(
    client_id = CLIENT_ID,
    redirect_uri="Callback / Redirect URI / URL here",
    scope=["tweet.read", "tweet.write", "tweet.delete", "like.read", "like.write", "like.delete"],
    # Client Secret is only necessary if using a confidential client
    client_secret = CLIENT_SECRET
)
response_url = oauth2_user_handler.get_authorization_url()
print(f"Please go to the following URL to authorize the application: {response_url}")
access_token = oauth2_user_handler.fetch_token(response_url)
client = tweepy.Client(access_token=access_token)

user_id = 'yinmou19'



# 获取自己的点赞推文
liked_tweets = client.get_liked_tweets(id=user_id)

# 输出点赞的推文内容
if liked_tweets.data:
    for tweet in liked_tweets.data:
        print(f"[{tweet.created_at}] {tweet.text}")
else:
    print("No liked tweets found.")

