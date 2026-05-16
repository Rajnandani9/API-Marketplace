from flask import Flask, render_template, request, redirect, url_for, session, g, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key"

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "database.db"


# ---------------- DATABASE ----------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    );

    CREATE TABLE IF NOT EXISTS apis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        monthly_cost REAL
    );

    CREATE TABLE IF NOT EXISTS subscriptions (
        user_id INTEGER,
        api_id INTEGER
    );

    CREATE TABLE IF NOT EXISTS usage (
        user_id INTEGER,
        api_id INTEGER,
        endpoint TEXT,
        used_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # sample APIs
    if not db.execute("SELECT * FROM apis").fetchone():
        db.executemany(
            "INSERT INTO apis (name, description, monthly_cost) VALUES (?, ?, ?)",
            [
                ("Weather API", "Weather data", 10),
                ("News API", "Latest news", 5),
            ],
        )
        db.commit()


# ---------------- USER LOAD ----------------
@app.before_request
def load_user():
    user_id = session.get("user_id")
    if user_id:
        g.user = get_db().execute(
            "SELECT * FROM users WHERE id=?", (user_id,)
        ).fetchone()
    else:
        g.user = None


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password),
            )
            db.commit()
            flash("Registered successfully", "success")
            return redirect("/login")
        except:
            flash("User already exists", "danger")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = get_db().execute(
            "SELECT * FROM users WHERE username=?", (username,)
        ).fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            flash("Login successful", "success")
            return redirect("/dashboard")
        else:
            flash("Invalid login", "danger")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if not g.user:
        return redirect("/login")

    apis = get_db().execute("SELECT * FROM apis").fetchall()
    return render_template("dashboard.html", apis=apis)


# ---------------- RUN ----------------
if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)