import pytest
import requests
import uuid
from tests.api_tests import Aux_Library as aux

pytestmark = pytest.mark.order(5)

# -------------------------------------------------
# Fixtures
# -------------------------------------------------
@pytest.fixture(scope="session")
def auth_token():
    """
    Create a test user and return a valid JWT token.
    """
    username = f"pytest_domains_{uuid.uuid4().hex[:6]}"
    password = "StrongPass12"

    reg = aux.check_register_user(username, password, password)
    assert reg.status_code in (201, 409)

    login = aux.check_login_user(username, password)
    assert login.status_code == 200

    token = login.json().get("token")
    assert token

    yield token

    aux.remove_user_from_running_app(username)


@pytest.fixture
def auth_headers(auth_token):
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }


# -------------------------------------------------
# 1. Add / Remove Domain – Happy Flow
# -------------------------------------------------
def test_add_and_remove_domain(auth_headers):
    base = aux.BASE_URL
    domain = f"pytest-{uuid.uuid4().hex[:6]}.com"

    # Add domain
    add_resp = requests.post(
        f"{base}/api/domains",
        json={"domain": domain},
        headers=auth_headers,
    )
    assert add_resp.status_code in (201, 409)
    assert add_resp.json().get("ok") is True

    # List domains
    list_resp = requests.get(
        f"{base}/api/domains",
        headers=auth_headers,
    )
    assert list_resp.status_code == 200
    domains = list_resp.json().get("domains", [])
    assert domain in domains

    # Remove domain
    remove_resp = requests.delete(
        f"{base}/api/domains",
        json={"domains": [domain]},
        headers=auth_headers,
    )
    assert remove_resp.status_code == 200
    assert remove_resp.json().get("ok") is True

    # Verify removal
    verify = requests.get(
        f"{base}/api/domains",
        headers=auth_headers,
    )
    assert domain not in verify.json().get("domains", [])


# -------------------------------------------------
# 2. Authorization Failures
# -------------------------------------------------
def test_remove_domain_without_auth():
    resp = requests.delete(
        f"{aux.BASE_URL}/api/domains",
        json={"domains": ["unauth.com"]},
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 401


# -------------------------------------------------
# 3. Edge Cases
# -------------------------------------------------
def test_remove_nonexistent_domain(auth_headers):
    resp = requests.delete(
        f"{aux.BASE_URL}/api/domains",
        json={"domains": ["does-not-exist.com"]},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json().get("ok") is True


def test_bulk_remove_domains(auth_headers):
    base = aux.BASE_URL
    domains = [f"bulk{i}-{uuid.uuid4().hex[:4]}.com" for i in range(3)]

    for d in domains:
        requests.post(
            f"{base}/api/domains",
            json={"domain": d},
            headers=auth_headers,
        )

    rem = requests.delete(
        f"{base}/api/domains",
        json={"domains": domains},
        headers=auth_headers,
    )
    assert rem.status_code == 200

    remaining = requests.get(
        f"{base}/api/domains",
        headers=auth_headers,
    ).json().get("domains", [])

    for d in domains:
        assert d not in remaining


def test_remove_domains_empty_payload(auth_headers):
    resp = requests.delete(
        f"{aux.BASE_URL}/api/domains",
        json={},
        headers=auth_headers,
    )
    assert resp.status_code == 400
