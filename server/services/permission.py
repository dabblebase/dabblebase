"""
Permission Service grants, revokes, tests, and enforces permissions for users and roles in the system.
"""

import re
from fastapi import Depends
from functools import lru_cache
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..entities import PermissionEntity
from ..services.exceptions import ResourceNotFoundException, UserPermissionException
from ..database import admin_db_session
from ..entities.user import Subject, UserEntity


class PermissionService:
    """PermissionService grants, revokes, tests, and enforces permissions for users and roles in the system."""

    _session: Session

    def __init__(self, session: Session = Depends(admin_db_session)):
        self._session = session

    def grant_superuser_permission(self, grantee: Subject) -> bool:
        """Grants the superuser permission to the grantee.
        NOTE: This function does not check for permissions itself and should only be used
        via a script in production or development.
        """
        # Ensure that the user exists
        user = self._session.get(UserEntity, grantee.id)
        if not user:
            raise ResourceNotFoundException(
                f"User with if {grantee.id} does not exist!"
            )

        # Grant permission
        permission = PermissionEntity(action="*", resource="*", user_id=grantee.id)
        self._session.add(permission)
        self._session.commit()

    def enforce_admin_permissions(self, subject: Subject):
        """Raises an exception if a user does not have admin permissions."""
        self.enforce_permission(subject, "*", "*")

    def enforce_permission(self, subject: Subject, action: str, resource: str):
        """Raises an exception if a user does not have permission."""
        if not self.check_permission(subject, action, resource):
            raise UserPermissionException(
                f"User {subject.id} cannot perform {action} on {resource}"
            )

    def check_permission(self, subject: Subject, action: str, resource: str):
        """Checks if a user has a permission"""
        # Load the user's permissions
        query = select(PermissionEntity).where(PermissionEntity.user_id == subject.id)
        permissions = self._session.scalars(query).all()
        # Check if any of these permissions grant the action and resource.
        for permission in permissions:
            if self._check_permission(permission, action, resource):
                return True
        return False

    def _check_permission(
        self, permission: PermissionEntity, action: str, resource: str
    ) -> bool:
        """Check if a user has permission to carry out an action on a resource."""
        action_re = self._expand_pattern(permission.action)
        if action_re.fullmatch(action) is not None:
            resource_re = self._expand_pattern(permission.resource)
            return resource_re.fullmatch(resource) is not None
        else:
            return False

    @lru_cache()
    def _expand_pattern(self, pattern: str) -> re.Pattern:
        """Expand a permission pattern into a regular expression.

        This function is memoized to avoid recompiling the same regular expression multiple times.

        Args:
            pattern (str): The pattern to expand.

        Returns:
            re.Pattern: The compiled regular expression."""
        search = pattern.replace("*", ".*")
        return re.compile(f"^{search}$")
