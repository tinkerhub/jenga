from jenga import app
from functools import wraps
from flask import request, jsonify
import jwt


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        """
        checks for Bearer Token in coming routes
        parses the token
        get the payload and save as first argument to the wrapped function
        """
        token = None
        # jwt is passed in the request header
        if "Authorization" in request.headers:
            token_type, token = request.headers["Authorization"].split(" ")
            print(app.config["SECRET_KEY"])
        # return 401 if token is not passed
        if token is None or token_type != "Bearer":
            return jsonify({"message": "Unauthorized Access"}), 401
        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config["SECRET_KEY"])
        except jwt.PyJWTError:
            return jsonify({"message": "Token is invalid !!"}), 401
        # returns the current logged in users contex to the routes
        return f(data["payload"], *args, **kwargs)

    return decorated
