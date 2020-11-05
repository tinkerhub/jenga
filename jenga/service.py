import os
import sys
from flask import Flask, session, request, flash, redirect, url_for, render_template
from dotenv import load_dotenv
from twilio.rest import Client
from deta import Deta
from airtable import Airtable
import requests
from jenga import app
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s : %(levelname)s : %(name)s : %(message)s'
)
generateotp_url = 'https://api.generateotp.com/'

load_dotenv()
twilio_client = Client()


deta = Deta(app.config.get("DETA_PROJECT_KEY"))
db = deta.Base(app.config.get("DETA_BASE"))
airtable = Airtable(app.config.get("AIRTABLE_BASE_KEY"), app.config.get("AIRTABLE_TABLE_NAME"), app.config.get("AIRTABLE_API_KEY"))
collegesTable = Airtable(app.config.get("AIRTABLE_BASE_KEY"), "Campus", app.config.get("AIRTABLE_API_KEY"))
rawcolleges = collegesTable.get_all()

def getCollegeList(raw_list):
    collegeList = [
        {
            "id": college.get("id"),
            "name": college.get("fields").get("your campus/school name")
        } for college in raw_list
    ]
    return collegeList

collegeList = getCollegeList(rawcolleges)
logging.info(collegeList)


@app.route('/', methods=["GET"])
def index_page():
    return render_template("index.html")

@app.route('/', methods=["POST"])
def generate():
    number = request.form["number"]
    logging.info(number)
    if len(number) != 10:
        logging.info("Invalid Phone number")
        flash("Invalid Phone number")
        return redirect(url_for('generate'))

    session['phone_number'] = number
    # print("session phone number set")
    # db.put({"key":number,"stage":"otp"})
    otp_code = make_otp_request(number)
    if otp_code:
        send_otp_code("+91"+number, otp_code, 'sms')
        logging.info('Otp has been generated successfully')            
        return redirect(url_for('validate'))  
        #code=307 does a POST request reference : https://stackoverflow.com/questions/15473626/make-a-post-request-while-redirecting-in-flask
    else:
        logging.info("Trouble with OTP")
        return redirect(url_for('generate'))
    # except:
    #     e = sys.exc_info()[0]
    #     print("Error :", str(e), e)
    #     return redirect(url_for('generate'))


@app.route('/validate', methods=['GET'])
def otp_page():
    return render_template('otp.html')

@app.route('/validate', methods=['POST'])
def validate():
    entered_otp = request.form["otp"]
    logging.info("entered_code : %s", entered_otp)
    if len(entered_otp) != 6:
        logging.info("Invalid OTP")
        flash("Invalid OTP")
        return redirect(url_for('validate'))

    if 'phone_number' in session:
        phone_number = session['phone_number']
        status, _ = verify_otp_code(entered_otp, phone_number)
        # db.update({"stage":"done","MembershipId":"RandomID"},key=phone_number)
        # status = True
        if status == True:
            logging.info("STATUS : %s", status)
            session["verified"] = True
            already_exists = check_if_already_member(phone_number)
            if already_exists:
                logging.info("member already exists")
                session["MembershipId"] = already_exists
                session.pop('phone_number', None)
                return render_template('exist.html')  # show exist.html with member ID
            else:
                return redirect(url_for('details'))
        else:
            logging.info("STATUS : %s" ,status)
            return redirect(url_for('validate'))
    else:
        return redirect(url_for('generate'))

@app.route('/details', methods=['GET','POST'])
def details_page():
    if "verified" in session:
        return render_template('details.html', colleges=collegeList)
    else:
        return redirect(url_for('generate'))


@app.route('/details', methods=['GET','POST'])
def details():
    if 'phone_number' not in session or 'verified' not in session:
        return redirect(url_for('generate'))

    number = session['phone_number']
    already_exists = check_if_already_member(number)
    if already_exists:
        logging.info("member already exists")
        session["MembershipId"] = already_exists
        session.pop('phone_number', None)
        return render_template('exist.html')

    data = request.form.to_dict()
    # data["AreasOfInterest"] = request.form.to_dict(flat=False)["AreasOfInterest"]  #removed this question from html
    if data["College"] == '':
        del data["College"]
    else:
        data["College"] = [data["College"]] # for some reason, Airtable requires a list of ids
    data["MobileNumber"] = int(number)
    logging.info(data)
    try:
        record = airtable.insert(data)
        logging.info(record)
        db.put({"key":number,"MembershipId":record["id"]})
        session["MembershipId"] = record["id"]
        session.pop('phone_number', None)
        session.pop('verified', None)
        return render_template('sucess.html')
    except:
        e = sys.exc_info()[0]
        logging.info("Error : %s", str(e))
        return redirect(url_for('details'))

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
    r = requests.post(f"{generateotp_url}/generate",
                      data={'initiator_id': phone_number})
    if r.status_code == 201:
        data = r.json()
        otp_code = str(data["code"])
        return otp_code

def send_otp_code(phone_number, otp_code, channel):
    _ = twilio_client.messages.create(to=f"{phone_number}", from_=os.getenv(
        'TWILIO_NUMBER'), body=f"Welcome to TinkerHub! Your one time password is {otp_code}")

def split_code(code):
    return " ".join(code)
