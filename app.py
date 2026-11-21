from datetime import datetime
import os
import random

from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager, UserMixin, current_user, login_required,
    login_user, logout_user
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "fortune-box-v0-development-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fortune_box.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Fortune(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), nullable=False, default="General")
    approved = db.Column(db.Boolean, nullable=False, default=True)
    submitted_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Draw(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    fortune_id = db.Column(db.Integer, db.ForeignKey("fortune.id"), nullable=False)
    drawn_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fortune = db.relationship("Fortune")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def admin_required():
    if not current_user.is_authenticated or current_user.role != "admin":
        abort(403)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Please complete every field.", "error")
        elif User.query.filter((User.username == username) | (User.email == email)).first():
            flash("That username or email is already registered.", "error")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Your account has been created.", "success")
            return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identity = request.form.get("identity", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter(
            (User.username == identity) | (User.email == identity.lower())
        ).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Welcome back!", "success")
            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("index"))

        flash("Invalid username/email or password.", "error")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


@app.route("/draw")
@login_required
def draw_fortune():
    fortunes = Fortune.query.filter_by(approved=True).all()
    if not fortunes:
        flash("There are no approved fortunes yet.", "error")
        return redirect(url_for("index"))

    fortune = random.choice(fortunes)
    draw = Draw(user_id=current_user.id, fortune_id=fortune.id)
    db.session.add(draw)
    db.session.commit()
    return render_template("draw.html", fortune=fortune)


@app.route("/my-fortunes")
@login_required
def my_fortunes():
    draws = Draw.query.filter_by(user_id=current_user.id).order_by(Draw.drawn_at.desc()).all()
    submissions = Fortune.query.filter_by(submitted_by=current_user.id).order_by(
        Fortune.created_at.desc()
    ).all()
    return render_template("my_fortunes.html", draws=draws, submissions=submissions)


@app.route("/submit-fortune", methods=["GET", "POST"])
@login_required
def submit_fortune():
    if request.method == "POST":
        content = request.form.get("content", "").strip()
        category = request.form.get("category", "General").strip() or "General"

        if not content:
            flash("Please enter a fortune.", "error")
        elif len(content) > 500:
            flash("Fortunes must be 500 characters or fewer.", "error")
        else:
            fortune = Fortune(
                content=content,
                category=category,
                approved=False,
                submitted_by=current_user.id
            )
            db.session.add(fortune)
            db.session.commit()
            flash("Thanks! Your fortune has been submitted for approval.", "success")
            return redirect(url_for("my_fortunes"))

    return render_template("submit_fortune.html")


@app.route("/admin")
@login_required
def admin_dashboard():
    admin_required()
    pending = Fortune.query.filter_by(approved=False).order_by(Fortune.created_at.desc()).all()
    approved = Fortune.query.filter_by(approved=True).order_by(Fortune.created_at.desc()).all()
    return render_template("admin.html", pending=pending, approved=approved)


@app.route("/admin/fortune/<int:fortune_id>/approve", methods=["POST"])
@login_required
def approve_fortune(fortune_id):
    admin_required()
    fortune = db.session.get(Fortune, fortune_id)
    if fortune is None:
        abort(404)
    fortune.approved = True
    db.session.commit()
    flash("Fortune approved.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/fortune/<int:fortune_id>/reject", methods=["POST"])
@login_required
def reject_fortune(fortune_id):
    admin_required()
    fortune = db.session.get(Fortune, fortune_id)
    if fortune is None:
        abort(404)
    db.session.delete(fortune)
    db.session.commit()
    flash("Submission rejected and deleted.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/fortune/new", methods=["GET", "POST"])
@login_required
def new_fortune():
    admin_required()
    if request.method == "POST":
        content = request.form.get("content", "").strip()
        category = request.form.get("category", "General").strip() or "General"
        if content:
            db.session.add(Fortune(content=content, category=category, approved=True))
            db.session.commit()
            flash("Fortune created.", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Fortune text cannot be empty.", "error")
    return render_template("fortune_form.html", fortune=None)


@app.route("/admin/fortune/<int:fortune_id>/edit", methods=["GET", "POST"])
@login_required
def edit_fortune(fortune_id):
    admin_required()
    fortune = db.session.get(Fortune, fortune_id)
    if fortune is None:
        abort(404)
    if request.method == "POST":
        content = request.form.get("content", "").strip()
        category = request.form.get("category", "General").strip() or "General"
        if content:
            fortune.content = content
            fortune.category = category
            db.session.commit()
            flash("Fortune updated.", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Fortune text cannot be empty.", "error")
    return render_template("fortune_form.html", fortune=fortune)


@app.route("/admin/fortune/<int:fortune_id>/delete", methods=["POST"])
@login_required
def delete_fortune(fortune_id):
    admin_required()
    fortune = db.session.get(Fortune, fortune_id)
    if fortune is None:
        abort(404)
    db.session.delete(fortune)
    db.session.commit()
    flash("Fortune deleted.", "success")
    return redirect(url_for("admin_dashboard"))


@app.errorhandler(403)
def forbidden(_error):
    return render_template("error.html", code=403, message="You do not have permission to view this page."), 403


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", code=404, message="The page or fortune could not be found."), 404


def initialise_database():
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", email="admin@example.com", role="admin")
            admin.set_password(os.environ.get("ADMIN_PASSWORD", "ChangeMe123!"))
            db.session.add(admin)

        if Fortune.query.count() == 0:
            starter_fortunes = [
                ("A small step today can lead to a big change tomorrow.", "Motivation"),
                ("Good things often arrive when you least expect them.", "Life"),
                ("Your curiosity will open an unexpected door.", "Adventure"),
                ("A kind word can change someone's entire day.", "Kindness"),
                ("The best time to begin is before you feel ready.", "Motivation"),
                ("An old friend may bring a new opportunity.", "Friendship"),
            ]
            for content, category in starter_fortunes:
                db.session.add(Fortune(content=content, category=category, approved=True))

        db.session.commit()


if __name__ == "__main__":
    initialise_database()
    app.run(debug=True)