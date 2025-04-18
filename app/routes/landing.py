from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    session,
    g,
)
from app.utils.table import CRUD
from app.helpers.helpers import is_email
from app.helpers.middleware import is_auth, is_guest, is_already_verified, is_not_block
from app.helpers.authdata import auth_data
from app.mail.forget import forget_mail
from app.mail.verify import verify_email
import random
from werkzeug.security import generate_password_hash, check_password_hash


landing = Blueprint("landing", __name__, template_folder="templates")


# all landing routes
@landing.route("/")
def dashboard():
    return render_template(
        "/landing/home.html",
        data=CRUD("reviews").where(feture="on"),
        total_services=CRUD("services").count(),
    )


@landing.route("/about")
def about():
    return render_template("/landing/about.html",data=CRUD("reviews").where(feture="on"))


@landing.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        fname = request.form.get("f_name")
        lname = request.form.get("l_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")

        if not fname or not lname or not email or not message:
            flash("All fields are required. Please fill out all the fields.", "error")
            return redirect(url_for("landing.contact"))

        model = CRUD("supports")
        fullname = f"{fname} {lname}"
        create = model.create(name=fullname, email=email, phone=phone, message=message)
        if create:
            flash(
                "Your request has been received by the admin. The admin will reply to you soon.",
                "success",
            )
            return redirect(url_for("landing.contact"))
        else:
            flash("Server erro try again.", "error")
            return redirect(url_for("landing.contact"))
    return render_template("/landing/contact.html")


@landing.route("/signup", methods=["GET", "POST"])
@is_guest
def signup():
    try:
        if request.method == "POST":
            from app import db

            user_crud = CRUD("users")
            username = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")
            hashed_password = generate_password_hash(password)

            if not (username and email and password):
                flash("Please fill all the fields", "error")
                return render_template("/landing/signup.html")

            if not is_email(email):
                flash("Invalid email", "error")
                return render_template("/landing/signup.html")

            if len(password) < 8:
                flash("Password must be at least 8 characters long", "error")
                return render_template("/landing/signup.html")

            existing = user_crud.exists("email", email)
            if existing.get("status") == "success" and existing.get("data"):
                flash("Email already exists", "error")
                return render_template("/landing/signup.html")

            veryfcode = "".join([str(random.randint(0, 9)) for _ in range(6)])
            create = user_crud.create(
                name=username,
                email=email,
                password=hashed_password,
                verify_code=veryfcode,
                avatar=f"https://avatar.iran.liara.run/public/boy?username={username}",
            )

            if create.get("status") == "success":
                html = verify_email(veryfcode)
                sender = g.send_email(
                    "Your Email Confirmation Code",
                    email,
                    html,
                )
                if sender:
                    session["user_id"] = create.get("data")
                    flash(
                        "Account created successfully. A verification code has been sent to your inbox.",
                        "success",
                    )
                    return redirect(url_for("landing.verify"))
                else:
                    flash("Failed to send verification code", "error")
                    return redirect(url_for("landing.verify"))
            else:
                flash("Failed to create account", "error")
                return render_template("/landing/signup.html")
        else:
            return render_template("/landing/signup.html")
    except Exception:
        flash("An error occurred. Please try again", "error")
        return render_template("/landing/signup.html")


@landing.route("/signin", methods=["GET", "POST"])
@is_guest
def signin():
    if request.method == "POST":
        try:
            db_user = CRUD("users")
            email = request.form.get("email")
            password = request.form.get("password")

            # validation
            if not email or not password:
                flash("Please fill all the fields", "error")
                return render_template("/landing/signin.html")

            if not is_email(email):
                flash("Invalid email", "error")
                return render_template("/landing/signin.html")

            if len(password) < 8:
                flash("Password must be at least 8 characters long", "error")
                return render_template("/landing/signin.html")

            user = db_user.get_by_column("email", email).get("data")
            if user:
                if check_password_hash(user.get("password"), password):
                    session["user_id"] = user.get("id")
                    if user.get("email_verify") == "no":
                        flash("Please verify your email to continue", "error")
                        return redirect(url_for("landing.verify"))
                    flash("Login successful", "success")
                    if auth_data().get("role") == "user":
                        return redirect(url_for("user.dashboard"))
                    else:
                        return redirect(url_for("admin.dashboard"))
                else:
                    flash("Invalid email or password", "error")
                    return render_template("/landing/signin.html")
            else:
                flash("User not found", "error")
                return render_template("/landing/signin.html")
        except Exception:
            flash("An error occurred. Please try again", "error")
            return render_template("/landing/signin.html")
    else:
        return render_template("/landing/signin.html")


