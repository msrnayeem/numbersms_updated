from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    request,
    url_for,
    jsonify,
    session,
)
from app.helpers.middleware import is_auth, is_user, is_verified, is_active
from app.helpers.authdata import auth_data
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.table import CRUD
from dotenv import load_dotenv
import os

user = Blueprint("user", __name__, template_folder="templates")

load_dotenv()


# dashboard ===========
@user.route("/")
@is_auth
@is_verified
@is_user
@is_active
def dashboard():
    try:
        balance = auth_data().get("data").get("coin")
        service = (
            CRUD("verifications")
            .count(user_id=auth_data().get("data").get("id"))
            .get("data")
        )
        c_service = (
            CRUD("verifications")
            .count(user_id=auth_data().get("data").get("id"), status="complete")
            .get("data")
        )

        x_service = (
            CRUD("verifications")
            .count(
                user_id=auth_data().get("data").get("id"),
                status="cancel",
            )
            .get("data")
        )
        tx_service = (
            CRUD("verifications")
            .count(
                user_id=auth_data().get("data").get("id"),
                status="timeout",
            )
            .get("data")
        )
        data = {
            "balance": float(f"{balance:.2f}"),
            "service": service,
            "c_service": c_service,
            "x_service": x_service,
            "tx_service": tx_service,
        }
        return render_template("/users/dashboard.html", data=data)
    except Exception as e:
        flash("An error occurred. Please try again", "error")
        return render_template("/users/dashboard.html", data={})


# creadits ===============
@user.route("/creadits", methods=["POST", "GET"])
@is_auth
@is_verified
@is_user
@is_active
def creadits():
    try:
        model = CRUD("transactions")
        data = model.where(user_id=auth_data().get("data").get("id"))

        if request.method == "GET":
            id = request.args.get("id")
            order = request.args.get("order")
            if id and order == "delete":
                model.delete(id)
                flash("Deleted successfully", "success")
                return redirect(url_for("user.creadits"))
        return render_template(
            "/users/creadits.html", data=data, stripe_pk=os.getenv("STRIPE_PUBLIC_KEY")
        )
    except Exception:
        flash("An error occurred. Please try again", "error")
        return render_template(
            "/users/creadits.html", data={}, stripe_pk=os.getenv("STRIPE_PUBLIC_KEY")
        )


# acounts ==========
@user.route("/account", methods=["GET", "POST"])
@is_auth
@is_verified
@is_user
@is_active
def account():
    try:
        user = CRUD("users")
        if request.method == "POST":
            name = request.form.get("name")
            c_password = request.form.get("c_password")
            n_password = request.form.get("n_password")
            hashed_password = generate_password_hash(n_password)

            # validation
            if not name:
                flash("Name fields are required")
                return render_template("/users/account.html")

            # update users name
            user.update(auth_data().get("data").get("id"), name=name)

            # if password has
            if c_password and n_password:
                # check password less cherecter
                if len(n_password) < 8:
                    flash("New Password must be at least 8 characters long", "error")
                    return render_template("/users/account.html")

                # check hased password
                if check_password_hash(
                    auth_data().get("data").get("password"), c_password
                ):
                    user.update(
                        auth_data().get("data").get("id"), password=hashed_password
                    )
                    flash("Profile updated successfully", "success")
                else:
                    flash("Current password is incorrect", "error")
            return render_template("/users/account.html")
        else:
            return render_template("/users/account.html")
    except Exception as e:
        flash("An error occurred. Please try again", "error")
        return render_template("/users/account.html")


# supports ==========
@user.route("/support", methods=["POST", "GET"])
@is_auth
@is_verified
@is_user
@is_active
def support():
    try:
        model = CRUD("supports")
        if request.method == "POST":
            subject = request.json.get("subject")
            message = request.json.get("message")

            if not all([subject, message]):
                return jsonify(
                    {"status": "error", "message": "All fields are required"}
                )

            create = model.create(
                user_id=auth_data().get("data").get("id"),
                name=auth_data().get("data").get("name"),
                email=auth_data().get("data").get("email"),
                subject=subject,
                message=message,
            )
            if create.get("status") == "success":
                return jsonify(
                    {"status": "success", "message": "Ticket opened successfully"}
                )
            else:
                return jsonify(
                    {
                        "status": "error",
                        "message": "Failed to open ticket. Please try again!",
                    }
                )
        else:
            id = request.args.get("id")
            order = request.args.get("order")
            if id and order == "delete":
                model.delete(id)
                flash("Deleted successfull", "success")
                return redirect(url_for("user.support"))

            return render_template(
                "/users/support.html",
                data=model.where(
                    user_id=auth_data().get("data").get("id"),
                ),
                rating=CRUD("reviews").count(user_id=auth_data().get("data").get("id")),
            )
    except Exception as e:
        flash("An error occurred. Please try again", "error")
        return render_template("/users/support.html", data={}, rating={})


# reqview
@user.route("/review", methods=["POST"])
@is_auth
@is_verified
@is_user
@is_active
def review():
    try:
        rating = request.json.get("rating")
        name = request.json.get("name")
        ocopation = request.json.get("ocopation")
        message = request.json.get("message")
        model = CRUD("reviews")

        if not all([rating, name, ocopation, message]):
            return jsonify({"status": "error", "message": "All fields are required"})

        create = model.create(
            user_id=auth_data().get("data").get("id"),
            user_name=name,
            ocopation=ocopation,
            message=message,
            rating=int(rating),
        )
        if create:
            return jsonify({"status": "success", "message": "Thanks for reviewing us"})
        else:
            return jsonify({"status": "error", "message": "Somthing wrong try again!"})
    except Exception as e:
        return jsonify({"status": "error", "message": "Server error try again!"})


# Verification ============
@user.route("/verification", methods=["GET", "POST"])
@is_auth
@is_verified
@is_user
@is_active
def verification():
    try:
        data = CRUD("verifications").where(user_id=auth_data().get("data").get("id"))
        return render_template("/users/verification.html", data=data)
    except Exception as e:
        flash("An error occurred. Please try again", "error")
        return render_template("/users/verification.html", data={})


# ajax
@user.route("/servicesget", methods=["POST"])
@is_auth
@is_verified
@is_user
@is_active
def servicesget():
    try:
        return jsonify(
            {
                "status": "success",
                "data": CRUD("services").notwhere(
                    price=0, selling_price=0, status="off"
                ),
            }
        )
    except Exception as e:
        return jsonify(
            {"status": "error", "message": "Server error. Please try again later!"}
        )


# servers ajax ===========
@user.route("/serverget", methods=["POSt"])
def serverget():
    try:
        model = CRUD("servers")
        data = model.where(
            status="on",
        )
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify(
            {"status": "error", "message": "Server error. Please try again later!"}
        )


# valid server id ajx ======
@user.route("/validserver", methods=["POST"])
def validserver():
    try:
        server_id = request.json.get("server_id")
        model = CRUD("servers")
        server = model.where(status="on", id=server_id)
        if server and server.get("data"):
            return jsonify({"status": "success", "message": "Valid server"})
        else:
            return jsonify({"status": "error", "message": "Invalid server"})
    except Exception as e:
        return jsonify(
            {"status": "error", "message": "Server error. Please try again later!"}
        )
