import pytest
import uuid
from tests.api_tests.Aux_Library import (
    check_register_user,
    check_login_user,
    scan_domains,
    remove_user_from_running_app,
)

pytestmark = pytest.mark.order(6)


def test_scan_domains_unauthorized():
    response = scan_domains()
    assert response.status_code == 401
    assert response.json().get("ok") is False


def test_scan_domains_authorized():
    username = f"scan_{uuid.uuid4().hex[:6]}"
    password = "StrongPass12"

    reg = check_register_user(username, password, password)
    assert reg.status_code == 201

    login = check_login_user(username, password)
    token = login.json().get("token")
    assert token

    scan = scan_domains(token)
    assert scan.status_code == 200
    assert scan.json().get("ok") is True
    assert isinstance(scan.json().get("updated"), int)

    remove_user_from_running_app(username)
