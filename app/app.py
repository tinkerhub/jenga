import os
import sys
from flask import Flask, session, request, flash, redirect, url_for, render_template
from dotenv import load_dotenv
from twilio.rest import Client
from deta import Deta
from airtable import Airtable
import requests
load_dotenv()
app = Flask(__name__, static_folder="static")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
app.secret_key = FLASK_SECRET_KEY
twilio_client = Client()

DETA_PROJECT_KEY = os.getenv("DETA_PROJECT_KEY")
DETA_BASE = os.getenv("DETA_BASE")
deta = Deta(DETA_PROJECT_KEY)
db = deta.Base(DETA_BASE)

AIRTABLE_BASE_KEY = os.getenv("AIRTABLE_BASE_KEY")
AIRTABLE_TABLE_NAME = "Members"
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
airtable = Airtable(AIRTABLE_BASE_KEY, AIRTABLE_TABLE_NAME, AIRTABLE_API_KEY)
collegesTable = Airtable(AIRTABLE_BASE_KEY, "Campus", AIRTABLE_API_KEY)
rawcolleges = collegesTable.get_all()
collegeList = []
for college in rawcolleges:
    c = {'id':college['id'],
         'name':college['fields']['Your campus/ school name']}
    collegeList.append(c)
print(collegeList)

generateotp_url = 'https://api.generateotp.com/'

@app.route('/', methods=['GET', 'POST'])
def generate():
    if request.method == 'GET':
        return render_template('index.html')
    
    if request.method == 'POST':
        number = request.form["number"]
        print(number)
        if len(number) != 10:
            print("Invalid Phone number")
            flash("Invalid Phone number")
            return redirect(url_for('generate'))
        session['phone_number'] = number
        # print("session phone number set")
        # db.put({"key":number,"stage":"otp"})
        otp_code = make_otp_request(number)
        if otp_code:
            send_otp_code("+91"+number, otp_code, 'sms')
            print('Otp has been generated successfully', 'success')            
            return redirect(url_for('validate'))  #code=307 does a POST request reference : https://stackoverflow.com/questions/15473626/make-a-post-request-while-redirecting-in-flask
        else:
            print("Trouble with OTP")
            return redirect(url_for('generate'))
        # except:
        #     e = sys.exc_info()[0]
        #     print("Error :", str(e), e)
        #     return redirect(url_for('generate'))

@app.route('/validate', methods=['GET', 'POST'])
def validate():
    if request.method == 'GET':
        return render_template('otp.html')
    if request.method == 'POST':
        entered_otp = request.form["otp"]
        print("entered_code :", entered_otp)
        if len(entered_otp) != 6:
            print("Invalid OTP")
            flash("Invalid OTP")
            return redirect(url_for('validate'))

        if 'phone_number' in session:
            phone_number = session['phone_number']
            status, message = verify_otp_code(entered_otp, phone_number)
            # db.update({"stage":"done","MembershipId":"RandomID"},key=phone_number)
            # status = True
            if status == True:
                print("STATUS : ",status)
                session["verified"] = True
                already_exists = check_if_already_member(phone_number)
                if already_exists:
                    print("member already exists")
                    session["MembershipId"] = already_exists
                    session.pop('phone_number', None)
                    return render_template('exist.html')  # show exist.html with member ID
                else:
                    return redirect(url_for('details'))
            if status == False:
                print("STATUS : ",status)
                return redirect(url_for('validate'))
        else:
            return redirect(url_for('generate'))

@app.route('/details', methods=['GET','POST'])
def details():
    if request.method == 'GET':
        if "verified" in session:
            return render_template('details.html', colleges=collegeList)
        else:
            return redirect(url_for('generate'))

    if request.method == 'POST':
        if 'phone_number' not in session or 'verified' not in session:
            return redirect(url_for('generate'))

        number = session['phone_number']
        already_exists = check_if_already_member(number)
        if already_exists:
            print("member already exists")
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
        print(data)
        try:
            record = airtable.insert(data)
            print(record)
            db.put({"key":number,"MembershipId":record["id"]})
            session["MembershipId"] = record["id"]
            session.pop('phone_number', None)
            session.pop('verified', None)
            return render_template('sucess.html')
        except:
            e = sys.exc_info()[0]
            print("Error :", str(e))
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
    messages = twilio_client.messages.create(to=f"{phone_number}", from_=os.getenv(
        'TWILIO_NUMBER'), body=f"Welcome to TinkerHub! Your one time password is {otp_code}")

def split_code(code):
    return " ".join(code)

if __name__ == '__main__':
    app.run()