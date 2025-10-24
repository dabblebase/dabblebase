"""Storage endpoints for projects."""

from botocore.client import ClientError
from fastapi import APIRouter, Cookie, Depends, Header, Request, UploadFile
from fastapi.exceptions import HTTPException
from server.storage import s3_client
from ..project import tag
from ...env import env
import anyio
from mypy_boto3_s3 import S3Client
from ...services.project import auth_crypto as crypto
from sqlalchemy.orm import Session
from ...database import admin_db_session
from sqlalchemy import select
from ...entities.project import ProjectEntity

api = APIRouter(prefix="/api/project/{project_id}/storage")


def authenticated_project_token(
    x_project_token: str = Header(default=None, alias="X-Project-Token")
) -> str:
    if not x_project_token:
        raise HTTPException(
            status_code=401, detail="X-Project-Token header is required"
        )
    return x_project_token


def _authenticated_project_id(
    project_token: str, project_id: int, admin_db: Session
) -> int:
    # Fetch the project to get the project's encrypted signing key
    try:
        project = (
            admin_db.query(ProjectEntity).where(ProjectEntity.id == project_id).one()
        )
        encryption_key = crypto.hkdf_derive_encryption_key(
            env.AUTH_MASTER_SECRET, project_id
        )
        project_signing_key = crypto.decrypt(
            project.project_encrypted_signing_key, encryption_key
        )
        payload = crypto.decode_jwt_with_symmetric_key(
            project_token, project_signing_key
        )
        return int(payload["project_id"])
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized: {e}")


@api.post("/upload", tags=[tag])
async def create_presigned_upload(
    project_id: int,
    path: str,
    authed_project_token: str = Depends(authenticated_project_token),
    admin_db: Session = Depends(admin_db_session),
    s3: S3Client = Depends(s3_client),
):
    """Generate a presigned PUT URL for uploading directly to MinIO."""
    authed_project_id = _authenticated_project_id(
        authed_project_token, project_id, admin_db
    )
    if project_id is not authed_project_id:
        raise HTTPException(
            status_code=401,
            detail=f"Unauthorized.",
        )

    url = await anyio.to_thread.run_sync(
        lambda: s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": "dabblebase-bucket", "Key": f"{project_id}/{path}"},
            ExpiresIn=3600,  # 1 hour
        )
    )

    # Replace minio hostname with localhost for browser access
    if "minio:9000" in url:
        url = url.replace("minio:9000", "localhost:9000")
        print(f"Converted upload URL for browser access: {url}")

    return {"url": url, "method": "PUT"}


@api.post("/upload-direct", tags=[tag])
async def upload_direct(
    project_id: int,
    path: str,
    file: UploadFile,
    authed_project_token: str = Depends(authenticated_project_token),
    admin_db: Session = Depends(admin_db_session),
    s3: S3Client = Depends(s3_client),
):
    """Upload file directly through the API to avoid CORS issues."""
    authed_project_id = _authenticated_project_id(
        authed_project_token, project_id, admin_db
    )
    if project_id != authed_project_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Create bucket if it doesn't exist
    try:
        await anyio.to_thread.run_sync(
            lambda: s3.head_bucket(Bucket="dabblebase-bucket")
        )
    except ClientError:
        try:
            await anyio.to_thread.run_sync(
                lambda: s3.create_bucket(Bucket="dabblebase-bucket")
            )
        except Exception:
            pass  # Bucket might already exist

    key = f"{project_id}/{path}"
    print(f"Uploading file to bucket: dabblebase-bucket, key: {key}")

    try:
        # Read file content
        file_content = await file.read()

        # Upload to S3
        await anyio.to_thread.run_sync(
            lambda: s3.put_object(
                Bucket="dabblebase-bucket",
                Key=key,
                Body=file_content,
                ContentType=file.content_type or "application/octet-stream",
            )
        )

        print(f"Successfully uploaded file: {key}")

        # Generate a view URL for the uploaded file
        view_url = f"/api/project/{project_id}/storage/view/{path}"

        return {"success": True, "key": key, "url": view_url}

    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@api.get("/download", tags=[tag])
