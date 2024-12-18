import os

class Config(object):
    TESTING = False
    HOST = "0.0.0.0"
    BUCKET = 'dogguesser'
    PORT = "8080"
    SESSION_TYPE = "filesystem"
    SECRET_KEY = os.urandom(24)
    ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif"]
    UPLOAD_FOLDER = None


class ProductionConfig(Config):
    DEBUG = False
    UPLOAD_FOLDER = "/app/static"


class DevelopmentConfig(Config):
    DEBUG = True
    UPLOAD_FOLDER = "test"
