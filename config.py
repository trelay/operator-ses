import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "AAbb1234"

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestConfig(Config):
    TESTING = True

class ProductionConfig(Config):
    @staticmethod
    def init_app(app):
        # Set logging
        pass

config = {
    "development": DevelopmentConfig,
    "test": TestConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}

openses_cmd=['cls_cli_tool','-d']
count_hyphen=20 # The count of hyphen that represents a table printed by ses
ses_quit='quit\n'
time_out=10
