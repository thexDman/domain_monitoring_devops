import os
import requests
import json
import re
from backend.UserManagementModule import UserManager as UM

# -----------------------------------------------------
# Global session and Base URL configuration
# -----------------------------------------------------
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
API_PREFIX = "/api"
session = requests.Session()


# -----------------------------------------------------
# Utility Functions
# -----------------------------------------------------
def print_response(response):
    print(f"\n[{response.request.method}] {response.url}")
    print(f"Status: {response.status_code}")
    try:
        print("Response JSON:", json.dumps(response.json(), indent=2))
    except Exception:
        print("Response Text:", response.text[:300])
    print("-" * 60)


# -----------------------------------------------------
# General HTTP helpers
# -----------------------------------------------------
def get(path: str, headers=None):
    return session.get(f"{BASE_URL}{path}", headers=headers)


def post(path: str, json=None, headers=None, files=None):
    return session.post(f"{BASE_URL}{path}", json=json, headers=headers, files=files)


# -----------------------------------------------------
# Auth
# -----------------------------------------------------
def check_register_user(username, password, password_confirmation):
    payload = {
        "username": username,
        "password": password,
        "password_confirmation": password_confirmation,
    }
    response = post(f"{API_PREFIX}/auth/register", json=payload)
    print_response(response)
    return response


def check_login_user(username, password):
    payload = {
        "username": username,
        "password": password,
    }
    response = post(f"{API_PREFIX}/auth/login", json=payload)
    print_response(response)
    return response


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


# -----------------------------------------------------
# Domains
# -----------------------------------------------------
def list_domains(token):
    response = get(
        f"{API_PREFIX}/domains",
        headers=auth_headers(token),
    )
    print_response(response)
    return response


def add_domain(token, domain):
    response = post(
        f"{API_PREFIX}/domains",
        json={"domain": domain},
        headers=auth_headers(token),
    )
    print_response(response)
    return response


def remove_domains(token, domains):
    response = requests.delete(
        f"{BASE_URL}{API_PREFIX}/domains",
        json={"domains": domains},
        headers=auth_headers(token),
    )
    print_response(response)
    return response


# -----------------------------------------------------
# Monitoring
# -----------------------------------------------------
def scan_domains(token=None):
    headers = auth_headers(token) if token else None
    response = post(f"{API_PREFIX}/domains/scan", headers=headers)
    print_response(response)
    return response


# -----------------------------------------------------
# Admin / cleanup
# -----------------------------------------------------
def remove_user_from_running_app(username):
    UM().remove_user(username)
    return post(f"{API_PREFIX}/admin/reload_users_to_memory")
