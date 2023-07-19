from mongoengine import Document, StringField

class Message(Document):
    name = StringField(required=True)
    email = StringField(required=True)
    message = StringField(required=True)
