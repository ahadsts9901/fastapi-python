from mongoengine import Document, StringField, DateTimeField
from datetime import datetime

class User(Document):
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    role = StringField(default="user")  # user, admin, etc.
    profile_picture = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "role": self.role,
            "profile_picture": self.profile_picture,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
