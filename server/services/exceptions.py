"""
This file contains exceptions found in the service layer.

These custom exceptions can then be handled peoperly
at the API level.
"""


class ResourceNotFoundException(Exception):
    """ResourceNotFoundException is raised when a user attempts to access a resource that does not exist."""


class ResourceAlreadyExistsException(Exception):
    """ResourceAlreadyExistsException is raised when a user attempts to create a resource that already exists."""


class UserPermissionException(Exception):
    """UserPermissionException is raised when a user attempts to acces a resource they are not allowed to access."""


class ContentDatabaseTransactionException(Exception):
    """Exception raised when an error occurs performing an operation on the content database."""


class InputValidationException(Exception):
    """Exception raised when input validation fails."""
