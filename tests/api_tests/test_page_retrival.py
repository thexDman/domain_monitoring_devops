import pytest
from tests.api_tests.Aux_Library import get

pytestmark = pytest.mark.order(1)


@pytest.mark.parametrize(
    "PATH",
    [
        "/api/health",
        "/api/auth/login",
        "/api/auth/register",
    ],
)
def test_api_endpoints_exist(PATH):
    response = get(PATH)
    assert response.status_code in (200, 401, 405)
