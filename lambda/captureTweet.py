import boto3
import json
import numbers
import decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('tweetstream')
    
def lambda_handler(event, context):
    msg_str = event['Records'][0]['Sns']['Message']
    msg = clean_data(json.loads(msg_str, parse_float=decimal.Decimal))
    print("trying", msg['id_str'])
    response = table.put_item(Item=msg)
    print("PutItem succeeded:", msg['id_str'])

def clean_data(struct):
    '''                                                                                                                 Removes any values which are None or empty_string. Replace floats with Decimal                                      '''
    if isinstance(struct, list):
        return [clean_data(v) for v in struct]
    if isinstance(struct, dict):
        return dict([(k, clean_data(v)) for (k, v) in struct.items() if v != None and v != ''])
    return struct
