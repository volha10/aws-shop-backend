import json
import os
import boto3
import logging
import urllib.parse
from botocore.exceptions import BotoCoreError, NoCredentialsError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


def lambda_handler(event: dict, _) -> dict:
    """
    AWS Lambda handler for generating a pre-signed S3 upload URL.
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        file_name = validate_request(event)
        signed_url = generate_signed_url(file_name)
        return {"statusCode": 200, "body": json.dumps({"url": signed_url})}
    except Exception as e:
        return handle_exception(e)


def validate_request(event: dict) -> str:
    """
    Validate request parameters and extract the file name.
    """
    query_params = event.get("queryStringParameters", {})
    file_name = query_params.get("name")

    if not file_name:
        raise ValueError("Missing 'name' query parameter")

    file_name = urllib.parse.unquote(file_name)  # Decode URL-encoded file names

    if not file_name.endswith(".csv"):
        raise ValueError("Only CSV files are allowed")

    return file_name


def generate_signed_url(file_name: str) -> str:
    """
    Generate a pre-signed URL for uploading a file to S3.
    """
    try:
        s3_key = f"uploaded/{file_name}"
        logger.info(
            f"Generating signed URL for {s3_key} in bucket {BUCKET_NAME}...")

        signed_url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": BUCKET_NAME, "Key": s3_key, "ContentType": "text/csv"},
            ExpiresIn=300,  # URL valid for 5 minutes
        )
        logger.info("Signed URL successfully generated.")

        return signed_url
    except (BotoCoreError, NoCredentialsError) as e:
        logger.error(f"Failed to generate signed URL: {str(e)}", exc_info=True)
        raise RuntimeError(f"Failed to generate signed URL: {str(e)}")


def handle_exception(e: Exception) -> dict:
    """
    Centralized exception handler.
    """
    if isinstance(e, ValueError):
        logger.error(f"Client error: {str(e)}")
        return {"statusCode": 400, "body": json.dumps({"message": str(e)})}
    elif isinstance(e, RuntimeError):
        logger.error(f"Server error: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": json.dumps({"message": str(e)})}

    logger.critical("Unexpected error", exc_info=True)
    return {"statusCode": 500, "body": json.dumps({"message": "Internal Server Error"})}
