from mongoengine import Document, StringField, DateTimeField, ReferenceField

class JobPosting(Document):
    title = StringField(required=True)
    content = StringField(required=True)
    user = ReferenceField('User')  # Reference to the User model
    created_at = DateTimeField(required=True)

    meta = {
        'collection': 'job_postings'
    }
