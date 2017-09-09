#!/usr/bin/env python3
import os
import sys
import json
import yaml
import tweepy
import boto3
import numbers
import decimal

import globals

if len(sys.argv) > 1:
    MAX_TWEETS = int(sys.argv[1])
else:
    MAX_TWEETS=10000

#No longer used, replaced by PROFILE
#TAG_CATEGORY = 'minicooper'
#TAG_CATEGORY = 'politics'
#TAG_CATEGORY = 'combo'

from globals import PROFILE, CONFIG

from credentials import twitter_auth, aws_sns, aws_sqs

CAPACITY = {'ReadCapacityUnits':5, 'WriteCapacityUnits':5}
TABLE = 'tweetstream'

SNS = boto3.client('sns', 'us-east-1',
                   aws_access_key_id=aws_sns['key'],
                   aws_secret_access_key=aws_sns['secret'])
SNS_ARN = CONFIG['topic_arn']

SQS = boto3.client('sqs', 'us-east-1',
                   aws_access_key_id=aws_sqs['key'],
                   aws_secret_access_key=aws_sqs['secret'])
SQS_URL = CONFIG['queue_url']
print( "Queue URL is %s"%SQS_URL)
TAGS_FILENAME = 'tags.yml'

class StopListening (Exception):
    pass

# Helper class to convert floats, which JSON doesn't support
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

class TwListener(tweepy.streaming.StreamListener):
    count = 0

    def on_data(self, data_str):
        try:
            data_dict = json.loads(data_str)
            print('-', self.count, data_dict['id_str'], data_dict['text'][:70])
            if data_dict['lang'] != 'en':
                print('-', self.count, 'Skipping tweet with lang=', data_dict['lang'])
                return True
            self.count += 1
            data_dict['venue']='TWITTER'
            data_dict['profile']=PROFILE
            self.send_item(data_dict)
            if MAX_TWEETS > 0 and self.count > MAX_TWEETS:
                raise StopListening('Time to stop')
        except StopListening:
            raise
        except BaseException as e:
            print('Error on_data: %s' % str(e))

        return True

    def on_error(self, status):
        print(status)
        return True

    def send_item(self, item):

        try:
            item_str = json.dumps(clean_data(item), cls=DecimalEncoder)
        except BaseException as e:
            print('Error on_json: %s' % str(e))

        try:
            SQS.send_message(QueueUrl=SQS_URL,
                             MessageBody=item_str)
        except StopListening:
            raise
        except BaseException as e:
            print('Error on_post: %s' % str(e))

        return True
    
def load_tags():
    filename = os.path.join(os.path.dirname(__file__), TAGS_FILENAME)
    tags = yaml.load(open(filename))
    return tags[PROFILE]

def clean_data(struct):
    '''
    Removes any values which are None or empty_string
    '''
    if False and isinstance(struct, numbers.Number):
        val = decimal.Decimal(str(struct))
        print('  -- convert', struct, struct.__class__, val, val.__class__)
        return val
    if isinstance(struct, list):
        return [clean_data(v) for v in struct]
    if isinstance(struct, dict):
        return dict((k, clean_data(v)) for (k, v) in struct.items() if v != None and v != '')
    return struct

def main():
    try:
        tags = load_tags()
        twitter_stream = tweepy.Stream(twitter_auth, TwListener())
        twitter_stream.filter(track=tags)
    except StopListening:
        return

if __name__ == '__main__':
    main()
