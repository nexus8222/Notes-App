# notes/apps.py
from django.apps import AppConfig
from django.conf import settings
from pymongo import MongoClient

class NotesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notes"

    def ready(self):
        # attach mongo_db lazily if not already present
        if not hasattr(settings, "mongo_db"):
            uri = getattr(settings, "MONGO_URI", "mongodb://localhost:27017/noteapp")
            client = MongoClient(uri, uuidRepresentation="standard")
            settings.mongo_db = client.get_default_database()
