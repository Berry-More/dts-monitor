from flask import Flask
from config import Config
from front import dash_app


server = Flask(__name__)
server.config.from_object(Config)
dash_application = dash_app(server)

from app import routes
