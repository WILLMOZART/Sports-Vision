from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
from utils.helpers import (
    login_required,
    validate_email,
    validate_username,
    validate_password,
)

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/")
def index():
    return redirect(url_for("auth.login"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Username and password required", "error")
            return render_template("login.html")

        with db.get_connection() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

            if user and check_password_hash(user["password_hash"], password):
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["role"] = user["role"]
                flash(f"Welcome back, {user['username']}!", "success")
                return redirect(url_for("main.dashboard"))
            else:
                flash("Invalid credentials", "error")

    return render_template("login.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        errors = []

        if not validate_username(username):
            errors.append("Username must be at least 3 characters and alphanumeric")
        if not validate_email(email):
            errors.append("Invalid email format")
        if not validate_password(password):
            errors.append("Password must be at least 6 characters")
        if password != confirm_password:
            errors.append("Passwords do not match")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("register.html")

        password_hash = generate_password_hash(password)

        try:
            with db.get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO users (username, email, password_hash, role)
                    VALUES (?, ?, ?, 'user')
                """,
                    (username, email, password_hash),
                )
                conn.commit()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))

        except Exception as e:
            flash("Username or email already exists", "error")

    return render_template("register.html")


@auth.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("auth.login"))


@auth.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "change_password":
            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirm_password")

            with db.get_connection() as conn:
                user = conn.execute(
                    "SELECT password_hash FROM users WHERE id = ?",
                    (session["user_id"],),
                ).fetchone()

                if not check_password_hash(user["password_hash"], current_password):
                    flash("Current password is incorrect", "error")
                elif new_password != confirm_password:
                    flash("New passwords do not match", "error")
                elif len(new_password) < 6:
                    flash("Password must be at least 6 characters", "error")
                else:
                    new_hash = generate_password_hash(new_password)
                    conn.execute(
                        "UPDATE users SET password_hash = ? WHERE id = ?",
                        (new_hash, session["user_id"]),
                    )
                    conn.commit()
                    flash("Password changed successfully!", "success")

        elif action == "update_profile":
            email = request.form.get("email")

            if not validate_email(email):
                flash("Invalid email format", "error")
            else:
                try:
                    with db.get_connection() as conn:
                        conn.execute(
                            "UPDATE users SET email = ? WHERE id = ?",
                            (email, session["user_id"]),
                        )
                        conn.commit()
                    flash("Profile updated successfully!", "success")
                except:
                    flash("Email already in use", "error")

    with db.get_connection() as conn:
        user = conn.execute(
            "SELECT username, email, role, created_at FROM users WHERE id = ?",
            (session["user_id"],),
        ).fetchone()

    return render_template("profile.html", user=user)
