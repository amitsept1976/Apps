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
