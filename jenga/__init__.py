import os
from flask import Flask
app = Flask(__name__, instance_relative_config=True, static_folder="static")
app.config.from_object(os.environ.get("APP_SETTINGS"))