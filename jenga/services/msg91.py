import http
from jenga import app
import json


class sendmessage:
    """
    MSG91 class to send sms with a payload
    """

    @staticmethod
    def send_otp(mobile):
        mobile = "+91" + mobile
        authkey = app.config.get("MSG91_BASE_KEY")
        template_id = app.config.get("MSG91_TEMPLATE_ID")
        # Prepare you post parameters
        conn = http.client.HTTPSConnection("api.msg91.com")
        headers = {"content-type": "application/json"}

        conn.request(
            "GET",
            f"/api/v5/otp?template_id={template_id}&mobile={mobile}&authkey={authkey}",
            "",
            headers,
        )
        res = conn.getresponse()
        data = res.read()
        print(f"-------------{mobile}------------------")
        data = data.decode("utf-8")
        print(data)
        return data

    @staticmethod
    def verify_otp(mobile, otp):
        mobile = "+91" + mobile
        authkey = app.config.get("MSG91_BASE_KEY")
        conn = http.client.HTTPSConnection("api.msg91.com")
        conn.request(
            "GET", f"/api/v5/otp/verify?authkey={authkey}&mobile={mobile}&otp={otp}"
        )
        print(f"-------------{mobile}------------------")
        res = conn.getresponse()
        data = res.read()

        data = data.decode("utf-8")
        success = "error" not in data
        print(data)
        return success

    @staticmethod
    def retry_otp(mobile, type):
        mobile = "+91" + mobile
        authkey = app.config.get("MSG91_BASE_KEY")
        conn = http.client.HTTPSConnection("api.msg91.com")
        conn.request(
            "GET",
            f"/api/v5/otp/retry?authkey={authkey}&retrytype={type}&mobile={mobile}",
        )
        res = conn.getresponse()
        data = res.read()
        data = json.loads(data.decode("utf-8"))
        return data
