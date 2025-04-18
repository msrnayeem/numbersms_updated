import functools
from flask import session, redirect, url_for
from app.utils.table import CRUD


# is auth middleware
def is_auth(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("landing.signin"))
        return func(*args, **kwargs)

    return wrapper


# is guest middleware
def is_guest(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if session.get("user_id"):
            return redirect(url_for("landing.dashboard"))
        return func(*args, **kwargs)

    return wrapper


# is admin middleware
def is_admin(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user = CRUD("users").get_by_column("id", session.get("user_id")).get("data")
        if user and user.get("role") != "admin":
            return redirect(url_for("landing.dashboard"))
        return func(*args, **kwargs)

    return wrapper


# is user middleware
def is_user(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user = CRUD("users").get_by_column("id", session.get("user_id")).get("data")
        if user and user.get("role") != "user":
            return redirect(url_for("landing.dashboard"))
        return func(*args, **kwargs)

    return wrapper


# email verification middleware
def is_verified(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user = CRUD("users").get_by_column("id", session.get("user_id")).get("data")
        if user and user.get("email_verify") != "yes":
            return redirect(url_for("landing.verify"))
        return func(*args, **kwargs)

    return wrapper


# emial already verified middleware
def is_already_verified(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user = CRUD("users").get_by_column("id", session.get("user_id")).get("data")
        if user and user.get("email_verify") == "yes":
            return redirect(url_for("landing.dashboard"))
        return func(*args, **kwargs)

    return wrapper


# is block
def is_active(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user = CRUD("users").get_by_column("id", session.get("user_id")).get("data")
        if user and user.get("status") != "good":
            return redirect(url_for("landing.blocked"))
        return func(*args, **kwargs)

    return wrapper


# is block
def is_not_block(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user = CRUD("users").get_by_column("id", session.get("user_id")).get("data")
        if user and user.get("status") == "good":
            return redirect(url_for("landing.dashboard"))
        return func(*args, **kwargs)

    return wrapper
