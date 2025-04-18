from flask import Blueprint, jsonify, request
import requests
from app.helpers.middleware import is_active, is_auth, is_verified, is_user, is_admin
from app.helpers.authdata import auth_data
from app.utils.table import CRUD
from dotenv import load_dotenv
import os

api = Blueprint("api", __name__)
load_dotenv()

# load environment variales
BASE_URL = os.getenv("BASE_URL")


# genaret bearer token
def generate_bearer_token(server):
    headers = {"X-API-KEY": server.get("api"), "X-API-USERNAME": server.get("email")}
    try:
        response = requests.post(f"{BASE_URL}/api/pub/v2/auth", headers=headers)
        response.raise_for_status()

        token_data = response.json()
        return token_data.get("token")  # Return the fresh token
    except requests.exceptions.RequestException as e:
        print(f"Error generating token: {e}")
        return None


# this function for request api
def make_api_request(
    server, endpoint, method="GET", data=None, params=None, urltype=None
):
    token = generate_bearer_token(server)
    if not token:
        return {"error": "Failed to generate token"}

    # Ensure the endpoint is correctly formatted
    if urltype == True:
        url = endpoint
    else:
        url = f"{BASE_URL}{endpoint}"

    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Debug: Log the final URL
        print(f"Making API request to: {url}")

        # Make the API call with the new token
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            return {"error": f"Unsupported HTTP method: {method}"}

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return {"error": f"API request failed: {str(e)}"}


# create verification route
@api.route("/createverification", methods=["POST"])
@is_auth
@is_verified
@is_user
@is_active
def createverification():
    try:
        model = CRUD("verifications")
        user_id = auth_data().get("data").get("id")

        # validate data
        service_id = request.json.get("service_id")
        server_id = request.json.get("server_id")
        if not all([service_id, server_id]):
            return jsonify({"status": "error", "message": "All fields are required"})

        # validate service id
        service = CRUD("services").where(id=service_id, status="on")
        if not service or not service.get("data"):
            return jsonify({"status": "error", "message": "Invalid service ID"})
        service_data = service.get("data")[0]

        # check is valid server or not
        server = CRUD("servers").get_by_column("id", server_id)
        server_data = {}
        if server.get("status") == "success":
            if not server.get("data").get("api") or not server.get("data").get("email"):
                return jsonify(
                    {
                        "status": "error",
                        "message": "Server error. Please contact with admin",
                    }
                )
            else:
                server_data = server.get("data")
        else:
            return jsonify(
                {"status": "error", "message": "Server error. Please try again later!"}
            )

        # check already runing any services
        check = model.where(user_id=user_id, status="pending")
        if check and check.get("data"):
            return jsonify(
                {
                    "status": "error",
                    "message": "You already have a pending verification",
                }
            )

        # cehck balance
        service_price = (
            service_data.get("selling_price")
            if service_data.get("selling_price")
            else service_data.get("price")
        )
        if service_price > auth_data().get("data").get("coin"):
            return jsonify(
                {
                    "status": "error",
                    "message": "Insufficient balance. Please recharge your account. <a href='/user/creadits' class='underline'>Deposit</a>",
                }
            )

        # Prepare the body for the verification request
        body = {
            "areaCodeSelectOption": service_data.get("areaCodeSelectOption", []),
            "carrierSelectOption": service_data.get("carrierSelectOption", []),
            "serviceName": service_data.get("service", ""),
            "capability": service_data.get("capacity", ""),
            "serviceNotListedName": service_data.get("serviceNotListedName", ""),
        }
        result = make_api_request(
            server_data, "/api/pub/v2/verifications", method="POST", data=body
        )
        if result:
            verification_id = (
                result.get("href", "").split("/")[-1] if result.get("href") else None
            )
            endpoint = f"/api/pub/v2/verifications/{verification_id}"
            polling_data = make_api_request(server_data, endpoint, method="GET")
            if polling_data:
                store = model.create(
                    service_id=service_id,
                    user_id=user_id,
                    service_name=service_data.get("service"),
                    price=service_price,
                    server_id=server_id,
                    service_token=verification_id,
                    number=polling_data.get("number"),
                    created_at=polling_data.get("createdAt"),
                    endsAt=polling_data.get("endsAt"),
                )
                if store.get("status") == "success":
                    # update user balance
                    new_balance = auth_data().get("data").get("coin") - service_price
                    CRUD("users").update(
                        auth_data().get("data").get("id"), coin=new_balance
                    )
                    return jsonify(
                        {
                            "status": "success",
                            "message": "Verification created successfully",
                            "data": model.get_by_column("id", store.get("data")).get(
                                "data"
                            ),
                        }
                    )
                else:
                    return jsonify(
                        {
                            "status": "error",
                            "message": "Failed to create verification. Please try again!",
                        }
                    )
            else:
                return jsonify(
                    {
                        "status": "error",
                        "message": "Failed to create verification. Please try again!",
                    }
                )
        else:
            return jsonify(
                {
                    "status": "error",
                    "message": "Failed to create verification. Please try again!",
                }
            )
    except Exception as e:
        return jsonify(
            {"status": "error", "message": "Server error. Please try again later!"}
        )


