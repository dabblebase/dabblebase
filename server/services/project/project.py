"""
Service to handle CRUD operations on projects.
"""

from sqlalchemy import text
from ..base import BaseService
from . import auth_crypto as crypto
from ...env import env
from ...entities import ProjectEntity
from ...services import ContentDatabaseNamingConventions, ContentDbClusterService
from ...models.auth import Subject
from ...models.project import CreateProjectRequest
from sqlalchemy.orm import Session
from fastapi import Depends
from ...database import admin_db_session
from ...services.project import auth_crypto as crypto


# class ProjectService:

#     _admin_db: Session

#     def __init__(
#         self,
#         admin_db: Session = Depends(admin_db_session),
#         content_db_cluster_svc: ContentDbClusterService = Depends(),
#     ):
#         self._admin_db = admin_db
#         self._content_db_cluster_svc = content_db_cluster_svc

#     def create(self, subject: Subject, request: CreateProjectRequest) -> ProjectEntity:
#         """
#         Creates a new project.
#         NOTE: This is a work-in-progress and is minimally viable for the authentication feature.
#         """
#         # Create a new project
#         project = ProjectEntity(
#             assignment_id=request.assignment_id,
#             group_id=request.group_id,
#             user_id=request.user_id,
#         )
#         self._admin_db.add(project)
#         self._admin_db.flush()

#         # Handle creating the authentication private key and public key
#         private_key, public_key = crypto.generate_serialied_rsa_keypair()
#         encryption_key = crypto.hkdf_derive_encryption_key(
#             env.AUTH_MASTER_SECRET, project.id
#         )
#         encrypted_private_key = crypto.encrypt(private_key, encryption_key)

#         # Update the project with the encrypted private key and public key
#         project.auth_encrypted_private_key = encrypted_private_key
#         project.auth_public_key = public_key

#         # Create the database for the project
#         db_name = ContentDatabaseNamingConventions.name_for_assignment_db(
#             assignment_id=request.assignment_id, project_id=project.id
#         )
#         admin_role_name, admin_role_password = (
#             self._content_db_cluster_svc.provision_database(db_name)
#         )

#         # Add a student user to the database
#         student_role_name = (
#             ContentDatabaseNamingConventions.name_for_assignment_db_student_role(
#                 assignment_id=request.assignment_id, project_id=project.id
#             )
#         )
#         student_role_password = crypto.generate_secure_password()
#         encrypted_student_role_password = (
#             self._content_db_cluster_svc.encrypt_role_password(
#                 student_role_password, request.assignment_id
#             )
#         )


#         self._content_db_cluster_svc.provision_role_for_database(
#             db_name, student_role_name
#         )

#         self._admin_db.commit()

#         return project
