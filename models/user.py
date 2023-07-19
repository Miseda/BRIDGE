from flask import session
from mongoengine import Document, StringField, ListField, ReferenceField
from flask_login import UserMixin
from models.job_postings import JobPosting

class User(UserMixin, Document):
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    job_postings = ListField(ReferenceField(JobPosting))
    
    meta = {
        'collection': 'user'
    }

    # Implement UserMixin methods
    def is_active(self):
        # You can customize this method based on your requirements.
        # For example, if there are specific conditions when a user should be considered inactive, check them here.
        return True

    def is_authenticated(self):
        # Return True if the user is authenticated (logged in) or False otherwise.
        # You can check if the user is logged in by examining the user session.
        # For instance, you can check if the 'username' key is present in the session.
        return 'username' in session

    def is_anonymous(self):
        # This method should return True if the user is anonymous (not logged in) or False otherwise.
        # Since your application requires users to log in, return False.
        return False

    def get_id(self):
        # This method should return a unique identifier for the user (e.g., the user's ID from the database).
        # Assuming your MongoDB ObjectIds are used as user IDs, convert the ObjectId to a string and return it.
        return str(self.id)