async def create_presigned_download(
    project_id: int,
    path: str,
    authed_project_token: str = Depends(authenticated_project_token),
    admin_db: Session = Depends(admin_db_session),
    s3: S3Client = Depends(s3_client),
):
    """Generate a presigned GET URL to download the image."""
    authed_project_id = _authenticated_project_id(
        authed_project_token, project_id, admin_db
    )
    if project_id != authed_project_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    key = f"{project_id}/{path}"
    print(f"Attempting to download from bucket: dabblebase-bucket, key: {key}")

    try:
        result = await anyio.to_thread.run_sync(
            lambda: s3.head_object(Bucket="dabblebase-bucket", Key=key)
        )
        print(f"Object found: {result}")
    except ClientError as e:
        print(f"ClientError: {e}")
        error_code = e.response["Error"]["Code"]
        if error_code == "NoSuchKey":
            raise HTTPException(
                status_code=404, detail=f"Image not found at key: {key}"
            )
        elif error_code == "NoSuchBucket":
            raise HTTPException(
                status_code=404, detail="Bucket 'dabblebase-bucket' not found"
            )
        else:
            raise HTTPException(status_code=500, detail=f"S3 error: {error_code}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    url = await anyio.to_thread.run_sync(
        lambda: s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": "dabblebase-bucket", "Key": f"{project_id}/{path}"},
            ExpiresIn=3600,
        )
    )

    # Replace minio hostname with localhost for browser access
    if "minio:9000" in url:
        url = url.replace("minio:9000", "localhost:9000")
        print(f"Converted URL for browser access: {url}")

    return {"url": url, "method": "GET"}


@api.get("/view/{path:path}", tags=[tag])
async def view_image(
    project_id: int,
    path: str,
    request: Request,
    x_project_token: str = Header(default=None, alias="X-Project-Token"),
    admin_db: Session = Depends(admin_db_session),
    s3: S3Client = Depends(s3_client),
):
    """Proxy image content through the API to avoid CORS issues."""
    from fastapi.responses import StreamingResponse
    import io

    # Try to get token from header first, then from query parameter
    token = x_project_token
    if not token:
        token = request.query_params.get("X-Project-Token")

    if not token:
        raise HTTPException(status_code=401, detail="X-Project-Token is required")

    authed_project_id = _authenticated_project_id(token, project_id, admin_db)
    if project_id != authed_project_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    key = f"{project_id}/{path}"
    print(f"Proxying image from bucket: dabblebase-bucket, key: {key}")

    try:
        # Get the object from S3
        response = await anyio.to_thread.run_sync(
            lambda: s3.get_object(Bucket="dabblebase-bucket", Key=key)
        )

        # Get content type from S3 metadata
        content_type = response.get("ContentType", "application/octet-stream")

        # Stream the content
        content = response["Body"].read()

        return StreamingResponse(
            io.BytesIO(content),
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=3600",
                "Content-Length": str(len(content)),
            },
        )

    except ClientError as e:
        print(f"ClientError while proxying: {e}")
        error_code = e.response["Error"]["Code"]
        if error_code == "NoSuchKey":
            raise HTTPException(
                status_code=404, detail=f"Image not found at key: {key}"
            )
        else:
            raise HTTPException(status_code=500, detail=f"S3 error: {error_code}")
    except Exception as e:
        print(f"Unexpected error while proxying: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@api.get("/list", tags=[tag])
async def list_project_files(
    project_id: int,
    authed_project_token: str = Depends(authenticated_project_token),
    admin_db: Session = Depends(admin_db_session),
    s3: S3Client = Depends(s3_client),
):
    """List all files in the project's storage."""
    authed_project_id = _authenticated_project_id(
        authed_project_token, project_id, admin_db
    )
    if project_id != authed_project_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        prefix = f"{project_id}/"
        print(f"Listing objects with prefix: {prefix}")

        result = await anyio.to_thread.run_sync(
            lambda: s3.list_objects_v2(Bucket="dabblebase-bucket", Prefix=prefix)
        )

        files = []
        if "Contents" in result:
            for obj in result["Contents"]:
                # Remove the project_id/ prefix to get the relative path
                relative_key = obj["Key"][len(prefix) :]
                files.append(
                    {
                        "key": obj["Key"],
                        "path": relative_key,
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"].isoformat(),
                    }
                )

        return {"files": files, "total": len(files)}
    except ClientError as e:
        print(f"List files error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@api.delete("/delete", tags=[tag])
async def delete_image(
    project_id: int,
    path: str,
    authed_project_token: str = Depends(authenticated_project_token),
    admin_db: Session = Depends(admin_db_session),
    s3: S3Client = Depends(s3_client),
):
    """Delete the image from MinIO."""
    authed_project_id = _authenticated_project_id(
        authed_project_token, project_id, admin_db
    )
    if project_id != authed_project_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        await anyio.to_thread.run_sync(
            lambda: s3.delete_object(
                Bucket="dabblebase-bucket", Key=f"{project_id}/{path}"
            )
        )
        return {"ok": True, "deleted": path}
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))
