# Job Application Tracker (Full-Stack Web)

A personal job-application tracker: Django REST Framework backend with JWT auth, and a React (Vite) frontend with a live stats dashboard, filtering, and full CRUD.

## Stack

- **Backend:** Python 3.14, Django 6, Django REST Framework, SimpleJWT (JWT auth), SQLite (swap to MySQL/Postgres by editing `DATABASES`)
- **Frontend:** React 18, Vite, Axios
- **Tests:** pytest + pytest-django (5 API tests)

## Features

- JWT-protected REST API — every user sees only their own applications
- Per-user data isolation (tested), plus a DB constraint against duplicate company+role per user
- Statuses: wishlist → applied → interview → offer / rejected, with priorities
- Validation: applications past "wishlist" require the date you applied
- `/api/applications/stats/` endpoint computing totals, per-status counts, and interview rate
- React dashboard with stat cards, status filter, create/edit/delete form

## Run it

### Backend (port 8000) — from the repo root

```bash
# one-time setup (repo root already has a shared .venv)
.venv/Scripts/activate            # Windows (Git Bash: source .venv/Scripts/activate)
pip install django djangorestframework django-cors-headers djangorestframework-simplejwt pytest pytest-django

cd projects/05_job_application_tracker/backend
python manage.py migrate
python manage.py createsuperuser  # this user signs into the frontend
python manage.py runserver
```

### Frontend (port 5173) — needs Node.js ≥ 18

```bash
cd projects/05_job_application_tracker/frontend
npm install
npm run dev
```

Open http://localhost:5173 and sign in with the superuser credentials.

### Run backend tests

```bash
cd projects/05_job_application_tracker/backend
python -m pytest        # 5 passed
```

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/token/` | Get JWT access + refresh |
| POST | `/api/token/refresh/` | Refresh the access token |
| GET | `/api/applications/` | List your applications (supports `?status=`) |
| POST | `/api/applications/` | Create one |
| PATCH/DELETE | `/api/applications/{id}/` | Update / delete (404 for other users' rows) |
| GET | `/api/applications/stats/` | Totals, per-status counts, interview rate |

## Honest-notes (same style as the other projects)

- JWT expiry is 30 minutes; the frontend does not yet auto-refresh tokens — log in again when a request 401s.
- SQLite is used for development; run against MySQL/Postgres before claiming production DB experience.
- No HTTPS/production hardening — set `DEBUG=False`, `SECRET_KEY` from env, and a real CORS config before deploying.
