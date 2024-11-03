import json
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('project2_UserProfiles')

def convert_decimal(obj):
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        # Convert Decimal to float or int
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj

def lambda_handler(event, context):
    # Get HTTP method
    http_method = event['httpMethod']
    
    # Get request path and query parameters
    path = event['path']
    query_params = event.get('queryStringParameters', {})
    
    # Route request based on path and method
    if path == "/user" and http_method == "GET":
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
        # Ensure the IndexName matches your table's GSI name
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
        r = table.get_item(Key={'userId': user_id})
        
        if 'Item' in r:
            item = convert_decimal(r['Item'])
            return response(200, item)
        else:
            return response(404, {"error": "User ID not found"})
    
    except ClientError as e:
        print(f"An error occurred: {e.r['Error']['Message']}")
        return {"error": str(e)}

def response(status_code, body):
    """Helper function to generate HTTP response."""
    return {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': {
            'Content-Type': 'application/json'
        }
    }
