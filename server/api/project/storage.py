"""Storage endpoints for projects."""

from botocore.client import ClientError
from fastapi import APIRouter, Cookie, Depends
from fastapi.exceptions import HTTPException
from server.storage import s3_client
from ..project import tag
from ...env import env
import anyio
from mypy_boto3_s3 import S3Client
from ...services.project import auth_crypto as crypto

api = APIRouter(prefix="/api/project/{project_id}/storage")


def authenticated_project_id(
    project_token: str = Cookie(
        default=None, alias="project-token", include_in_schema=False
    )
) -> str:
    try:
        payload = crypto.decode_jwt_with_symmetric_key(
            project_token, env.AUTH_MASTER_SECRET
        )
        return payload["project_id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")


@api.post("/{path}", tags=[tag])
async def create_presigned_upload(
    project_id: str,
    path: str,
    authed_project_id: str = Depends(authenticated_project_id),
    s3: S3Client = Depends(s3_client),
):
    """Generate a presigned PUT URL for uploading directly to MinIO."""
    if project_id != authed_project_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    bucket = project_id
    url = await anyio.to_thread.run_sync(
        lambda: s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket, "Key": path, "ContentType": "image/*"},
            ExpiresIn=3600,  # 1 hour
        )
    )
    return {"url": url, "method": "PUT", "headers": {"Content-Type": "image/*"}}


@api.get("/{path}", tags=[tag])
async def create_presigned_download(
    project_id: str,
    path: str,
    authed_project_id: str = Depends(authenticated_project_id),
    s3: S3Client = Depends(s3_client),
):
    """Generate a presigned GET URL to download the image."""
    if project_id != authed_project_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    bucket = project_id
    try:
        await anyio.to_thread.run_sync(lambda: s3.head_object(Bucket=bucket, Key=path))
    except ClientError:
        raise HTTPException(status_code=404, detail="Image not found")

    url = await anyio.to_thread.run_sync(
        lambda: s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": path},
            ExpiresIn=3600,
        )
    )
    return {"url": url, "method": "GET"}


@api.delete("/{path}", tags=[tag])
async def delete_image(
    project_id: str,
    path: str,
    authed_project_id: str = Depends(authenticated_project_id),
    s3: S3Client = Depends(s3_client),
):
    """Delete the image from MinIO."""
    if project_id != authed_project_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    bucket = project_id
    try:
        await anyio.to_thread.run_sync(
            lambda: s3.delete_object(Bucket=bucket, Key=path)
        )
        return {"ok": True, "deleted": path}
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))
