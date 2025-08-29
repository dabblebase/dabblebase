"""API endpoint for admin functionality"""

from fastapi import APIRouter, Depends

from server.api.auth import registered_user
from server.models.admin import ListUsersResponse
from server.models.auth import Subject
from server.services.admin import AdminService


tag = "Admin"
openapi_tags = {
    "name": tag,
    "description": "API endpoint for admin functions.",
}

api = APIRouter(prefix="/api/admin")


@api.get("/", tags=[tag])
def is_admin(
    subject: Subject = Depends(registered_user), admin_svc: AdminService = Depends()
) -> bool:
    return admin_svc.is_admin(subject)


@api.get("/users", tags=[tag])
def list_users(
    subject: Subject = Depends(registered_user), admin_svc: AdminService = Depends()
) -> ListUsersResponse:
    return admin_svc.list_users(subject)


@api.put("/instructor/add", tags=[tag])
def add_instructor(
    new_instructor: Subject,
    subject: Subject = Depends(registered_user),
    admin_svc: AdminService = Depends(),
) -> None:
    return admin_svc.add_instructor(subject, new_instructor)


@api.put("/instructor/remove", tags=[tag])
def remove_instructor(
    instructor: Subject,
    subject: Subject = Depends(registered_user),
    admin_svc: AdminService = Depends(),
) -> None:
    return admin_svc.remove_instructor(subject, instructor)
