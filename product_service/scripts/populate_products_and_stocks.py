import boto3
import uuid
import random

from mock_products import PRODUCTS


# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb")

PRODUCTS_TABLE_NAME = "products"
STOCKS_TABLE_NAME = "stocks"


def delete_all_items(table_name, primary_key):
    """
    Deletes all items from a given DynamoDB table using batch_writer().
    :param table_name: The name of the table.
    :param primary_key: The primary key attribute of the table.
    """
    table = dynamodb.Table(table_name)

    # Scan the table to get all items
    response = table.scan()
    items = response.get("Items", [])

    with table.batch_writer() as batch:
        for item in items:
            print(item)
            key = {primary_key: item[primary_key]}

            batch.delete_item(Key=key)

    print(f"Deleted {len(items)} items from {table_name}.")


def delete_all_products():
    delete_all_items(PRODUCTS_TABLE_NAME, "id")


def delete_all_stocks():
    delete_all_items(STOCKS_TABLE_NAME, "product_id")


def populate_products():
    """
    Populates the 'products' table with sample product data.
    """
    table = dynamodb.Table(PRODUCTS_TABLE_NAME)

    with table.batch_writer() as batch:
        for product in PRODUCTS:
            item = {
                "id": product["id"],
                "title": product["title"],
                "description": product["description"],
                "price": product["price"],
            }

            batch.put_item(Item=item)

    print(f"Added {len(PRODUCTS)} products to {PRODUCTS_TABLE_NAME}.")


def populate_stocks():
    """
    Populates the 'stocks' table with stock counts for each product.
    """
    products_table = dynamodb.Table(PRODUCTS_TABLE_NAME)
    stocks_table = dynamodb.Table(STOCKS_TABLE_NAME)

    # Scan products to get product IDs
    response = products_table.scan()
    products = response.get("Items", [])

    with stocks_table.batch_writer() as batch:
        for product in products:
            stock_item = {"product_id": product["id"], "count": random.randint(0, 50)}

            batch.put_item(Item=stock_item)

    print(f"Added stock data for {len(products)} products to {STOCKS_TABLE_NAME}.")


if __name__ == "__main__":
    print("Deleting old data...")
    delete_all_products()
    # delete_all_stocks()

    print("\nPopulating new data...")
    populate_products()
    # populate_stocks()
