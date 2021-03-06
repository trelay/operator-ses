from flask import Flask
from config import config
from codebase import init_channels

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    init_channels()

    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app



