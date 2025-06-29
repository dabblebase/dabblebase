"""Production systems monitor these end points upon deployment, and at regular intervals, to ensure the service is running"""

from fastapi import APIRouter

tag = "System Health"
openapi_tags = {
    "name": tag,
    "description": "Production systems monitor these end points upon deployment, and at regular intervals, to ensure the service is running.",
}

api = APIRouter(prefix="/api/health")


@api.get("", tags=[tag])
def health_check() -> str:
    return "OK"
