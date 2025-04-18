from flask import (
    Blueprint,
    jsonify,
    url_for,
    redirect,
    request,
    render_template,
)
import stripe
import paypalrestsdk
from dotenv import load_dotenv
import os
from app.helpers.middleware import is_auth, is_verified, is_user, is_active
from app.helpers.authdata import auth_data
from app.utils.table import CRUD

pay = Blueprint("pay", __name__)

load_dotenv()

# stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
BASE_HOST_URL = os.getenv("APP_URL")

# PayPal SDK Configuration
paypalrestsdk.configure(
    {
        #'sandbox'
        "mode": "live",
        "client_id": os.getenv("PAYPAL_CLIENT_ID"),
        "client_secret": os.getenv("PAYPAL_SECRET"),
    }
)


@pay.route("session", methods=["POST"])
@is_auth
@is_verified
@is_user
@is_active
def create_payment_session():
    data = request.json
    gateway = data.get("gateway")
    amount = data.get("amount")
    currency = data.get("currency", "usd")

    if gateway == "stripe":
        return create_stripe_session(amount, currency)

    elif gateway == "paypal":
        return create_paypal_order(amount, currency)

    return jsonify({"error": "Invalid payment gateway"}), 400


@pay.route("/success", methods=["GET"])
@is_auth
@is_verified
@is_user
@is_active
def success():
    gateway = request.args.get("gateway")
    order_id = request.args.get("order_id")

    if gateway == "stripe":
        session_id = request.args.get("session_id")
        session = stripe.checkout.Session.retrieve(session_id)

        payment_status = session.get("payment_status")
        amount_total = session.get("amount_total", 0) / 100
        currency = session.get("currency").upper()
        payment_in = session.get("payment_intent")

        # store
        model = CRUD("transactions")
        existing_list = model.count(pay_id=payment_in)

        user_name = auth_data().get("data").get("name")
        user_id = auth_data().get("data").get("id")
        if existing_list.get("status") == "success" and existing_list.get("data") <= 0:
            store = model.create(
                user_name=user_name,
                user_id=user_id,
                amount=amount_total,
                type=gateway,
                type_details="Pay by " + gateway,
                status=payment_status,
                pay_id=payment_in,
            )
            user_model = CRUD("users")
            new_coin = auth_data().get("data").get("coin") + float(amount_total)
            user_model.update(auth_data().get("data").get("id"), coin=new_coin)
        else:
            return redirect(url_for("user.creadits"))

        return render_template(
            "pay/success.html",
            data={
                "message": "Payment successful",
                "payment_status": payment_status,
                "amount_total": amount_total,
                "currency": currency,
            },
        )

    if gateway == "paypal" and order_id:
        order = paypalrestsdk.Payment.find(order_id)
        payment_status = order.state
        amount_total = float(order.transactions[0].amount.total)
        currency = order.transactions[0].amount.currency
        payment_in = order.id

        model = CRUD("transactions")
        existing_list = model.where(py_id=payment_in)
        if existing_list.get("status") != "success":
            model.create(
                user_name=auth_data().get("data").get("name"),
                user_id=auth_data().get("data").get("id"),
                amount=amount_total,
                type=gateway,
                type_details="Pay by " + gateway,
                status=payment_status,
                py_id=payment_in,
            )
            user_model = CRUD("users")
            new_coin = auth_data().get("data").get("coin") + float(amount_total)
            user_model.update(auth_data().get("data").get("id"), coin=new_coin)
        else:
            return redirect(url_for("user.creadits"))

        # Step 4: Render success page
        return render_template(
            "pay/success.html",
            data={
                "message": "Payment successful",
                "payment_status": payment_status,
                "amount_total": amount_total,
                "currency": currency,
            },
        )


@pay.route("/cancel")
@is_auth
@is_verified
@is_user
@is_active
def cancel():
    return render_template("pay/failed.html")


# stripe function
def create_stripe_session(amount, currency):
    try:
        # Validate and convert amount to cents
        amount_in_cents = int(float(amount) * 100)

        # Create a Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": currency.lower(),
                        "product_data": {
                            "name": "Token",
                        },
                        "unit_amount": amount_in_cents,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=f"{BASE_HOST_URL}"
            + "?session_id={CHECKOUT_SESSION_ID}&gateway=stripe",
            cancel_url=f"{BASE_HOST_URL}",
        )
        return jsonify({"id": session.id})
    except ValueError:
        # Handle invalid amount
        return jsonify({"error": "Invalid amount provided."}), 400
    except stripe.error.StripeError as e:
        # Handle Stripe-specific errors
        return jsonify({"error": str(e.user_message or e)}), 500
    except Exception as e:
        # Handle other exceptions
        return jsonify({"error": str(e)}), 500


# paypal function using paypalrestsdk
def create_paypal_order(amount, currency):
    try:
        amount = float(amount)

        # Create payment
        payment = paypalrestsdk.Payment(
            {
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "transactions": [
                    {
                        "amount": {
                            "total": f"{amount:.2f}",  # Ensure value is in proper decimal format
                            "currency": currency.upper(),
                        },
                        "description": "Payment for your purchase",
                    }
                ],
                "redirect_urls": {
                    "return_url": f"{BASE_HOST_URL}" + "?gateway=paypal",
                    "cancel_url": f"{BASE_HOST_URL}",
                },
            }
        )

        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    return jsonify({"approval_url": approval_url})
        else:
            return jsonify({"error": "Failed to create PayPal payment"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
