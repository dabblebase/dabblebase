"""Testing suite for the health service."""

from ...services import HealthService
from .fixtures import health_svc


def test_health_check(health_svc: HealthService):
    """Test the health check endpoint."""
    assert "OK" in health_svc.check(), "Health check should return 'OK'"
