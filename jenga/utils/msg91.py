import urllib
import urllib.request
import urllib.parse

from jenga import app


class sendmessage:
    """
    MSG91 class to send sms with a payload
    """

    @staticmethod
    def send_sms(mobile, message):
        authkey = app.config.get("MSG91_BASE_KEY")
        route = "4"
        sender = "Tinkerhub"
        mobiles = mobile
        # Prepare you post parameters
        values = {
            "authkey": authkey,
            "mobiles": mobiles,
            "message": message,
            "sender": sender,
            "route": route,
            "country": 91,
        }
        url = "http://api.msg91.com/api/sendhttp.php"  # API URL
        postdata = urllib.parse.urlencode(values)  # URL encoding the data here.
        postdata = postdata.encode("utf-8")
        req = urllib.request.Request(url, postdata)
        response = urllib.request.urlopen(req)
        output = response.read()  # Get Response
        return output
