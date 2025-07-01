"""
This file contains exceptions found in the service layer.

These custom exceptions can then be handled peoperly
at the API level.
"""


class ResourceNotFoundException(Exception):
    """ResourceNotFoundException is raised when a user attempts to access a resource that does not exist."""


class ContentDatabaseTransactionException(Exception):
    """Exception raised when an error occurs performing an operation on the content database."""
