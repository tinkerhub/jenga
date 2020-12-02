import os
import sys
from flask import (
    request,
    redirect,
    jsonify,
)
from dotenv import load_dotenv
from twilio.rest import Client
from deta import Deta
from airtable import Airtable
import requests
from jenga import app

## jwt utility tools
from jenga.jwt.encode import jenga_jwt_encoder
from jenga.jwt.decorator import token_required

# error handler
from jenga.error import InvalidUsage
import logging


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s : %(levelname)s : %(name)s : %(message)s"
)
generateotp_url = "https://api.generateotp.com/"

load_dotenv()
twilio_client = Client()

"""
    deta and airtable configurations
"""
deta = Deta(app.config.get("DETA_PROJECT_KEY"))
db = deta.Base(app.config.get("DETA_BASE"))
airtable = Airtable(
    app.config.get("AIRTABLE_BASE_KEY"),
    app.config.get("AIRTABLE_TABLE_NAME"),
    app.config.get("AIRTABLE_API_KEY"),
)
collegesTable = Airtable(
    app.config.get("AIRTABLE_BASE_KEY"), "Campus", app.config.get("AIRTABLE_API_KEY")
)

"""
    App Routes
"""


@app.route("/", methods=["POST"])
def generate():
    """
    inputs a mobile number as JSON key
    generates an OTP
    sends to the given mobile number
    """
    number = request.json["number"]
    logging.info(number)
    if len(number) != 10:
        logging.info("Invalid Phone number")
        raise InvalidUsage("Invalid Phone number", status_code=417)

    # print("session phone number set")
    # db.put({"key":number,"stage":"otp"})
    otp_code = make_otp_request(number)
    if otp_code:
        send_otp_code("+91" + number, otp_code, "sms")
        logging.info(otp_code)
        logging.info("Otp has been generated successfully")
        token = jenga_jwt_encoder(number=number)
        return {
            "message": "Otp has been send. Check your number",
            "token": token.decode("UTF-8"),
        }
        # code=307 does a POST request reference : https://stackoverflow.com/questions/15473626/make-a-post-request-while-redirecting-in-flask
    else:
        logging.info("Trouble with OTP")
        raise InvalidUsage("OTP send failed", status_code=417)
    # except:
    #     e = sys.exc_info()[0]
    #     print("Error :", str(e), e)
    #     return redirect(url_for('generate'))


@app.route("/user", methods=["GET"])
@token_required
def get_auth_status(user):
    """
    returns user information of status
    number, verified, memberShipID
    """
    return jsonify(user)


@app.route("/validate", methods=["POST"])
@token_required
def validate(user):
    """
    to validate an OTP send via GET: /
    checks validity of the OTP
    on verified checks number exist if it does sends back the membershipID
    else sends the new token
    """
    entered_otp = request.json["otp"]
    logging.info("entered_code : %s", entered_otp)
    if len(entered_otp) != 6:
        logging.info("Invalid OTP")
        raise InvalidUsage("Invalid OTP", status_code=417)

    if user.get("number") is not None:
        phone_number = user["number"]
        status, _ = verify_otp_code(entered_otp, phone_number)
        # db.update({"stage":"done","MembershipId":"RandomID"},key=phone_number)
        # status = True
        if status is True:
            logging.info("STATUS : %s", status)
            already_exists = check_if_already_member(phone_number)
            if already_exists:
                logging.info("member already exists")
                new_token = jenga_jwt_encoder(
                    verified=True, memberShipID=already_exists
                )
                raise InvalidUsage(
                    "user already exist",
                    status_code=419,
                    payload={
                        "memberShipID": already_exists,
                        "token": new_token.decode("UTF-8"),
                    },
                )
            else:
                new_token = jenga_jwt_encoder(number=phone_number, verified=True)
                return {
                    "message": "successfully signed up",
                    "token": new_token.decode("UTF-8"),
                }
        else:
            logging.info("STATUS : %s", status)
            raise InvalidUsage("status failed", status_code=417)
    else:
        raise InvalidUsage("Time expired, retry again", status_code=404)


@app.route("/colleges", methods=["GET"])
@token_required
def get_college_list():
    """
    get all colleges saved in DB from deta
    """
    raw_college_list = collegesTable.get_all()
    collegeList = [
        {
            "id": college.get("id"),
            "name": college.get("fields").get("Your campus/ school name"),
        }
        for college in raw_college_list
    ]
    return jsonify(collegeList)


@app.route("/details", methods=["POST"])
@token_required
def details(user):
    """
    user form registration
    accepts various details of user like college etc
    saves it to deta and airtable
    returns membershipid and token
    """
    number = user.get("number")
    if number is None or user.get("verified") is None:
        raise InvalidUsage("Unauthorized access", status_code=401)

    already_exists = check_if_already_member(number)
    if already_exists:
        logging.info("member already exists")
        new_token = jenga_jwt_encoder(memberShipID=already_exists, verified=True)
        raise InvalidUsage(
            "user already exist",
            status_code=419,
            payload={"memberID": already_exists, "payload": new_token},
        )

    data = request.get_json()
    # data["AreasOfInterest"] = request.form.to_dict(flat=False)["AreasOfInterest"]  #removed this question from html
    if data["College"] == "":
        del data["College"]
    else:
        data["College"] = [
            data["College"]
        ]  # for some reason, Airtable requires a list of ids
    data["MobileNumber"] = int(number)
    logging.info(data)
    try:
        record = airtable.insert(data)
        logging.info(record)
        db.put({"key": number, "MembershipId": record["id"]})
        new_token = jenga_jwt_encoder(memberShipID=record["id"], verified=True)
        return {
            "message": "Successfully registered",
            "memberShipID": record["id"],
            "token": new_token,
        }
    except requests.HTTPError as exception:
        e = sys.exc_info()[0]
        logging.info("Error : %s", str(e))
        print(exception)
        raise InvalidUsage(str(e), status_code=417)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """
    error handler to fire all errors from flask
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


"""
    App Utility functions
"""


def check_if_already_member(phone_number):
    member = db.get(phone_number)
    if member:
        if "MembershipId" in member:
            return member["MembershipId"]
    return False


def verify_otp_code(otp_code, phone_number):
    r = requests.post(f"{generateotp_url}/validate/{otp_code}/{phone_number}")
    if r.status_code == 200:
        data = r.json()
        status = data["status"]
        message = data["message"]
        return status, message
    return None, None


def make_otp_request(phone_number):
    r = requests.post(
        f"{generateotp_url}/generate", data={"initiator_id": phone_number}
    )
    if r.status_code == 201:
        data = r.json()
        otp_code = str(data["code"])
        return otp_code


def send_otp_code(phone_number, otp_code, channel):
    _ = twilio_client.messages.create(
        to=f"{phone_number}",
        from_=os.getenv("TWILIO_NUMBER"),
        body=f"Welcome to TinkerHub! Your one time password is {otp_code}",
    )


def split_code(code):
    return " ".join(code)
