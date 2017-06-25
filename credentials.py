# Reads secret credentials from ./config.yml
# Initializes and returns auth: an instance of tweepy.OAuthHandler

import os
import yaml
from globals import CONFIG

import tweepy
from tweepy import OAuthHandler

__all__ = ['twitter_auth', 'aws_sns']

twitter_auth = OAuthHandler(CONFIG['twitter_consumer_key'], 
                            CONFIG['twitter_consumer_secret'])
twitter_auth.set_access_token(CONFIG['twitter_access_token'], 
                              CONFIG['twitter_access_secret'])

# api = tweepy.API(auth)

aws_sns = {'key': CONFIG['aws_tweetstream_key'],
           'secret': CONFIG['aws_tweetstream_secret']}
