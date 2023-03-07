from flask import Flask
from config import Config
from front import dash_app


app = Flask(__name__)
app.config.from_object(Config)
dash_app(app)

from app import routes
