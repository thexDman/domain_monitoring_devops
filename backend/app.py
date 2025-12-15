from flask import Flask, request, jsonify
import os
import tempfile

from UserManagementModule import UserManager as UM
from DomainManagementEngine import DomainManagementEngine as DME
from MonitoringSystem import MonitoringSystem as MS

from auth.token import generate_token
from auth.decorators import require_auth

import logger

# -------------------------------------------------
# App & Core Services
# -------------------------------------------------
logger = logger.setup_logger("app")

app = Flask(__name__)

user_manager = UM()
domain_engine = DME()
monitoring_system = MS()


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _json_payload():
    """Safely extract JSON body."""
    return request.get_json(silent=True) or {}


def _add_cors_headers(resp):
    """
    Minimal CORS support.
    In production you would restrict origins.
    """
    origin = request.headers.get("Origin", "*")
    resp.headers["Access-Control-Allow-Origin"] = origin
    resp.headers["Vary"] = "Origin"
    resp.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
    return resp


@app.after_request
def after_request(resp):
    return _add_cors_headers(resp)


@app.route("/api/<path:_any>", methods=["OPTIONS"])
def api_preflight(_any):
    """CORS preflight handler"""
    return _add_cors_headers(jsonify({"ok": True})), 200


# -------------------------------------------------
# AUTH API (JWT)
# -------------------------------------------------
@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = _json_payload()

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if user_manager.validate_login(username, password):
        token = generate_token(username)
        return jsonify({
            "ok": True,
            "username": username,
            "token": token
        }), 200

    return jsonify({
        "ok": False,
        "error": "Invalid username or password"
    }), 401


@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = _json_payload()

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    password_confirmation = data.get("password_confirmation") or ""

    try:
        result = user_manager.register_page_add_user(
            username,
            password,
            password_confirmation,
            domain_engine
        )

        if "error" in result:
            msg = result.get("error", "").lower()
            if "already" in msg or "taken" in msg:
                return jsonify({"ok": False, **result}), 409
            return jsonify({"ok": False, **result}), 400

        return jsonify({
            "ok": True,
            "message": "Registered successfully"
        }), 201

    except Exception as e:
        logger.error(f"Registration failed: {e}")
        return jsonify({
            "ok": False,
            "error": "Registration failed"
        }), 500


# -------------------------------------------------
# DOMAIN APIs (JWT protected)
# -------------------------------------------------
@app.route("/api/domains", methods=["GET"])
@require_auth
def api_list_domains(username):
    try:
        domains = domain_engine.list_domains(username)
        return jsonify({
            "ok": True,
            "domains": domains
        }), 200
    except Exception as e:
        logger.error(f"List domains failed for {username}: {e}")
        return jsonify({
            "ok": False,
            "error": "Failed to retrieve domains"
        }), 500


@app.route("/api/domains", methods=["POST"])
@require_auth
def api_add_domain(username):
    data = _json_payload()
    raw_domain = (data.get("domain") or "").strip()

    ok, normalized, reason = domain_engine.validate_domain(raw_domain)
    if not ok:
        return jsonify({
            "ok": False,
            "error": f"Invalid domain: {reason}"
        }), 400

    if not domain_engine.add_domain(username, normalized):
        return jsonify({
            "ok": False,
            "error": "Domain already exists"
        }), 409

    return jsonify({
        "ok": True,
        "domain": normalized
    }), 201


@app.route("/api/domains", methods=["DELETE"])
@require_auth
def api_remove_domains(username):
    data = _json_payload()
    domains = data.get("domains")

    if not isinstance(domains, list) or not domains:
        return jsonify({
            "ok": False,
            "error": "Request must include a non-empty 'domains' list"
        }), 400

    result = domain_engine.remove_domains(username, domains)
    return jsonify({
        "ok": True,
        "summary": result
    }), 200


@app.route("/api/domains/bulk", methods=["POST"])
@require_auth
def api_bulk_domains(username):
    uploaded = request.files.get("file")

    if not uploaded:
        return jsonify({"ok": False, "error": "File is required"}), 400

    if not uploaded.filename.lower().endswith(".txt"):
        return jsonify({"ok": False, "error": "Only .txt files allowed"}), 400

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp_path = tmp.name
            uploaded.save(tmp_path)

        summary = domain_engine.bulk_upload(username, tmp_path)
        status = 200 if summary.get("ok") else 400
        return jsonify(summary), status

    except Exception as e:
        logger.error(f"Bulk upload failed for {username}: {e}")
        return jsonify({"ok": False, "error": "Bulk upload failed"}), 500

    finally:
        if tmp_path:
            try:
                os.remove(tmp_path)
            except Exception:
                pass


# -------------------------------------------------
# MONITORING
# -------------------------------------------------
@app.route("/api/domains/scan", methods=["POST"])
@require_auth
def api_scan_domains(username):
    try:
        updated = monitoring_system.scan_user_domains(
            username,
            dme=domain_engine
        )
        return jsonify({
            "ok": True,
            "updated": len(updated)
        }), 200
    except Exception as e:
        logger.error(f"Scan failed for {username}: {e}")
        return jsonify({
            "ok": False,
            "error": "Scan failed"
        }), 500


# -------------------------------------------------
# OPS / ADMIN (OPTIONAL)
# -------------------------------------------------
@app.route("/api/admin/reload_users_to_memory", methods=["POST"])
def api_reload_users_to_memory():
    try:
        user_manager.load_users_json_to_memory()
        return jsonify({"ok": True}), 200
    except Exception as e:
        logger.error(f"Reload users failed: {e}")
        return jsonify({"ok": False, "error": "Reload failed"}), 500

# -------------------------------------------------
# Health Check
# -------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "ok": True,
        "service": "domain-monitoring-backend"
    }), 200


# -------------------------------------------------
# ENTRYPOINT
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
