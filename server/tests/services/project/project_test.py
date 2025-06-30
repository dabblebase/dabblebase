"""Testing suite for the project service."""

from ....services import ProjectService
from ..fixtures import project_svc


def test_create(project_svc: ProjectService):
    """Tests creating a project."""
    project = project_svc.create()
    assert project is not None, "Project creation should return a project object"
    assert project.id is not None, "Project should have an ID after creation"
    assert (
        project.auth_encrypted_private_key is not None
    ), "Project should have an encrypted private key after creation"
    assert (
        project.auth_public_key is not None
    ), "Project should have a public key after creation"
