import pytest
import uuid
from tests.api_tests.Aux_Library import (
    check_register_user,
    check_login_user,
    list_domains,
    add_domain,
    remove_domains,
    remove_user_from_running_app,
)

pytestmark = pytest.mark.order(4)


def test_domains_list_flow():
    username = f"dash_{uuid.uuid4().hex[:6]}"
    password = "Test1234"

    check_register_user(username, password, password)
    login = check_login_user(username, password)
    token = login.json()["token"]

    # empty state
    r = list_domains(token)
    assert r.status_code == 200
    assert r.json()["domains"] == []

    domain = f"{uuid.uuid4().hex[:6]}.com"

    add_domain(token, domain)
    r2 = list_domains(token)
    domains = r2.json()["domains"]
    assert any(d["domain"] == domain for d in domains)


    remove_domains(token, [domain])
    r3 = list_domains(token)
    assert domain not in r3.json()["domains"]

    remove_user_from_running_app(username)
