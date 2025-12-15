import pytest
import uuid
from tests.api_tests.Aux_Library import (
    check_register_user,
    check_login_user,
    scan_domains,
    remove_user_from_running_app,
)

pytestmark = pytest.mark.order(6)

# -------------------------------------------------
# 1. Unauthorized access
# -------------------------------------------------
def test_scan_domains_unauthorized():
    response = scan_domains()

    assert response.status_code == 401

    data = response.json()
    assert isinstance(data, dict)
    assert "error" in data
    assert "authorization" in data["error"].lower()


# -------------------------------------------------
# 2. Authorized access
# -------------------------------------------------
def test_scan_domains_authorized():
    username = f"scan_{uuid.uuid4().hex[:6]}"
    password = "StrongPass12"

    reg = check_register_user(username, password, password)
    assert reg.status_code == 201

    login = check_login_user(username, password)
    assert login.status_code == 200

    token = login.json().get("token")
    assert token, "JWT token missing from login response"

    scan = scan_domains(token)
    assert scan.status_code == 200

    data = scan.json()
    assert data.get("ok") is True
    assert "updated" in data
    assert isinstance(data["updated"], int)
    assert data["updated"] >= 0

    remove_user_from_running_app(username)
