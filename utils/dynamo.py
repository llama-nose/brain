import boto3
from boto3.dynamodb.conditions import Key    

def query_table(session_id):
    # Create DynamoDB resource
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('response')

    # Query the table
    response = table.query(
        IndexName='session_id-index',
        KeyConditionExpression=Key('session_id').eq(session_id)
    )
    
    return response['Items']