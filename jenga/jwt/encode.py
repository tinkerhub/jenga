from jenga import app
from datetime import datetime,timedelta
import jwt

def encode_token(payload):
    return jwt.encode({'payload':payload, 'exp' : datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'])


def jenga_jwt_encoder(number=None,verified = False,memberShipID = None):
    return encode_token({'number':number,'verified':verified,'memberShipID':memberShipID})