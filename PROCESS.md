# Vunoh Assistant - Step-by-Step Setup and Run Guide

This document provides a complete, tested step-by-step process to set up and run the Vunoh Assistant Django application locally on Windows 10. The application uses Django 5, PostgreSQL (via Supabase or local), Groq Llama 3.3 AI, and serves a simple HTML/JS interface.

## Prerequisites

- Python 3.10+ installed (check with `python --version`)
- Git (if cloning fresh)
- Optional: Free Supabase account for PostgreSQL, Google AI Studio API key for Gemini
- Optional: Free Supabase account for PostgreSQL, Groq API key

## Step 1: Clone and Navigate (if not already in directory)

```
cd /d D:\Project\AI-internship-test
```

## Step 2: Create and Activate Virtual Environment

Open PowerShell, Command Prompt, or Git Bash in the project root and run:

```
python -m venv .venv
```

Activate:

- **PowerShell**: `.venv\Scripts\Activate.ps1`
- **Command Prompt (cmd)**: `.venv\Scripts\activate.bat`
- **Git Bash**: `source .venv/Scripts/activate`

Verify: Prompt should show `(.venv)`.

## Step 3: Install Dependencies

```
pip install -r requirements.txt
```

This installs:

- Django 5.0.\*
- dj-database-url, python-dotenv, whitenoise
- psycopg (PostgreSQL adapter)
- google-generativeai (Gemini AI)

## Step 4: Configure Environment Variables

Copy the template:

```
copy .env.example .env
```

**Important**: Edit `.env` immediately after copying—focus on `SUPABASE_DB_URL` line.

Example `.env` content (fill your values):

```
DJANGO_SECRET_KEY=your-super-secret-key-here-generate-with-django-admin-generate-a-long-one-at-least-50-chars-random
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
USE_POSTGRES=True
SUPABASE_DB_URL=postgresql://postgres:password@db.supabase.com:5432/postgres
GROQ_API_KEY=your-groq-api-key
```

- Generate SECRET_KEY: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- **Local SQLite**: Must have `SUPABASE_DB_URL=` blank (no value after =) or delete the line entirely. Invalid placeholder like `postgresql://user:pass...` causes ParseError.
- Without GEMINI_API_KEY: AI endpoints return errors gracefully; app runs.

**Note**: Never commit `.env` to Git.

## Step 5: Apply Database Migrations (First-Time Setup)

Even on fresh DB:

```
python manage.py makemigrations
python manage.py migrate
```

Creates tables for `Client`, `Task`, `CommunicationLog`, auth, etc.

## Step 6: Collect Static Files (for Whitenoise)

```
python manage.py collectstatic --noinput
```

## Step 7: Create Superuser (Optional)

```
python manage.py createsuperuser
```

## Step 8: Start Server

```
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## Verification

- Index page loads.
- API test: Use browser dev tools or curl for `/api/process-request/`.

## Troubleshooting

- **dj_database_url.ParseError**: `.env` `SUPABASE_DB_URL` must be blank for SQLite. Edit `.env`, change `SUPABASE_DB_URL=postgresql://...` to `SUPABASE_DB_URL=` (blank value), save, retry migrations.
- **ModuleNotFound**: Reactivate venv.
- **SECRET_KEY prompt**: Set valid SECRET_KEY in `.env`.
- **Migrations fail**: `del db.sqlite3` then retry.
- **Port 8000 busy**: `runserver 8001`.

## Deactivate/Cleanup

```
deactivate
rmdir /s .venv
del db.sqlite3
```
