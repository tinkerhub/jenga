import requests
from twilio.rest import Client
from .msg91 import sendmessage


class OTP:
    """
    OTP Controlling Class
    Uses the free service generateotp.com
    - Verification - Generation
    """

    def __init__(self, account_key, token_key, from_number):
        self.url = "https://api.generateotp.com"
        self.twilio = Client(account_key, token_key)
        self.from_number = from_number

    def generate_otp(self, phone_number):
        r = requests.post(f"{self.url}/generate", data={"initiator_id": phone_number})
        if r.status_code == 201:
            data = r.json()
            otp_code = str(data["code"])
            return otp_code

    def verify_otp(self, otp_code, phone_number):
        r = requests.post(f"{self.url}/validate/{otp_code}/{phone_number}")
        if r.status_code == 200:
            data = r.json()
            status = data["status"]
            message = data["message"]
            return status, message
        return None, None

    def send_otp_sms(self, otp_code, phone_number):
        _ = self.twilio.messages.create(
            to=phone_number,
            from_=self.from_number,
            body=f"Welcome to TinkerHub! Your one time password is {otp_code}",
        )
        # _ = sendmessage.send_sms(
        #     mobile=phone_number,
        #     message=f"Welcome to TinkerHub! Your one time password is {otp_code}",
        # )
