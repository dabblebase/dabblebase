"""Testing suite for the project auth service."""

import pytest
from jwt.exceptions import InvalidSignatureError
from ....services import ProjectAuthService
from ....services.project import auth_crypto as crypto
from ....entities import UserAuthenticationProvider
from ..fixtures import project_auth_svc


# def test_authentication_workflow(
#     project_svc: ProjectService, project_auth_svc: ProjectAuthService
# ):
#     """
#     Tests the authentication workflow for a project.
#     NOTE: This test is a work-in-progress
#     """
#     # Create a dummy project
#     project = project_svc.create()
#     # Create a dummy user, imagining that the UNC SSO proxy provides `123456789` as the user's PID
#     user = project_auth_svc.get_or_create_user(
#         "123456789", UserAuthenticationProvider.UNC_SSO
#     )
#     # Generate a JWT token for the user to be authenticated with the project
#     jwt_token = project_auth_svc.generate_token_for_project_auth_request(
#         project.id, user.id
#     )
#     assert jwt_token is not None, "JWT token should be generated successfully"
#     # This token should be verifiable using the project's public key
#     jwt_payload = crypto.decode_jwt_with_asymmetric_keys(
#         jwt_token, project.auth_public_key
#     )
#     assert jwt_payload["id"] == user.id, "JWT token should contain the correct user ID"


# def test_decode_jwt_fails_with_wrong_public_key(
#     project_svc: ProjectService, project_auth_svc: ProjectAuthService
# ):
#     """ """
#     # Create two dummy projects
#     project_one = project_svc.create()
#     project_two = project_svc.create()
#     # Create a dummy user, imagining that the UNC SSO proxy provides `123456789` as the user's PID
#     user = project_auth_svc.get_or_create_user(
#         "123456789", UserAuthenticationProvider.UNC_SSO
#     )
#     # Sign a JWT token for the user to be authenticated with project 1
#     jwt_token = project_auth_svc.generate_token_for_project_auth_request(
#         project_one.id, user.id
#     )
#     # Assert that decoding the JWT token with project one's public key succeeds
#     crypto.decode_jwt_with_asymmetric_keys(jwt_token, project_one.auth_public_key)
#     # Assert that decoding the JWT token with project two's public key fails
#     with pytest.raises(InvalidSignatureError):
#         crypto.decode_jwt_with_asymmetric_keys(jwt_token, project_two.auth_public_key)
