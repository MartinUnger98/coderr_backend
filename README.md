
# Coderr Backend

This is the backend project of **Coderr**, a web-based platform built with Django and Django REST Framework. It provides a robust foundation for building and scaling APIs.

## 🔧 Technologies

- **Python 3.12**
- **Django 5.2.1**
- **Django REST Framework**
- **django-cors-headers**
- **django-filter**
- **SQLite** (default, can be replaced with PostgreSQL or others)

## 📁 Project Structure

```
coderr_backend-main/
├── core/                   # Django project configuration
│   ├── settings.py         # Global settings
│   ├── urls.py             # URL routing
│   └── wsgi.py / asgi.py   # Server gateway interfaces
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── ...
```

## ⚙️ Setup Instructions

### 1. Clone or extract the repository

```bash
git clone <repo-url>
cd coderr_backend-main
```

### 2. Create a virtual environment

```bash
python -m venv env
source env/Scripts/activate  # On Unix/macOS use: source env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (optional, for admin access)

```bash
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

## 🔐 Admin Panel

You can access the Django admin panel at:

```
http://127.0.0.1:8000/admin/
```

Log in using the credentials of the superuser you created.

## 🧪 Running Tests

This project uses `coverage` to measure test coverage.

```bash
coverage run manage.py test
coverage report
```

## 📤 Media Uploads

Media files are stored in the `media/` directory. This is configured in `settings.py`:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

Make sure the following code is included in `urls.py` during development:

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

