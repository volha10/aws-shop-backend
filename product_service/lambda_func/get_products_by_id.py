import json
import logging
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb")

PRODUCTS_TABLE_NAME = os.getenv("PRODUCTS_TABLE_NAME")
STOCKS_TABLE_NAME = os.getenv("STOCKS_TABLE_NAME")

products_table = dynamodb.Table(PRODUCTS_TABLE_NAME)
stocks_table = dynamodb.Table(STOCKS_TABLE_NAME)


def lambda_handler(event, context):
    """
    AWS Lambda handler for fetching a product and its associated stock count.

    :param event: The event data passed to the Lambda.
    :param context: The context object for the Lambda function.

    :return: API Gateway response.
    """
    try:
        logger.info(f"CloudWatch logs group: {context.log_group_name}")
        logger.info(f"Request received: {event}")

        path_params = event.get("pathParameters", {})
        product_id = path_params.get("productId")

        if not product_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "productId is not provided."}),
            }

        product = get_product_with_stock(product_id)

        if not product:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": f"Product {product_id} not found"}),
            }

        return {"statusCode": 200, "body": json.dumps(product)}

    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "An unexpected error occurred."}),
        }


def get_product_with_stock(product_id):
    """
    Fetches a product and its associated stock count from DynamoDB.

    :param product_id: The ID of the product to retrieve.

    :return: Product details merged with stock count, or None if not found.
    """
    product_response = products_table.get_item(Key={"id": product_id})
    product = product_response.get("Item")

    if not product:
        return None

    stock_response = stocks_table.get_item(Key={"product_id": product_id})
    stock = stock_response.get("Item")

    # Add stock count to product (default to 0 if not found)
    product["count"] = int(stock["count"]) if stock else 0

    # Convert Decimal to int
    price = product["price"]
    product["price"] = int(price)

    return product
