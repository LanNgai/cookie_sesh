from pathlib import Path
import os
import random
import sqlite3

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-development-secret")

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "fortunes.db"

STARTER_FORTUNES = [
    "A small step today can lead to a wonderful adventure tomorrow.",
    "The answer you seek may arrive when you make room for quiet.",
    "A kind word can change the direction of someone's day.",
    "Trust the progress you are making, even when it feels slow.",
    "An unexpected opportunity may be closer than you think.",
]


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS fortunes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        count = db.execute("SELECT COUNT(*) FROM fortunes").fetchone()[0]
        if count == 0:
            db.executemany(
                "INSERT OR IGNORE INTO fortunes (text) VALUES (?)",
                [(fortune,) for fortune in STARTER_FORTUNES],
            )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/draw", methods=["POST"])
def draw_fortune():
    with get_db() as db:
        fortunes = db.execute("SELECT text FROM fortunes").fetchall()
    if not fortunes:
        flash("There are no fortunes in the pool yet. Add one to get started.", "info")
        return redirect(url_for("home"))
    fortune = random.choice(fortunes)["text"]
    return render_template("index.html", fortune=fortune)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if not name or not email or not message:
            flash("Please complete every field.", "error")
        else:
            # Demo behavior: this confirms receipt but does not send an email.
            flash("Thanks for reaching out! This demo form does not send email yet.", "success")
            return redirect(url_for("contact"))
    return render_template("contact.html")


@app.route("/admin")
def admin():
    with get_db() as db:
        fortunes = db.execute(
            "SELECT id, text, created_at FROM fortunes ORDER BY id DESC"
        ).fetchall()
    return render_template("admin.html", fortunes=fortunes)


@app.route("/submit", methods=["GET", "POST"])
def submit_fortune():
    if request.method == "POST":
        fortune = request.form.get("fortune", "").strip()
        if not fortune:
            flash("Please enter a fortune before submitting.", "error")
        elif len(fortune) > 500:
            flash("Please keep fortunes to 500 characters or fewer.", "error")
        else:
            try:
                with get_db() as db:
                    db.execute("INSERT INTO fortunes (text) VALUES (?)", (fortune,))
                flash("Your fortune was added to the pool!", "success")
                return redirect(url_for("admin"))
            except sqlite3.IntegrityError:
                flash("That fortune is already in the pool. Try writing a different one.", "error")
    return render_template("submit.html")


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(debug=True)
