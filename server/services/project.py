"""
Service to handle CRUD operations on projects.
"""

from sqlalchemy import text
from .base import BaseService
from .auth_crypto import (
    generate_serialied_rsa_keypair,
    hkdf_derive_encryption_key,
    encrypt,
)


class ProjectService(BaseService):

    def create(self):
        """
        Creates a new project.
        NOTE: This is a work-in-progress and is minimally viable for the authentication feature.
        """
        project_id = 1
        # Handle creating the authentication private key and public key
        private_key, public_key = generate_serialied_rsa_keypair()
        encryption_key = hkdf_derive_encryption_key("AUTH_MASTER_SECRET", project_id)
        encrypted_private_key = encrypt(private_key, encryption_key)
