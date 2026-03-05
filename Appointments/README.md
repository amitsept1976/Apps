Appointments and Auth Python

The guide below gives you:

A complete minimal Flask app (auth + booking)

PostgreSQL schema

Project structure

Deployment steps for Render

🧱 1. Project Structure
Code
appointment-app/
  app.py
  models.py
  requirements.txt
  render.yaml   (optional but recommended)
🗄️ 2. PostgreSQL Schema
Create these tables in your Render PostgreSQL instance:

sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL
);

CREATE TABLE appointments (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  date TIMESTAMP NOT NULL,
  description TEXT
);
🧩 3. Flask App Code
requirements.txt
Code
flask
flask_sqlalchemy
psycopg2-binary
werkzeug
python-dotenv
models.py
python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String)
app.py
python
import os
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Appointment
from datetime import datetime
import jwt

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("JWT_SECRET")

db.init_app(app)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    hashed = generate_password_hash(data["password"])
    user = User(email=data["email"], password_hash=hashed)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 400

    token = jwt.encode({"id": user.id}, app.config["SECRET_KEY"], algorithm="HS256")
    return jsonify({"token": token})

def auth_required(f):
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization")
        if not header:
            return jsonify({"error": "Missing token"}), 401
        token = header.split(" ")[1]
        try:
            user_data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            request.user_id = user_data["id"]
        except:
            return jsonify({"error": "Invalid token"}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route("/appointments", methods=["POST"])
@auth_required
def create_appointment():
    data = request.json
    appt = Appointment(
        user_id=request.user_id,
        date=datetime.fromisoformat(data["date"]),
        description=data["description"]
    )
    db.session.add(appt)
    db.session.commit()
    return jsonify({"message": "Appointment booked"})

@app.route("/appointments", methods=["GET"])
@auth_required
def list_appointments():
    appts = Appointment.query.filter_by(user_id=request.user_id).all()
    return jsonify([
        {"id": a.id, "date": a.date.isoformat(), "description": a.description}
        for a in appts
    ])

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
🛠️ 4. Optional: render.yaml (auto‑deploy config)
yaml
services:
  - type: web
    name: appointment-app
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: JWT_SECRET
        sync: false
🚀 5. Deployment Steps on Render
Step 1 — Push to GitHub
From your project folder:

bash
git init
git add .
git commit -m "initial appointment app"
git branch -M main
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main
Step 2 — Create a Render PostgreSQL Database
Go to Render Dashboard

Click New → PostgreSQL

Copy the Internal Database URL

Save it for later

Step 3 — Create a Render Web Service
Click New → Web Service

Select your GitHub repo

Set:

Environment: Python

Build Command:

Code
pip install -r requirements.txt
Start Command:

Code
gunicorn app:app
Step 4 — Add Environment Variables
In Render → Your Web Service → Environment:

Code
DATABASE_URL=postgres://...
JWT_SECRET=your_secret_key
Step 5 — Deploy
Render will:

Install dependencies

Start your Flask app

Expose it at:
https://<your-app>.onrender.com

🧪 6. Test Your API
Register
bash
curl -X POST https://your-app.onrender.com/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"123"}'
Login
bash
curl -X POST https://your-app.onrender.com/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"123"}'
Copy the returned token.

Book Appointment
bash
curl -X POST https://your-app.onrender.com/appointments \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"date":"2026-03-05T14:00:00","description":"Consultatio
