from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

app=Flask(__name__, static_url_path='/static')
app.secret_key='mysecretkeyforthisproject'
# Configuration for MySQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:retrodays@localhost:3306/medicalrecords'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional optimization
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')

bcrypt=Bcrypt(app)
db = SQLAlchemy(app)  # Initialize SQLAlchemy instance with app
login_manager=LoginManager(app)
login_manager.login_view='login' #this redirects the user to login pages before they can access user specific routes
login_manager.login_message_category='info' #presents please login message more colorfully

from uhr import routes