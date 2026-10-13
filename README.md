# Django REST Framework API Starter

A starter project for building REST APIs with Django and Django REST Framework.

## Features

* **JWT authentication** (`djangorestframework-simplejwt`): login, refresh with rotation, and logout via token blacklist.
* **Custom user model** that uses email as the identifier, with soft delete. Logging in again restores a deleted account.
* **Account flows**: registration, email verification (optional or required), and password reset.
* **Social login** with Google and Facebook.
* **Consistent responses**: every endpoint returns `{success, status_code, message, data, errors}`.
* **Secure defaults**: endpoints require authentication unless marked public, auth endpoints are rate limited, and production hardening applies when `DEBUG=0`.
* **API docs** with Swagger and ReDoc (`drf-yasg`).
* **Celery + Redis** for background tasks.
* **SQLite or Postgres**, chosen with one environment variable.
* **Docker**: a production image, plus a `docker-compose.yml` with web, Postgres, Redis, a Celery worker and beat.
* **Health checks** at `/health/` (liveness) and `/ready/` (checks the database).

## Getting started

### Prerequisites

* Python 3.12+
* Redis, only if you run Celery locally

### Local setup

```bash
git clone https://github.com/musicmeetscode/django-rest-framework-starter.git
cd django-rest-framework-starter

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
python generate_key.py            # paste the output into SECRET_KEY in .env

python manage.py migrate
python manage.py create_super_user   # uses ADMIN_EMAIL / ADMIN_PASSWORD from .env
python manage.py runserver
```

The API runs at `http://127.0.0.1:8000/`. To also start Celery, use `./run_dev.sh`.

### With Docker

```bash
cp .env.example .env              # set SECRET_KEY (and ADMIN_EMAIL / ADMIN_PASSWORD)
docker compose up --build
```

This starts the API on port 8000 with Postgres, Redis, a Celery worker and beat. Migrations, `collectstatic`
and the admin user are handled on startup by `entrypoint.sh`. For a server deployment behind Nginx, see [DEPLOY.md](DEPLOY.md).

### Running tests

```bash
python manage.py test
```

## Configuration

All settings come from environment variables. The full list is in [.env.example](.env.example). The main ones:

| Variable | Default | Notes |
|---|---|---|
| `SECRET_KEY` | (required) | `python generate_key.py` |
| `DEBUG` | `0` | `1` for local development |
| `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` | empty | comma separated |
| `DB_CHOICE` | `sqlite` | `postgres` requires `DATABASE_URL` |
| `REQUIRE_EMAIL_VERIFICATION` | `0` | block login until the email is verified |
| `EMAIL_BACKEND` | console | set to the SMTP backend to send real email |
| `GOOGLE_CLIENT_ID`, `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET` | empty | required for social login |

## API endpoints

* Swagger: `/swagger/` · ReDoc: `/redoc/` · Admin: `/admin/`

### Authentication (`/user/`)

| Method | Path | Auth | Body |
|---|---|---|---|
| POST | `/user/register` | public | `{"email", "password", "full_name"?}` |
| GET | `/user/verify-email?token=...` | public | link from the verification email |
| POST | `/user/resend-verification` | public | `{"email"}` |
| POST | `/user/login` | public | `{"email", "password"}` → `{user, tokens: {access, refresh}}` |
| POST | `/user/token/refresh` | public | `{"refresh"}` → new `access` and `refresh` |
| POST | `/user/logout` | user | `{"refresh"}` (blacklists the token) |
| POST | `/user/request-reset-password` | public | `{"email"}` |
| GET | `/user/password-reset/<uidb64>/<token>` | public | checks a reset link |
| PATCH | `/user/password-reset-complete` | public | `{"password", "uidb64", "token"}` |
| GET/PATCH | `/user/me` | user | the current user's profile |
| GET | `/user/users` | admin | paginated list of users |
| GET/PATCH/DELETE | `/user/<id>` | owner or admin | `DELETE` soft deletes |
| POST | `/social-auth/google/` | public | `{"auth_token": "<Google ID token>"}` |
| POST | `/social-auth/facebook/` | public | `{"auth_token": "<Facebook access token>"}` |

Send the access token on protected endpoints:

```
Authorization: Bearer <access_token>
```

### Response format

```json
{"success": true, "status_code": 200, "message": "", "data": {"...": "..."}}
{"success": false, "status_code": 400, "message": "email: Enter a valid email address.", "data": null, "errors": ["email: Enter a valid email address."]}
```

## Adding your own endpoints

Put your models and views in the `api` app (or a new app) and register routes in `api/urls.py`; they're served under `/api/`.
For soft delete, UUIDs and timestamps, models can extend `accounts.models.BaseModel`. Views require
authentication by default; set `permission_classes = (AllowAny,)` to make one public.
