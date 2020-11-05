import os
import logging
from flask import Flask
app = Flask(__name__, instance_relative_config=True, static_folder="static")
app.config.from_object(os.environ.get("APP_SETTINGS"))
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s : %(levelname)s : %(name)s : %(message)s'
)
