from flask import Flask, redirect, render_template, request, session, url_for, jsonify
from authlib.integrations.flask_client import OAuth
from functools import wraps
import requests

app = Flask(__name__)
app.secret_key = "una_chiave_segretissima"

KEYCLOAK_BASE_URL = "http://localhost:8080"
REALM = "Simple-web-App"
CLIENT_ID = "Simple-web-app-Keycloak"
CLIENT_SECRET = "X4yOSYSTPyVWZBCgM1cR5pkMWkyKvx6H"

oauth = OAuth(app)
keycloak = oauth.register(
    name="keycloak",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url=f"{KEYCLOAK_BASE_URL}/realms/{REALM}/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user" not in session:
                return redirect(url_for("login"))
            roles = session["user"].get("realm_access", {}).get("roles", [])
            if role not in roles:
                return redirect(url_for("home"))
            return f(*args, **kwargs)
        return decorated
    return decorator

@app.route("/")
def home():
    return "sei nella home"

@app.route("/login")
def login():
    redirect_uri = url_for("auth_callback", _external=True)
    return keycloak.authorize_redirect(redirect_uri)

@app.route("/auth/callback")
def auth_callback():
    token = keycloak.authorize_access_token()
    userinfo = token.get("userinfo")
    session["user"] = userinfo
    #session["access_token"] = token["access_token"]
    return redirect(url_for("home"))

@app.route("/user")
@login_required
def user():
    user = session["user"]
    return f"pagina per utenti - benvenuto {user.get('preferred_username')}"

@app.route("/admin")
@role_required("admin")
def admin():
    user = session["user"]
    return f"pagina per admin - benvenuto {user.get('preferred_username')}"

@app.route("/logout")
def logout():
    access_token = session.get("access_token", "")
    session.clear()

    logout_url = (
        f"{KEYCLOAK_BASE_URL}/realms/{REALM}/protocol/openid-connect/logout"
        f"?post_logout_redirect_uri={url_for('home', _external=True)}"
        f"&client_id={CLIENT_ID}"
    )
    return redirect(logout_url)

if __name__ == "__main__":
    app.run(debug=True)