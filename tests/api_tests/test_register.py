from .Aux_Library import check_register_user, remove_user_from_running_app as remove_user
import pytest

pytestmark = pytest.mark.order(2)

# -------------------------------------------------
# Fixtures
# -------------------------------------------------

@pytest.fixture(scope="module")
def existing_username():
    return "test1"


@pytest.fixture(scope="module")
def new_username():
    return "test57"


# -------------------------------------------------
# Invalid Username Tests
# -------------------------------------------------

@pytest.mark.parametrize(
    "username,password,password_confirmation",
    [
        ("", "Qwe12345", "Qwe12345"),
        ("", "Qwe12345", "Qwe12346"),
        ("", "Qwe1234", "Qwe1234"),
        ("", "Qwe1234567890", "Qwe1234567890"),
        ("", "qwe12345", "qwe12345"),
        ("", "QWE12345", "QWE12345"),
        ("", "Qwertyuiop", "Qwertyuiop"),
        ("", "Qwe12345!", "Qwe12345!"),
        (" ", "Qwe12345", "Qwe12345"),
    ],
)
def test_2_register_invalid_username(username, password, password_confirmation):
    expected_error = "Username invalid."

    response = check_register_user(
        username=username,
        password=password,
        password_confirmation=password_confirmation,
    )

    assert response.status_code == 400
    assert response.json()["error"] == expected_error


# -------------------------------------------------
# Existing Username Tests
# -------------------------------------------------

@pytest.mark.parametrize(
    "password,password_confirmation",
    [
        ("Qwe12345", "Qwe12345"),
        ("Qwe12345", "Qwe12346"),
        ("Qwe1234", "Qwe1234"),
        ("Qwe1234567890", "Qwe1234567890"),
        ("qwe12345", "qwe12345"),
        ("QWE12345", "QWE12345"),
        ("Qwertyuiop", "Qwertyuiop"),
        ("Qwe12345!", "Qwe12345!"),
    ],
)
def test_3_register_existing_username(existing_username, password, password_confirmation):
    expected_error = "Username already taken."

    response = check_register_user(
        username=existing_username,
        password=password,
        password_confirmation=password_confirmation,
    )

    assert response.status_code == 409
    assert response.json()["error"] == expected_error


# -------------------------------------------------
# Invalid Password Confirmation Tests
# -------------------------------------------------

@pytest.mark.parametrize(
    "password,password_confirmation",
    [
        ("Qwe12345", "Qwe12346"),
        ("Qwe12345", "Qwe1234"),
        ("Qwe123456", "Qwe12345"),
        ("Qwe1234567891", "Qwe12345678901"),
        ("qwe12345", "Qwe12345"),
        ("QWE12345", "Qwe12345"),
        ("Qwertyuiop", "Qwertyuiopq"),
        ("Qwe12345!", "Qwe12345"),
    ],
)
def test_4_register_invalid_password_confirmation(new_username, password, password_confirmation):
    expected_error = "Password and Password Confirmation are not the same."

    response = check_register_user(
        username=new_username,
        password=password,
        password_confirmation=password_confirmation,
    )

    assert response.status_code == 400
    assert response.json()["error"] == expected_error


# -------------------------------------------------
# Invalid Password Tests
# -------------------------------------------------

@pytest.mark.parametrize(
    "password,password_confirmation,expected_error",
    [
        ("Qwe1234", "Qwe1234", "Password is not between 8 to 12 characters."),
        ("Qwe123", "Qwe123", "Password is not between 8 to 12 characters."),
        ("qwe1234", "qwe1234", "Password is not between 8 to 12 characters."),
        ("QWE123", "QWE123", "Password is not between 8 to 12 characters."),
        ("Qwert", "Qwert", "Password is not between 8 to 12 characters."),
        ("Qwe12!", "Qwe12!", "Password is not between 8 to 12 characters."),
        ("Qwe1234567890", "Qwe1234567890", "Password is not between 8 to 12 characters."),
        ("Qwe123456789012", "Qwe123456789012", "Password is not between 8 to 12 characters."),
        ("qwe1234567890", "qwe1234567890", "Password is not between 8 to 12 characters."),
        ("QWE1234567890", "QWE1234567890", "Password is not between 8 to 12 characters."),
        ("Qwertyuiopasd", "Qwertyuiopasd", "Password is not between 8 to 12 characters."),
        ("Qwe123456789!", "Qwe123456789!", "Password is not between 8 to 12 characters."),
        ("qwe12345", "qwe12345", "Password does not include at least one uppercase character."),
        ("qwertyuiop", "qwertyuiop", "Password does not include at least one uppercase character."),
        ("qwe12345!", "qwe12345!", "Password does not include at least one uppercase character."),
        ("QWE12345", "QWE12345", "Password does not include at least one lowercase character."),
        ("QWERTYUIOP", "QWERTYUIOP", "Password does not include at least one lowercase character."),
        ("QWE12345!", "QWE12345!", "Password does not include at least one lowercase character."),
        ("Qwertyuiop", "Qwertyuiop", "Password does not include at least one digit."),
        ("Qwertyuiop!", "Qwertyuiop!", "Password does not include at least one digit."),
        (
            "Qwe12345!",
            "Qwe12345!",
            "Password should include only uppercase characters, lowercase characters and digits!",
        ),
    ],
)
def test_5_register_invalid_password(new_username, password, password_confirmation, expected_error):
    response = check_register_user(
        username=new_username,
        password=password,
        password_confirmation=password_confirmation,
    )

    assert response.status_code == 400
    assert response.json()["error"] == expected_error


# -------------------------------------------------
# Successful Registration
# -------------------------------------------------

def test_6_register_successful_registration(new_username):
    response = check_register_user(
        username=new_username,
        password="Qwe12345",
        password_confirmation="Qwe12345",
    )

    assert response.status_code == 201
    assert response.json()["ok"] is True
    assert response.json()["message"] == "Registered successfully"

    remove_user(new_username)
