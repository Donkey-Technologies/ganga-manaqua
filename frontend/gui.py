import boto3
import os
from os.path import dirname, abspath


def get_table_name():
    ddb_table_path = os.path.join(dirname(abspath(__file__)), "ddb_table.txt")
    try:
        with open(ddb_table_path, "r") as f:
            for line in f:
                if ":" in line:
                    _, table_name = line.strip().split(":", 1)
        return table_name

    except OSError:
        print("Unable get the table name")
        return ""


def get_dynamodb_data():
    # Get the table name
    table_name = get_table_name()

    # Configure DynamoDB Connection
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    respuesta = table.scan()

    return respuesta["Items"]
