from flask import Flask, request, jsonify
from functools import wraps
import requests
import jwt
from flask_cors import CORS
import os
from jwt import PyJWKClient

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, allow_headers=["Content-Type", "Authorization"])

KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_BASE_URL")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")

OIDC_CONFIG_URL = f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}/.well-known/openid-configuration"

jwks_cache = None

def get_jwks():
    global jwks_cache
    if jwks_cache is None:
        oidc_config = requests.get(OIDC_CONFIG_URL).json()
        jwks_uri = oidc_config["jwks_uri"]
        jwks_cache = requests.get(jwks_uri).json()
    return jwks_cache

def verify_token(token):
    try:
        oidc_config = requests.get(OIDC_CONFIG_URL).json()
        jwks_uri = oidc_config["jwks_uri"]
        jwks_client = PyJWKClient(jwks_uri)
        signing_key = jwks_client.get_signing_key_from_jwt(token).key

        decoded = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience="account",
            options={"verify_iss": False} #the token issuer is localhost:8080 but the backend sees it as keycloak:8080
        )
        return decoded

    except jwt.ExpiredSignatureError:
        print("Expired token", flush=True)
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}", flush=True)
        return None
    except Exception as e:
        print(f"Error: {e}", flush=True)
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

@app.route("/api/user")
@login_required
def user():
    return jsonify({
        "message": "utente autenticato",
        "username": request.user.get("preferred_username"),
        "email": request.user.get("email"),
        "roles": request.user.get("realm_access", {}).get("roles", [])
    })

if __name__ == "__main__":
    app.run(app.run(host="0.0.0.0", port=5001))