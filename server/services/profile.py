"""Service used to interface with profiles"""

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import admin_db_session
from ..models.auth import Subject
from ..models.profile import GetProfileSummaryResponse
from ..entities import UserEntity
from .exceptions import ResourceNotFoundException


class ProfileService:

    _admin_db: Session

    def __init__(
        self,
        admin_db: Session = Depends(admin_db_session),
    ):
        self._admin_db = admin_db

    def get_profile_summary(
        self, subject: Subject | None
    ) -> GetProfileSummaryResponse | None:
        """Get the profile for the given subject."""
        if not subject:
            return None
        user = self._admin_db.get(UserEntity, subject.id)
        if not user:
            raise ResourceNotFoundException(f"User with id {subject.id} not found.")

        initials = (
            user.first_name[0].upper() + user.last_name[0].upper()
            if user.first_name and user.last_name
            else ""
        )
        return GetProfileSummaryResponse(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            initials=initials,
        )
