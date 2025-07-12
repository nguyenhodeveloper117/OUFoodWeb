from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary
from authlib.integrations.flask_client import OAuth
import json

app = Flask(__name__)
app.secret_key = 'nhom6@321'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/oufooddb?charset=utf8mb4" % quote("Admin@123")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 8
oauth = OAuth(app)

db = SQLAlchemy(app=app)
login = LoginManager(app=app)

# Configuration
cloudinary.config(
    cloud_name="dnwyvuqej",
    api_key="559324578186686",
    api_secret="tjXbrfktUPN8lYMmE9SN-33QXjc",  # Click 'View API Keys' above to copy your API secret
    secure=True
)

with open('config.json') as config_file:
    config = json.load(config_file)

google = oauth.register(
    name='google',
    client_id=config['client_id_gg'],
    client_secret=config['client_secret_gg'],
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
)