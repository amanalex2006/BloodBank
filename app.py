from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# load env
load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"

# DB config
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {"sslmode": "require"}
}

db = SQLAlchemy(app)

# =======================
# MODEL
# =======================
class Role(db.Model):
    __tablename__ = "Roles"  # must match EXACT case

    role = db.Column(db.BigInteger, primary_key=True)
    roleName = db.Column(db.Text, nullable=False)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    passwordhash = db.Column(db.Text, nullable=False)
    role_id = db.Column(
        db.BigInteger,
        db.ForeignKey("Roles.role")  # this now works
    )

    def __repr__(self):
        return f"<User {self.email}>"

# =======================
# ROUTES
# =======================

@app.route("/")
def home():
    return render_template("home.html")


# -------- SIGNUP --------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        name = request.form["name"]
        password = request.form["password"]
        role_id = request.form.get("role_id")

        # check duplicate
        if User.query.filter_by(email=email).first():
            return "Email already exists"

        user = User(
            email=email,
            name=name,
            passwordhash=generate_password_hash(password),
            role_id=role_id
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("signup.html")


# -------- LOGIN --------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.passwordhash, password):
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))

        return "Invalid credentials"

    return render_template("login.html")


# -------- DASHBOARD --------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    return render_template("dashboard.html", user=user)


# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))


# =======================
# RUN
# =======================
if __name__ == "__main__":
    app.run(debug=True)