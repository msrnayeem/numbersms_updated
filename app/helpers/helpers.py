import re
import os
from flask import url_for, current_app


# valid email
def is_email(email):
    if not email:
        return False
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_regex, email))


# get media
def get_media(path=""):
    base_path = "media"
    uploads_path = os.path.join(base_path, "uploads", path)
    placeholder_path = os.path.join(base_path, "placeholder.png")
    static_folder = current_app.static_folder
    if path != "":
        absolute_uploads_path = os.path.join(static_folder, uploads_path)
        absolute_placeholder_path = os.path.join(static_folder, placeholder_path)

        if os.path.exists(absolute_uploads_path):
            return url_for("static", filename=uploads_path.replace(os.sep, "/"))
        elif os.path.exists(absolute_placeholder_path):
            return url_for("static", filename=placeholder_path.replace(os.sep, "/"))
        else:
            return ""
    else:
        absolute_placeholder_path = os.path.join(static_folder, placeholder_path)
        if os.path.exists(absolute_placeholder_path):
            return url_for("static", filename=placeholder_path.replace(os.sep, "/"))
        else:
            return ""
