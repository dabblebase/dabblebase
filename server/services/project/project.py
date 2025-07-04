"""
Service to handle CRUD operations on projects.
"""

from sqlalchemy import text
from ..base import BaseService
from . import auth_crypto as crypto
from ...env import env
from ...entities import ProjectEntity


class ProjectService(BaseService):

    def create(self) -> ProjectEntity:
        """
        Creates a new project.
        NOTE: This is a work-in-progress and is minimally viable for the authentication feature.
        """
        # Create a new project
        project = ProjectEntity()
        self._admin_db.add(project)
        self._admin_db.flush()

        # Handle creating the authentication private key and public key
        private_key, public_key = crypto.generate_serialied_rsa_keypair()
        encryption_key = crypto.hkdf_derive_encryption_key(
            env.AUTH_MASTER_SECRET, project.id
        )
        encrypted_private_key = crypto.encrypt(private_key, encryption_key)

        # Update the project with the encrypted private key and public key
        project.auth_encrypted_private_key = encrypted_private_key
        project.auth_public_key = public_key
        self._admin_db.commit()

        return project
