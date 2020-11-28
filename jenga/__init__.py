import os
from flask import Flask
from flask_cors import CORS
app = Flask(__name__, instance_relative_config=True, static_folder="static")
CORS(app)
app.config.from_object(os.environ.get("APP_SETTINGS"))
import jenga.service