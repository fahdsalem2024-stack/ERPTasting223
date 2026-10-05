"""
Authentication helpers
"""
from functools import wraps
from flask import session, redirect, url_for, request
from web.settings_helper import verify_password, get_user


def login_required(f):
    """Decorator: requires login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


def current_user():
    """Get current logged-in user"""
    if "user_id" not in session:
        return None
    return {
        "id": session.get("user_id"),
        "username": session.get("username"),
        "full_name": session.get("full_name"),
        "role": session.get("role"),
    }


def is_admin():
    """Check if current user is admin"""
    return session.get("role") == "admin"


def login_user(username, password):
    """Login user - returns True on success"""
    user = verify_password(username, password)
    if not user:
        return False
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["full_name"] = user.get("full_name", user["username"])
    session["role"] = user.get("role", "user")
    session.permanent = True
    return True


def logout_user():
    """Logout"""
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("full_name", None)
    session.pop("role", None)
