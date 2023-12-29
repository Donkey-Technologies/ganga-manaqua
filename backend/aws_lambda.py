import json
import boto3
import time
import os

# Get the table name
table_name = os.environ.get('DDB_TABLE')

# Configure DynamoDB Connection
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        data = json.loads(event['body'])
        timestamp = data['timestamp']
        temperature = data['temperature']
        humidity = data['humidity']

        write_to_dynamodb(timestamp, temperature, humidity)

        return {
            'statusCode': 200,
            'body': json.dumps('Data correctly written in DynamoDB')
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error processing the request')
        }


def write_to_dynamodb(timestamp, temperature, humidity):
    try:
        response = table.put_item(
            Item={
                'Timestamp': timestamp,
                'Temperature': temperature,
                'Humidity': humidity
            }
        )
    except Exception as e:
        raise e
