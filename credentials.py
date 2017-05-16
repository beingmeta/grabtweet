# Reads secret credentials from ./config.yml
# Initializes and returns auth: an instance of tweepy.OAuthHandler

import os
import yaml

import tweepy
from tweepy import OAuthHandler

__all__ = ['twitter_auth', 'aws_tweetstream']

FILE = os.path.join(os.path.dirname(__file__), 'config.yml')
CREDENTIALS = yaml.load(open(FILE))

twitter_auth = OAuthHandler(CREDENTIALS['twitter_consumer_key'], CREDENTIALS['twitter_consumer_secret'])
twitter_auth.set_access_token(CREDENTIALS['twitter_access_token'], CREDENTIALS['twitter_access_secret'])

# api = tweepy.API(auth)

aws_tweetstream = {'key': CREDENTIALS['aws_tweetstream_key'],
                   'secret': CREDENTIALS['aws_tweetstream_secret']}
