import json
import boto3
from botocore.exceptions import ClientError

#
# Nuevo Comentario6
#

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UserProfiles')

def lambda_handler(event, context):
    # Get HTTP method
    http_method = event['httpMethod']
    
    # Get request path and query parameters
    path = event['path']
    query_params = event.get('queryStringParameters', {})
    
    # Route request based on path and method
    if path == "/user/profile" and http_method == "GET":
        if 'username' in query_params:
            return get_user_profile_by_username(query_params['username'])
        elif 'userId' in query_params:
            return get_username_by_userid(query_params['userId'])
        else:
            return response(400, {"error": "Missing required parameters"})
    else:
        return response(404, {"error": "Route not found"})


def get_user_profile_by_username(username):
    try:
        # Query the table using the Global Secondary Index (GSI) by username
        result = table.query(
            IndexName='username-index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('username').eq(username)
        )
        if 'Items' in result and result['Items']:
            return response(200, result['Items'][0])
        else:
            return response(404, {"error": "User profile not found"})
    except ClientError as e:
        return response(500, {"error": str(e)})


def get_username_by_userid(user_id):
    try:
        # Query the table using the Primary Key (userId)
        result = table.get_item(Key={'userId': user_id})
        
        if 'Item' in result:
            return response(200, {"username": result['Item']['username']})
        else:
            return response(404, {"error": "User ID not found"})
    except ClientError as e:
        return response(500, {"error": str(e)})


def response(status_code, body):
    """Helper function to generate HTTP response."""
    return {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': {
            'Content-Type': 'application/json'
        }
    }
