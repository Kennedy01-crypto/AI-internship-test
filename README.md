# Vunoh Global Bootstrap (Django 5 + Supabase + Groq)

This project is a Django 5.0 boilerplate for processing diaspora client requests with Groq (Llama 3.3), storing structured outputs in Supabase PostgreSQL, and exposing a simple vanilla HTML/JS interface.

## Stack

- Backend: Django 5 (`core` app)
- Database: PostgreSQL (Supabase via `SUPABASE_DB_URL`)
- AI: Groq (`groq`)
- Frontend: Server-rendered template + vanilla JavaScript `fetch()`
- Static files: WhiteNoise

## Project Structure

- `requirements.txt` - Python dependencies
- `.env.example` - environment variable template
- `manage.py` - Django management entrypoint
- `vunoh_assistant/settings.py` - Django configuration (DB + static + env)
- `core/models.py` - `Client`, `Task`, `CommunicationLog`
- `core/services.py` - `AIRequestProcessor` service layer
- `core/views.py` - page view + API processing endpoint
- `core/urls.py` - app routes
- `templates/index.html` - mobile-first UI

## Core Data Models

- `Client`: basic diaspora user profile
- `Task`:
  - `intent` (choice)
  - `status` (`pending`, `in_progress`, `completed`)
  - `employee_category` (`finance`, `operations`, `legal`)
  - `risk_score` (`FloatField`)
  - `raw_input` (`TextField`)
  - `structured_data` (`JSONField`)
- `CommunicationLog`:
  - Stores generated `whatsapp_message`, `email_message`, and `sms_message`

## API

- `POST /api/process-request/`
  - Accepts JSON body:
    ```json
    {
      "user_input": "I need help with business banking and compliance"
    }
    ```
  - Calls Groq through `AIRequestProcessor`
  - Persists `Task` and `CommunicationLog`
  - Returns structured JSON response

## Environment Variables

Copy `.env.example` to `.env` and fill values:

- `SUPABASE_DB_URL` - PostgreSQL connection URL from Supabase
- `GROQ_API_KEY` - Groq API key
- `DJANGO_SECRET_KEY` - Django secret key
- `DJANGO_DEBUG` - `True` or `False`
- `DJANGO_ALLOWED_HOSTS` - comma-separated hosts

## Local Setup

1. Create and activate virtual environment
2. Install dependencies
3. Configure `.env`
4. Run migrations
5. Start dev server

```bash
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (cmd)
.venv\Scripts\activate.bat

pip install -r requirements.txt
copy .env.example .env

python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Open: `http://127.0.0.1:8000/`

## Notes

- `AIRequestProcessor` enforces `risk_score` in the range `0.0` to `1.0`.
- If the AI returns non-JSON or partial JSON, the service attempts safe extraction and normalization.
