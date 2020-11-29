import os
from flask import Flask
from flask_cors import CORS
from jenga.config import Config

app = Flask(__name__)
app.config['CORS_SUPPORTS_CREDENTIALS'] = 'true'
CORS(app, support_credentials=True)

app.config.from_object(os.environ.get("APP_SETTINGS"))

import jenga.service