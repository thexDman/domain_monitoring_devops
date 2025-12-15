import pytest
from tests.api_tests.Aux_Library import check_register_user, remove_user_from_running_app

pytestmark = pytest.mark.order(2)


@pytest.fixture(scope="module")
def existing_username():
    return "test1"


@pytest.fixture(scope="module")
def new_username():
    return "test57"


@pytest.mark.parametrize(
    "username,password,password_confirmation",
    [
        ("", "Qwe12345", "Qwe12345"),
        ("", "Qwe12345", "Qwe12346"),
        (" ", "Qwe12345", "Qwe12345"),
    ],
)
def test_register_invalid_username(username, password, password_confirmation):
    response = check_register_user(username, password, password_confirmation)
    assert response.status_code == 400
    assert response.json().get("ok") is False
    assert "error" in response.json()


def test_register_existing_username(existing_username):
    response = check_register_user(existing_username, "Qwe12345", "Qwe12345")
    assert response.status_code == 409
    assert response.json().get("ok") is False


@pytest.mark.parametrize(
    "password,password_confirmation",
    [
        ("Qwe12345", "Qwe12346"),
        ("Qwe123", "Qwe123"),
    ],
)
def test_register_invalid_password_confirmation(new_username, password, password_confirmation):
    response = check_register_user(new_username, password, password_confirmation)
    assert response.status_code == 400
    assert response.json().get("ok") is False


def test_register_success(new_username):
    response = check_register_user(new_username, "Qwe12345", "Qwe12345")
    assert response.status_code == 201
    assert response.json().get("ok") is True

    remove_user_from_running_app(new_username)
