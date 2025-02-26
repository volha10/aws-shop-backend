import json
import logging
from mock_products import PRODUCTS

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(f"CloudWatch logs group: {context.log_group_name}")
    logger.info(f"event={event}")

    # product_id = event["pathParameters"]

    path_params = event.get("pathParameters")
    product_id = path_params.get("productId")

    print(f"product_id={product_id}")

    if not product_id:
        raise Exception(f"Product id is not provided.")

    product = next((p for p in PRODUCTS if p["id"] == product_id), None)

    if product:
        return {
            "statusCode": 200,
            "body": json.dumps(product)
        }

    print(f"product={product}")

    return {
        "statusCode": 404,
        "body": json.dumps({"message": f"Product {product_id} not found"})
    }
