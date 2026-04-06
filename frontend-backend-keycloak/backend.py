from flask import Flask, request, jsonify
from functools import wraps
import requests
import jwt
from flask_cors import CORS

app = Flask(__name__)
from flask_cors import CORS

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, allow_headers=["Content-Type", "Authorization"])

KEYCLOAK_BASE_URL = "http://localhost:8080"
REALM = "Simple-web-App"
CLIENT_ID = "Simple-web-app-Keycloak"

OIDC_CONFIG_URL = f"{KEYCLOAK_BASE_URL}/realms/{REALM}/.well-known/openid-configuration"
oidc_config = requests.get(OIDC_CONFIG_URL).json()
JWKS_URI = oidc_config["jwks_uri"]

jwks = requests.get(JWKS_URI).json()

def verify_token(token):
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header["kid"]
        key = next(k for k in jwks["keys"] if k["kid"] == kid)
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)

        decoded = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"]
        )

        if decoded.get("azp") != CLIENT_ID:
            print("Audience/azp mismatch")
            return None

        return decoded

    except Exception as e:
        print("Token error:", e)
        return None


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Missing Authorization header"}), 401

        try:
            token = auth_header.split(" ")[1]
        except:
            return jsonify({"error": "Invalid Authorization format"}), 401

        user = verify_token(token)

        if not user:
            return jsonify({"error": "Invalid or expired token"}), 401

        request.user = user
        return f(*args, **kwargs)

    return decorated


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            roles = request.user.get("realm_access", {}).get("roles", [])

            if role not in roles:
                return jsonify({"error": "Forbidden"}), 403

            return f(*args, **kwargs)

        return decorated
    return decorator

@app.route("/api/user")
@login_required
def user():
    return jsonify({
        "message": "utente autenticato",
        "username": request.user.get("preferred_username"),
        "email": request.user.get("email"),
        "roles": request.user.get("realm_access", {}).get("roles", [])
    })

@app.route("/api/admin")
@role_required("admin")
def admin():
    return jsonify({
        "message": "area admin",
        "user": request.user.get("preferred_username")
    })

if __name__ == "__main__":
    app.run(debug=True)