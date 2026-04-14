from flask import Flask, request, jsonify
from functools import wraps
import requests
import jwt
from flask_cors import CORS
import os
from jwt import PyJWKClient
from models import db, Post

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URL")

db.init_app(app)

with app.app_context():
    db.create_all()

CORS(app, 
  resources={r"/*": {"origins": "https://api.local"}}, 
  allow_headers=["Content-Type", "Authorization"],
  supports_credentials=True
)

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

@app.route("/getPosts")
@login_required
def getPosts():
    posts = Post.query.filter_by(author_id=request.user.get("sub")).all()
    print(len(posts), flush=True)
    return jsonify([
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "author_id": post.author_id
        }
        for post in posts
    ])

@app.route("/createPost", methods=["POST"])
@login_required
def createPost():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    title = data.get("title")
    content = data.get("content")
    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400
    author_id = request.user.get("sub")
    try:
        post = Post(
            title=title,
            content=content,
            author_id=author_id,
        )
        db.session.add(post)
        db.session.commit()
        return jsonify({
            "message": "Post created successfully",
            "post": {
                "title": post.title,
                "content": post.content,
                "author_id": post.author_id
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(app.run(host="0.0.0.0", port=5001))