"""Contains injectible S3 instance to connect to object storage."""

import sqlalchemy
from sqlalchemy.orm import Session
from .env import env, in_production
from celery import Celery
import boto3
from botocore.config import Config


def s3_client():
    # Force path-style addressing for MinIO (avoids DNS bucket issues)
    cfg = Config(
        s3={"addressing_style": "path"},
        signature_version="s3v4",
        retries={"max_attempts": 1},  # Reduce retries for faster debugging
    )

    # Handle docker networking - try minio service name if localhost fails
    endpoint_url = env.S3_ENDPOINT

    # If we're running in a container and using localhost, try the service name instead
    if "localhost" in endpoint_url:
        import socket

        try:
            # Test if we can resolve the minio service name
            socket.gethostbyname("minio")
            endpoint_url = endpoint_url.replace("localhost", "minio")
            print(f"Using docker service name for S3: {endpoint_url}")
        except socket.gaierror:
            # minio service name not resolvable, stick with localhost
            print(f"Using localhost for S3: {endpoint_url}")

    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        region_name=env.S3_REGION,
        aws_access_key_id=env.S3_ACCESS_KEY,
        aws_secret_access_key=env.S3_SECRET_KEY,
        config=cfg,
        use_ssl=False,  # Since we're using http://localhost:9000
    )
