import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))
TOP_LEVEL_DIR = os.path.abspath(os.curdir)


class Config(object):
    DEBUG = False
    TESTING = False
    TEMPLATES_AUTO_RELOAD = True
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    DETA_PROJECT_KEY = os.getenv("DETA_PROJECT_KEY")
    DETA_BASE = os.getenv("DETA_BASE")
    AIRTABLE_BASE_KEY = os.getenv("AIRTABLE_BASE_KEY")
    AIRTABLE_TABLE_NAME = "Members"
    AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
    MSG91_BASE_KEY = os.getenv("MSG91_BASE_KEY")
    TWILIO_TOKEN_KEY = os.getenv("TWILIO_TOKEN_KEY")
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
    MSG91_TEMPLATE_ID = os.getenv("MSG91_TEMPLATE_ID")


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