@landing.route("/forget", methods=["GET", "POST"])
@is_guest
def forget():
    try:
        if request.method == "POST":
            email = request.form.get("email")
            if not email:
                flash("Please fill all the fields", "error")
                return render_template("/landing/forget.html")

            if not is_email(email):
                flash("Invalid email", "error")
                return render_template("/landing/forget.html")

            user = CRUD("users").get_by_column("email", email)
            if user and user.get("status") == "success" and user.get("data"):
                veryfcode = "".join([str(random.randint(0, 9)) for _ in range(6)])
                html = forget_mail(veryfcode)
                sender = g.send_email(
                    "Reset password code",
                    user.get("data").get("email"),
                    html,
                )
                if sender:
                    db_user = CRUD("users")
                    db_user.update(user.get("data").get("id"), verify_code=veryfcode)
                    flash("Password reset code sent successfully", "success")
                    return redirect(url_for("landing.reset"))
                else:
                    flash("Password reset code sent faild", "error")
                    return redirect(url_for("landing.forget"))
            else:
                flash("Invalid email", "error")
                return redirect(url_for("landing.forget"))
        else:
            return render_template("/landing/forget.html")
    except Exception as e:
        flash("An error occurred. Please try again", "erro")
        return render_template("/landing/forget.html")


@landing.route("/reset", methods=["GET", "POST"])
@is_guest
def reset():
    try:
        if request.method == "POST":
            email = request.form.get("email")
            code = request.form.get("code")
            password = request.form.get("password")
            hashed_password = generate_password_hash(password)

            # validation
            if not email or not code or not password:
                flash("Please fill all the fields", "error")
                return render_template("/landing/reset.html")

            if not is_email(email):
                flash("Invalid email", "error")
                return render_template("/landing/reset.html")

            if len(password) < 8:
                flash("Password must be at least 8 characters long", "error")
                return render_template("/landing/reset.html")

            if len(code) < 6:
                flash("OTP code must be at least 6 characters long", "error")
                return render_template("/landing/reset.html")

            db_user = CRUD("users")
            user = db_user.get_by_column("email", email).get("data")
            if user:
                if user.get("verify_code") == code:
                    db_user.update(
                        user.get("id"), password=hashed_password, verify_code=""
                    )
                    flash("Password reset was successfull", "success")
                    return redirect(url_for("landing.signin"))
                else:
                    flash("Invalid OTP code address", "error")
                    return render_template("/landing/reset.html")
            else:
                flash("Invalid credentials", "error")
                return render_template("/landing/reset.html")
        else:
            return render_template("/landing/reset.html")
    except Exception as e:
        flash("An error occurred. Please try again", "erro")
        return render_template("/landing/reset.html")


@landing.route("/verify", methods=["GET", "POST"])
@is_auth
@is_already_verified
def verify():
    try:
        db_user = CRUD("users")
        if request.method == "POST":
            code = request.form.get("code")

            # validation
            if not code:
                flash("Please fill all the fields", "error")
                return render_template("/landing/verify.html")

            user = db_user.get_by_column("id", session.get("user_id")).get("data")
            if user:
                if user.get("verify_code") == code:
                    result = db_user.update(
                        user.get("id"), email_verify="yes", verify_code=""
                    )
                    print(result)
                    flash("Email verified successfully", "success")
                    return redirect(url_for("landing.signin"))
                else:
                    flash("Invalid verification code", "error")
                    return render_template("/landing/verify.html")
            else:
                flash("User not found", "error")
                return render_template("/landing/verify.html")
        else:
            return render_template("/landing/verify.html")
    except Exception as e:
        flash("An error occurred. Please try again", "erro")
        return render_template("/landing/verify.html")


@landing.route("/resendcode")
@is_auth
@is_already_verified
def resendcode():
    try:
        user = auth_data()
        if user.get("auth"):
            veryfcode = "".join([str(random.randint(0, 9)) for _ in range(6)])
            html = verify_email(veryfcode)
            sender = g.send_email(
                "Your Email Confirmation Code",
                user.get("data").get("email"),
                html,
            )
            if sender:
                db_user = CRUD("users")
                db_user.update(user.get("data").get("id"), verify_code=veryfcode)
                flash("Verification code resent successfully", "success")
                return redirect(url_for("landing.verify"))
            else:
                flash("Failed to resend verification code", "error")
                return redirect(url_for("landing.verify"))
        else:
            flash("Please login first to your account", "error")
            session.clear()
            return redirect(url_for("landing.signin"))
    except Exception as e:
        flash("An error occurred. Please try again", "erro")
        return redirect(url_for("landing.verify"))


@landing.route("/logout")
@is_auth
def logout():
    session.pop("user_id", None)
    return redirect(url_for("landing.signin"))


@landing.route("/blocked")
@is_not_block
def blocked():
    return render_template("userbloc.html")
