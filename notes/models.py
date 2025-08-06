# notes/models.py
from bson import ObjectId
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password # <-- Important imports

class NoteManager:
    def __init__(self):
        self.col = settings.mongo_db.notes

    def _process_tags(self, tags_string):
        if not tags_string: return []
        return [tag.strip() for tag in tags_string.split(',') if tag.strip()]

    # --- CRUD Operations ---
    def create(self, title, content, tags="", is_pinned=False, attachments=None, password=None):
        now = timezone.now()
        # Securely hash the password if one is provided
        hashed_password = make_password(password) if password else None
        
        return self.col.insert_one({
            "title": title,
            "content": content,
            "tags": self._process_tags(tags),
            "is_pinned": is_pinned,
            "attachments": attachments or [],
            "password": hashed_password, # <-- Store the hashed password
            "created_at": now,
            "updated_at": now
        }).inserted_id

    def all(self):
        return list(self.col.find().sort([("is_pinned", -1), ("updated_at", -1)]))

    def get(self, pk):
        try:
            return self.col.find_one({"_id": ObjectId(pk)})
        except Exception:
            return None

    def update(self, pk, title, content, tags="", is_pinned=False, attachments=None, password=None):
        update_doc = {
            "title": title,
            "content": content,
            "tags": self._process_tags(tags),
            "is_pinned": is_pinned,
            "updated_at": timezone.now()
        }
        if attachments is not None:
            update_doc["attachments"] = attachments
        
        # --- Logic to update or remove the password ---
        if password:
            # If a new password is provided, hash and save it
            update_doc["password"] = make_password(password)
        elif password is not None: # An empty string means "remove password"
             update_doc["password"] = None

        self.col.update_one({"_id": ObjectId(pk)}, {"$set": update_doc})
    
    def delete(self, pk):
        self.col.delete_one({"_id": ObjectId(pk)})

    def delete_many(self, pks):
        if not pks: return 0
        object_ids = [ObjectId(pk) for pk in pks if pk]
        result = self.col.delete_many({"_id": {"$in": object_ids}})
        return result.deleted_count
        
    def find_by_title(self, title):
        return self.col.find_one({"title": title})

    def search(self, q):
        rx = {"$regex": q, "$options": "i"}
        return list(self.col.find({
            "$or": [{"title": rx}, {"content": rx}, {"tags": rx}]
        }).sort([("is_pinned", -1), ("updated_at", -1)]))

note_manager = None
