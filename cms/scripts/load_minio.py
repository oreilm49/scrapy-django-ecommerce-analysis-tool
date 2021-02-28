import boto3

from cms.settings import AWS_S3_ENDPOINT_URL


def run():
    boto3.client('s3', endpoint_url=AWS_S3_ENDPOINT_URL).create_bucket(Bucket="product-images")
