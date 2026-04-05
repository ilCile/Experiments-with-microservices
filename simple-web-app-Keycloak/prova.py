from flask import Flask, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

#docker run --name my-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -v pgdata:/var/lib/postgresql/data -d postgres:15

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/postgres'
app.secret_key = "una_chiave_segretissima"

db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(1), unique=False, nullable=False)

@app.route("/")
def home():
    return "sei nella home"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_role'] = user.role
            return redirect(url_for("secret"))
        else:
            return "Username o password errati."

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        hashed_password = generate_password_hash(request.form.get("password"), method="pbkdf2:sha256", salt_length=16)
        user = Users(
            username=request.form.get("username"),
            password=hashed_password,
            email=request.form.get("email"),
            role="U"
        )
        try:
            db.session.add(user)
            db.session.commit()
            return "Utente creato correttamente!"
        except Exception as e:
            db.session.rollback()
            return f"Errore: {str(e)}"
    return render_template("register.html")

@app.route("/user", methods=["GET"])
def user():
    if 'user_id' not in session:
        return redirect(url_for("login"))
    return f"pagina segreta per soli utenti {session['user_id']}"

@app.route("/admin", methods=["GET"])
def admin():
    if 'user_id' not in session:
        return redirect(url_for("login"))
    if session.get('user_role') != 'A':
        return redirect(url_for("home"))
    return f"pagina segreta per soli admin {session['user_id']}"

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)