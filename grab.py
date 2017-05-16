#!/usr/bin/env python3
import os
import json
import yaml
import tweepy
import boto3
import numbers
import decimal

from credentials import twitter_auth, aws_tweetstream


MAX_TWEETS = 5000

SNS_ARN = 'arn:aws:sns:us-east-1:206027209718:tweetstream-capture'

SNS = boto3.client('sns', 'us-east-1',
                   aws_access_key_id=aws_tweetstream['key'],
                   aws_secret_access_key=aws_tweetstream['secret'])

TAGS_FILENAME = 'tags.yml'
TAG_CATEGORY = 'minicooper'

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
            print('-', self.count, data_dict['id_str'], data_dict['text'][:40])
            self.count += 1
            self.send_item(data_dict)
            if self.count > MAX_TWEETS:
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
        item_str = json.dumps(clean_data(item), cls=DecimalEncoder)
        SNS.publish(TargetArn=SNS_ARN,
                    Message=json.dumps({'default': item_str}, cls=DecimalEncoder),
                    MessageStructure='json')
    
def load_tags():
    filename = os.path.join(os.path.dirname(__file__), TAGS_FILENAME)
    tags = yaml.load(open(filename))
    return tags[TAG_CATEGORY]

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

