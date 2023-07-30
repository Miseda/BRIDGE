from flask import Flask, redirect, url_for, request
from flask_bcrypt import Bcrypt
from mongoengine import connect
from views.auth import auth_bp
from flask_login import LoginManager
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET'  # Secret key

app.config['MONGODB_SETTINGS'] = {
    'db': 'bridge',  # Database name
    'host': 'mongodb+srv://bridge:1234@bridge.oisqkif.mongodb.net/bridge?retryWrites=true&w=majority',
}
# Custom filter to mimic zip function in templates
@app.template_filter()
def zip_filter(lst1, lst2):
    return zip(lst1, lst2)

# Connect to MongoDB
connect('bridge', host=app.config['MONGODB_SETTINGS']['host'])

bcrypt = Bcrypt(app)

# Register the authentication blueprint
app.register_blueprint(auth_bp)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    from models.user import User

    if not user_id:
        print("User ID is None or empty")
        return None

    try:
        user = User.objects(id=user_id).first()

        if user is None:
            print("User not found in the database")
        else:
            print("User found:{}".format (user.username))

        return user
    except Exception as e:
        print("Error loading user: {}".format(str(e)))
        return None
    
# Remove the login route from app.py
# The login route is already defined in the auth_bp (authentication blueprint) in auth.py

@app.route('/')
def index():
    # Redirect to the login page
    return redirect(url_for('auth.login'))

@app.route('/check_connection')
def check_connection():
    try:
        # Access the MongoDB connection through mongoengine's connection
        connect('bridge').ping()
        return 'Successfully connected to MongoDB!'
    except Exception as e:
        return 'Error connecting to MongoDB: {}'.format(str(e))



if __name__ == '__main__':
    app.run(debug=True)
