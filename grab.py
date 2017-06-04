#!/usr/bin/env python3
import os
import json
import yaml
import tweepy
import boto3
import numbers
import decimal

from credentials import twitter_auth, aws_tweetstream


MAX_TWEETS = 5
CAPACITY = {'ReadCapacityUnits':5, 'WriteCapacityUnits':5}
TABLE = 'tweetstream'
SNS_ARN = 'arn:aws:sns:us-east-1:206027209718:tweetstream'
#SNS_ARN = 'arn:aws:sns:us-east-1:206027209718:tweetstream-capture'

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
        dynamodb_client = boto3.client('dynamodb')
        set_capacity(dynamodb_client, TABLE, **CAPACITY)
        tags = load_tags()
        twitter_stream = tweepy.Stream(twitter_auth, TwListener())
        twitter_stream.filter(track=tags)
    except StopListening:
        return

def read_capacity(client, table):
    '''
    returns current read and write capacity for dynamodb table(:string)
    '''
    response = client.describe_table(TableName=table)
    props = response['Table']['ProvisionedThroughput']
    return dict((k, props[k]) for k in ['ReadCapacityUnits', 'WriteCapacityUnits'])


def set_capacity(client, table, ReadCapacityUnits=5, WriteCapacityUnits=5):
    '''
    updates current read and write capacity for dynamodb table
    '''
    current = read_capacity(client, table)
    newval = {}
    if current['ReadCapacityUnits'] != ReadCapacityUnits:
        newval['ReadCapacityUnits'] = ReadCapacityUnits
    if current['WriteCapacityUnits'] != WriteCapacityUnits:
        newval['WriteCapacityUnits'] = WriteCapacityUnits
    if newval == {}:
        print('No updates needed. Current value: {}'.format(current))
        return
    print('Updates needed.\n Current value: {},\n new value: {}'.format(current, newval))
    client.update_table(TableName=table, ProvisionedThroughput=newval)

if __name__ == '__main__':
    main()
