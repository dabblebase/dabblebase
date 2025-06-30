"""
Service to handle authentication-related operations for projects.
"""

from ..base import BaseService
from sqlalchemy import select
from ...entities import ProjectEntity, UserEntity, UserAuthenticationProvider
from ..exceptions import ResourceNotFoundException
from . import auth_crypto as crypto
from ...env import env


class ProjectAuthService(BaseService):

    def get_or_create_user(
        self, auth_identifier: str, auth_provider: UserAuthenticationProvider
    ) -> UserEntity:
        """
        Retrieves a user based on their authentication identifier and provider, if it exists.
        If not, a new one is created.
        """
        # Retrieve the user
        query = (
            select(UserEntity)
            .where(UserEntity.auth_id == auth_identifier)
            .where(UserEntity.auth_provider == auth_provider)
        )
        user = self._admin_db.scalars(query).one_or_none()

        # If the user exists, return
        if user:
            return user

        # If not, create a new user using the auth credentials from the provider.
        new_user = UserEntity(
            auth_id=auth_identifier,
            auth_provider=auth_provider,
        )

        self._admin_db.add(new_user)
        self._admin_db.commit()

        return new_user

    def generate_token_for_project_auth_request(
        self, project_id: int, user_id: int
    ) -> str:
        """ """
        # Retrieve the project
        project = self._admin_db.get(ProjectEntity, project_id)
        if not project:
            raise ResourceNotFoundException(f"Project with ID {project_id} not found.")

        # Retrieve the project's encrypted private authentication key and decrypt it.
        # Recall the encryption key was derived from the master secret and project ID.
        encryption_key = crypto.hkdf_derive_encryption_key(
            env.AUTH_MASTER_SECRET, project_id
        )
        auth_private_key = crypto.decrypt(
            project.auth_encrypted_private_key, encryption_key
        )

        # Sign a new JWT token for the user with the project's private key. This token
        # can then be verified using the project's public key, which is distributed.
        payload = {"id": user_id}
        token = crypto.sign_jwt_with_asymmetric_keys(payload, auth_private_key)

        return token
