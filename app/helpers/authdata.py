from flask import session
from app.utils.table import CRUD


def auth_data():
    if session.get("user_id"):
        user = CRUD("users").get_by_column("id", session.get("user_id")).get("data")
        if user:
            return {"auth": True, "role": user.get("role"), "data": user}
        else:
            return {}
    return {}
