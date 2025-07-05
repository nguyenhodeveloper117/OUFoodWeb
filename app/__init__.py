from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)
app.secret_key = 'nhom6@321'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/oufooddb?charset=utf8mb4" % quote("Admin@123")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 8

db = SQLAlchemy(app=app)
login = LoginManager(app=app)

# Configuration
cloudinary.config(
    cloud_name="dnwyvuqej",
    api_key="559324578186686",
    api_secret="tjXbrfktUPN8lYMmE9SN-33QXjc",  # Click 'View API Keys' above to copy your API secret
    secure=True
)