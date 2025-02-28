import json

from mock_products import PRODUCTS


def lambda_handler(event, context):
    print("Request received:", event)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(PRODUCTS),
    }
