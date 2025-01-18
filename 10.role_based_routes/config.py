import os
from dotenv import load_dotenv

load_dotenv()

JWT_KEY = os.getenv("JWT_KEY")
MONGO_URI = os.getenv("MONGO_URI")
