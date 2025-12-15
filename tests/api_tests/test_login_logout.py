import pytest
from tests.api_tests.Aux_Library import check_login_user

pytestmark = pytest.mark.order(3)

# -------------------------------------------------
# Invalid Login Scenarios
# -------------------------------------------------
@pytest.mark.parametrize(
    "username,password",
    [
        ("JOHN_DOE", "PASSWORD"),        # case-sensitive mismatch
        ("john_doe", "wrong_password"),  # wrong password
        ("wrong_username", "password"),  # wrong username
        ("", "password"),                # empty username
        ("john_doe", ""),                # empty password
        ("", ""),                        # both empty
    ],
)
def test_login_invalid(username, password):
    response = check_login_user(username, password)

    assert response.status_code == 401
    body = response.json()

    assert body.get("ok") is False
    assert body.get("error") == "Invalid username or password"


# -------------------------------------------------
# Valid Login
# -------------------------------------------------
def test_login_valid():
    """
    Valid login should return:
    - HTTP 200
    - ok: True
    - username
    - JWT token
    """
    response = check_login_user("john_doe", "password")

    assert response.status_code == 200

    body = response.json()
    assert body.get("ok") is True
    assert body.get("username") == "john_doe"
    assert "token" in body
    assert isinstance(body["token"], str)
    assert len(body["token"]) > 20
