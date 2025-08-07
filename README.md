#  Advanced Django Note-Taking App

An **advanced, feature-rich note-taking web application** built with Django and using MongoDB as the backend database. This project goes far beyond basic CRUD operations by incorporating features like password protection, file attachments, markdown support, and more.

---

##  Features

- **CRUD Operations**: Create, read, update, and delete notes.
- **Markdown Support**: Write notes using full Markdown syntax (headers, lists, links, etc.).
- **Syntax Highlighting**: Code blocks automatically get syntax highlighting.
- **Password Protection**: Secure notes individually with passwords. Password is also required to delete protected notes.
- **File Attachments**: Attach multiple files per note with clean, unique names.
- **Tagging System**: Organize notes using comma-separated tags.
- **Pinning Notes**: Keep important notes at the top of the list.
- **Note Linking**: Use `[[Note Title]]` wiki-style links to reference other notes.
- **Bulk Deletion**: Select and delete multiple notes at once (protected notes are excluded).
- **Full-Text Search**: Search across titles, content, and tags.
- **Modern UI**: Clean and responsive interface built with **Bootstrap 5 (Cyborg theme)**.

---

## Structure:

```bash 
├── manage.py
├── noteapp
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── notes
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── __init__.py
│   ├── models.py
│   ├── templatetags
│   │   └── note_extras.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── README.md
├── requirements.txt
└── templates
    ├── base.html
    └── notes
        ├── note_confirm_delete.html
        ├── note_detail.html
        ├── note_form.html
        ├── note_list.html
        └── note_unlock_form.html
```
---
## Tech Stack

- **Backend**: Django 5
- **Database**: MongoDB
- **Frontend**: Bootstrap 5, Font Awesome
- **Python Libraries**: `pymongo`, `markdown2`, `django-environ`

---

##  Installation & Setup

Follow these steps to get the application running locally:

### 1. Prerequisites

- Python 3.8+
- MongoDB installed (locally or using [MongoDB Atlas](https://www.mongodb.com/cloud/atlas))

---

### 2. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

```
---
## 3. Set Up a Virtual Environment(optional)
```bash
# Create virtual environment
python3 -m venv venv

# Activate the environment
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

```
---
## 4. Install Dependencies

```bash
pip install -r requirements.txt --break-system-packages
```
---
## 5. Configure Environment Variables

```bash

CREATE .env FILE

# .env

# Generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
SECRET_KEY="your-random-secret-key"

DEBUG="True"

# MongoDB connection
MONGO_URI="mongodb://localhost:27017/noteapp"

ALLOWED_HOSTS="127.0.0.1,localhost"

```
---
## 6. Set Up the Default SQLite DB (for session/admin) && Run the deployment
```bash
python3 manage.py migrate
python3 manage.py runserver 

Visit: http://127.0.0.1:8000
```




