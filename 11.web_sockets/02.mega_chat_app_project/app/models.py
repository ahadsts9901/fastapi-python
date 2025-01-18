from mongoengine import Document, StringField, DateTimeField
from datetime import datetime

class User(Document):
    username = StringField(required=True)
    email = StringField(required=True, unique=True)
    profile_picture = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "profile_picture": self.profile_picture,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class Chat(Document):
    from_id = StringField(required=True)
    to_id = StringField(required=True)
    text = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "from_id": str(self.from_id),
            "to_id": str(self.to_id),
            "text": str(self.text),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
