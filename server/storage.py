"""Contains injectible S3 instance to connect to object storage."""

import sqlalchemy
from sqlalchemy.orm import Session
from .env import env, in_production
from celery import Celery
import boto3
from botocore.config import Config


def s3_client():
    # Force path-style addressing for MinIO (avoids DNS bucket issues)
    cfg = Config(s3={"addressing_style": "path"}, signature_version="s3v4")
    return boto3.client(
        "s3",
        endpoint_url=env.S3_ENDPOINT,
        region_name=env.S3_REGION,
        aws_access_key_id=env.S3_ACCESS_KEY,
        aws_secret_access_key=env.S3_SECRET_KEY,
        config=cfg,
    )
