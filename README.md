# ConsultBook — Appointment Booking App

A Flask + PostgreSQL web service for booking and managing consultations, with user authentication. Deployable to [Render](https://render.com) in minutes.

---

## Features

- **User registration & login** — secure password hashing with Werkzeug
- **Book appointments** — date, time, duration, consultant, type
- **View appointments** — dashboard with upcoming, past, and cancelled
- **Edit appointments** — update any field before the appointment
- **Cancel appointments** — soft-cancel with status tracking
- **Access control** — users can only see and manage their own appointments
- **CSRF protection** — all forms protected via Flask-WTF

---

## Tech Stack

| Layer      | Technology              |
|------------|-------------------------|
| Language   | Python 3.11             |
| Framework  | Flask 3.x               |
| Database   | PostgreSQL (via Render)  |
| ORM        | Flask-SQLAlchemy         |
| Auth       | Flask-Login              |
| Forms      | Flask-WTF / WTForms      |
| Server     | Gunicorn                 |
| Hosting    | Render                   |

---

## Project Structure

```
appointment-app/
├── app.py                  # App factory, extensions init
├── wsgi.py                 # Gunicorn entry point
├── models.py               # User & Appointment DB models
├── forms.py                # WTForms form classes
├── requirements.txt
├── render.yaml             # Render deployment config
├── .env.example
├── routes/
│   ├── auth.py             # /register, /login, /logout
│   ├── appointments.py     # /dashboard, /appointments/*
│   └── main.py             # /, error handlers
├── templates/
│   ├── base.html
│   ├── main/index.html
│   ├── auth/{login,register}.html
│   ├── appointments/{dashboard,form,view}.html
│   └── errors/{403,404}.html
└── static/css/style.css
```

---

## Local Development

### 1. Clone & set up environment

```bash
git clone <your-repo-url>
cd appointment-app
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set SECRET_KEY and DATABASE_URL
```

For local Postgres:
```bash
createdb consultbook_dev
# Set DATABASE_URL=postgresql://localhost/consultbook_dev in .env
```

### 3. Run

```bash
python wsgi.py
# App runs at http://localhost:5000
```

Tables are created automatically on first run via `db.create_all()`.

---

## Deploy to Render

### Option A — Using render.yaml (recommended, one-click)

1. Push your code to a GitHub or GitLab repo
2. Go to [render.com](https://render.com) → **New** → **Blueprint**
3. Connect your repo — Render reads `render.yaml` automatically
4. It will create:
   - A **Web Service** (Python/Gunicorn)
   - A **PostgreSQL database** (free tier)
   - Auto-link `DATABASE_URL` and generate `SECRET_KEY`
5. Click **Apply** — deployment starts

### Option B — Manual setup

1. **Create PostgreSQL DB** on Render → note the **Internal Database URL**
2. **Create Web Service** → connect your repo
   - Environment: `Python 3`
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn wsgi:app --workers 2 --bind 0.0.0.0:$PORT`
3. Add **Environment Variables**:
   | Key | Value |
   |-----|-------|
   | `SECRET_KEY` | Generate a strong random string |
   | `DATABASE_URL` | Internal connection string from step 1 |
4. Deploy

> **Note:** Render's free PostgreSQL instances expire after 90 days. Upgrade to a paid plan for production use.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask secret key for sessions & CSRF |
| `DATABASE_URL` | PostgreSQL connection string |

---

## Security Notes

- Passwords are hashed with PBKDF2-SHA256 via Werkzeug
- All forms use CSRF tokens (Flask-WTF)
- Users can only access their own appointments (403 on unauthorized access)
- `LOGIN_REQUIRED` decorator protects all appointment routes
- SQL injection protected via SQLAlchemy ORM
