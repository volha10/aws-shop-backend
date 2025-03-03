import json
import logging
import os

import boto3

dynamodb = boto3.resource("dynamodb")

PRODUCTS_TABLE_NAME = os.getenv("PRODUCTS_TABLE_NAME")
STOCKS_TABLE_NAME = os.getenv("STOCKS_TABLE_NAME")


def lambda_handler(event, _):
    """
    AWS Lambda handler for fetching all products and joins them with stock count.

    :param event: The event data passed to the Lambda.
    :param _: The context object for the Lambda function.

    :return: API Gateway response.
    """

    try:
        print("Request received:", event)

        products_and_stocks = get_products_and_stocks()

        return {
            "statusCode": 200,
            "body": json.dumps(products_and_stocks),
            "headers": {
                "Content-Type": "application/json",
            },
        }
    except Exception as e:
        logging.exception(f"Error: {str(e)}")

        return {
            "statusCode": 500,
            "body": json.dumps({"message": "An unexpected error occurred."}),
            "headers": {
                "Content-Type": "application/json",
            },
        }


def get_products_and_stocks():
    """
    Fetches products and their associated stock data by product_id.
    """
    # Initialize DynamoDB tables
    products_table = dynamodb.Table(PRODUCTS_TABLE_NAME)
    stocks_table = dynamodb.Table(STOCKS_TABLE_NAME)

    # Scan products table
    response = products_table.scan()
    products = response.get("Items", [])

    # Scan stocks table
    response = stocks_table.scan()
    stocks = response.get("Items", [])

    stock_map = {stock["product_id"]: stock["count"] for stock in stocks}

    for product in products:
        product["count"] = int(
            stock_map.get(product["id"], 0)
        )  # Default to 0 if no stock entry
        price = product["price"]
        product["price"] = int(price)

    return products
