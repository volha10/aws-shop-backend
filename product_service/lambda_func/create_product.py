import json
import logging
import boto3
import os
import uuid
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb")

PRODUCTS_TABLE_NAME = os.getenv("PRODUCTS_TABLE_NAME")
STOCKS_TABLE_NAME = os.getenv("STOCKS_TABLE_NAME")

# Reference the DynamoDB table
# products_table = dynamodb.Table(PRODUCTS_TABLE_NAME)


def lambda_handler(event, _):
    """
    AWS Lambda handler for creating a new product.

    :param event: The event data from API Gateway.
    :param _: The Lambda execution context.

    :return: API Gateway response.
    """
    try:
        logger.info(f"Event received: {event}")

        body = json.loads(event.get("body", "{}"))

        # Create a new product
        product = create_product(body)

        return {
            "statusCode": 201,
            "body": json.dumps(product)
        }

    except ValueError as error:
        logger.error(f"Validation error: {error}")
        return {
            "statusCode": 400,
            "body": json.dumps({"message": str(error)})
        }

    except ClientError as error:
        logger.error(f"DynamoDB transaction error: {error}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error"})
        }

    except Exception as error:
        logger.exception(f"Unexpected error: {error}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "An unexpected error occurred."})
        }


def create_product(data: dict) -> dict:
    """
    Inserts a new product into the DynamoDB Products table.

    :param data: Dictionary containing 'title', 'description', 'price'.

    :return: The created product item.
    """
    if "title" not in data or "price" not in data:
        raise ValueError("Missing required fields: 'title' and 'price'.")

    product_id = str(uuid.uuid4())

    new_product = {
        "id": product_id,
        "title": data["title"],
        "description": data.get("description", ""),  # Default to empty string
        "price": data["price"],  # Ensure price is an integer
    }

    new_stock = {
        "product_id": product_id,
        "count": data["count"],
    }

    save_product_and_stock(new_product, new_stock)

    new_product["count"] = data["count"]
    return new_product


def save_product_and_stock(product: dict[str, int], stock: dict[str, int]) -> None:
    """
    Saves the product and stock data in a DynamoDB transaction.

    :param product: Product item to be saved.
    :param stock: Stock item to be saved.

    :raises ClientError: If DynamoDB transaction fails.
    """
    dynamodb.meta.client.transact_write_items(
            TransactItems=[
                {"Put": {"TableName": PRODUCTS_TABLE_NAME, "Item": product}},
                {"Put": {"TableName": STOCKS_TABLE_NAME, "Item": stock}},
            ]
        )