# get otp
@api.route("/otp", methods=["POST"])
@is_auth
@is_verified
@is_user
@is_active
def otp():
    try:
        id = request.json.get("id")
        if not id:
            return jsonify(
                {"status": "error", "message": "Server error. Please try again later!"}
            )

        model = CRUD("verifications").get_by_column("id", id).get("data")
        if model:
            # check is valid server or not
            server = CRUD("servers").get_by_column("id", model.get("server_id"))
            server_data = {}
            if server.get("status") == "success":
                if not server.get("data").get("api") or not server.get("data").get(
                    "email"
                ):
                    return jsonify(
                        {
                            "status": "error",
                            "message": "Server error. Please contact with admin",
                        }
                    )
                else:
                    server_data = server.get("data")
            else:
                return jsonify(
                    {
                        "status": "error",
                        "message": "Server error. Please try again later!",
                    }
                )

            endpoint = f"/api/pub/v2/sms?ReservationId={model.get('service_token')}"
            otpdata = make_api_request(server_data, endpoint, method="GET")
            if otpdata.get("data")[0]:
                CRUD("verifications").update(
                    id,
                    opt=otpdata.get("data")[0].get("parsedCode"),
                    status="complete",
                    sms=otpdata.get("data")[0].get("smsContent"),
                )
                return jsonify(CRUD("verifications").get_by_column("id", id))
        else:
            return jsonify(
                {"status": "error", "message": "Server error. Please try again later!"}
            )
    except Exception as e:
        return jsonify(
            {"status": "error", "message": "Server error. Please try again later!"}
        )


# cancal
@api.route("/cancel", methods=["POST"])
@is_auth
@is_verified
@is_user
@is_active
def cancel():
    try:
        model = CRUD("verifications")
        id = request.json.get("id")
        if not id:
            return jsonify(
                {"status": "error", "message": "Server error. Please try again later!"}
            )

        v_data = model.get_by_column("id", id).get("data")
        if v_data:
            # check is valid server or not
            server = CRUD("servers").get_by_column("id", v_data.get("server_id"))
            server_data = {}
            if server.get("status") == "success":
                if not server.get("data").get("api") or not server.get("data").get(
                    "email"
                ):
                    return jsonify(
                        {
                            "status": "error",
                            "message": "Server error. Please contact with admin",
                        }
                    )
                else:
                    server_data = server.get("data")
            else:
                return jsonify(
                    {
                        "status": "error",
                        "message": "Server error. Please try again later!",
                    }
                )

            endpoint = f"/api/pub/v2/verifications/{v_data.get('service_token')}/cancel"
            res_data = make_api_request(server_data, endpoint, method="POST")
            if res_data:
                CRUD("verifications").update(
                    id,
                    status="cancel",
                )
                new_balance = auth_data().get("data").get("coin") + v_data.get("price")
                CRUD("users").update(
                    auth_data().get("data").get("id"), coin=new_balance
                )
                return jsonify(
                    {
                        "status": "success",
                        "message": "Cancellation was successful",
                        "data": CRUD("verifications").get_by_column("id", id),
                    }
                )
    except Exception as e:
        return jsonify(
            {"status": "error", "message": "Server error. Please try again later!"}
        )


# get data
@api.route("getdata", methods=["POST"])
@is_auth
@is_verified
@is_user
@is_active
def getdata():
    try:
        model = CRUD("verifications")
        id = request.json.get("id")
        if not id:
            return jsonify(
                {
                    "status": "error",
                    "message": "Something wrong. Try again! Or reload the page.",
                }
            )
        else:
            return jsonify(
                {"status": "success", "data": model.get_by_column("id", id).get("data")}
            )

    except Exception as e:
        return jsonify(
            {"status": "error", "message": "Server error. Please try again later!"}
        )


# timeout
@api.route("/timeout", methods=["POST"])
@is_auth
@is_verified
@is_user
@is_active
def timeout():
    try:
        id = request.json.get("id")
        model = CRUD("verifications").update(id, status="timeout")
        if model:
            return jsonify(
                {"status": "success", "message": "Ops! your service are timeout"}
            )
    except Exception as e:
        return jsonify({"status": "error", "message": "Server error"})


# get server detals
@api.route("/serverdetails", methods=["POST"])
@is_auth
@is_verified
@is_admin
@is_active
def serverdetails():
    try:
        server_id = request.json.get("id")
        if not server_id:
            return jsonify({"status": "error", "message": "Server ID is required"})

        # check is valid server or not
        server = CRUD("servers").get_by_column("id", server_id)
        server_data = {}
        if server.get("status") == "success":
            if not server.get("data").get("api") or not server.get("data").get("email"):
                return jsonify(
                    {
                        "status": "error",
                        "message": "Server error. Please contact with admin",
                    }
                )
            else:
                server_data = server.get("data")
        else:
            return jsonify(
                {
                    "status": "error",
                    "message": "Server error. Please try again later!",
                }
            )

        endpoint = f"/api/pub/v2/account/me"
        res_data = make_api_request(server_data, endpoint, method="GET")
        if res_data:
            return jsonify(
                {
                    "status": "success",
                    "data": res_data,
                }
            )
        else:
            return jsonify(
                {
                    "status": "error",
                    "message": "Server error. Please try again later!",
                }
            )
    except Exception as e:
        return jsonify({"status": "error", "message": "Server error try again!"})


# get price
@api.route("/price", methods=["POST"])
def price():
    try:
        model = CRUD("services")
        id = request.json.get("id")
        if not id:
            return jsonify(
                {"status": "error", "message": "Server error. Please try again later!"}
            )

        v_data = model.get_by_column("id", id).get("data")
        if v_data:
            # check is valid server or not
            server = CRUD("servers").first().get("data")
            endpoint = f"/api/pub/v2/pricing/verifications"
            body = {
                "serviceName": v_data.get("service"),
                "areaCode": True,
                "carrier": True,
                "numberType": "mobile",
                "capability": "sms",
            }
            res_data = make_api_request(server, endpoint, method="POST", data=body)
            if res_data:
                model.update(id, price=res_data.get("price"))
                return jsonify(
                    {
                        "status": "success",
                        "data": res_data.get("price"),
                        "old": model.get_by_column("id", id),
                    }
                )
    except Exception as e:
        return jsonify(
            {"status": "error", "message": "Server error. Please try again later!"}
        )
