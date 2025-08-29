"""Service defining functionality for the admin user"""

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from server.database import admin_db_session
from server.entities.user import UserEntity
from server.services.exceptions import (
    ResourceAlreadyExistsException,
    ResourceNotFoundException,
)
from ..models.admin import ListUsersResponse, ListUsersResponse_User
from ..models.auth import Subject
from ..services.base import BaseService
from ..services.permission import PermissionService


class AdminService:
    """Service defining admin functionality"""

    def __init__(
        self,
        permission_svc: PermissionService = Depends(),
        admin_db: Session = Depends(admin_db_session),
    ):
        self._admin_db = admin_db
        self._permission_svc = permission_svc

    def is_admin(self, subject: Subject) -> bool:
        """Checks if the current user is an admin user"""
        return self._permission_svc.check_admin_permissions(subject)

    def list_users(self, subject: Subject) -> ListUsersResponse:
        """Lists all of the registered Dabblebase users
        TODO: Consider making this request server-side paginated.
        """
        # Verify admin permissions
        self._permission_svc.enforce_admin_permissions(subject)
        # List all users
        users_query = select(UserEntity).order_by(UserEntity.last_name)
        users = self._admin_db.scalars(users_query).all()
        # Convert data to correct shape
        user_models = [
            ListUsersResponse_User(
                id=user.id,
                name=f"{user.first_name} {user.last_name}",
                email=user.email,
                is_instructor=user.is_instructor,
            )
            for user in users
        ]
        return ListUsersResponse(users=user_models)

    def add_instructor(self, subject: Subject, new_instructor: Subject):
        """Elevates a user to instructor status"""
        # Verify admin permissions
        self._permission_svc.enforce_admin_permissions(subject)
        # Make sure that the user exists
        user = self._admin_db.get(UserEntity, new_instructor.id)
        if not user:
            raise ResourceNotFoundException(
                f"No user found with id: {new_instructor.id}"
            )
        if user.is_instructor:
            raise ResourceAlreadyExistsException(f"User is already an instructor!")
        # Change the instructor flag
        user.is_instructor = True
        self._admin_db.commit()

    def remove_instructor(self, subject: Subject, instructor: Subject):
        """Removes instructor permissions from a user"""
        # Verify admin permissions
        self._permission_svc.enforce_admin_permissions(subject)
        # Make sure that the user exists
        user = self._admin_db.get(UserEntity, instructor.id)
        if not user:
            raise ResourceNotFoundException(f"No user found with id: {instructor.id}")
        if not user.is_instructor:
            raise ResourceAlreadyExistsException(f"User is already not an instructor!")
        # Change the instructor flag
        user.is_instructor = False
        self._admin_db.commit()
