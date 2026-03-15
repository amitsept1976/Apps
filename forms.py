from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, TextAreaField,
    DateField, TimeField, SelectField, IntegerField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, Optional, ValidationError, NumberRange
)
from models import User


class RegistrationForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(min=2, max=80)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone Number", validators=[Optional(), Length(max=20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match")]
    )
    submit = SubmitField("Create Account")

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data.lower()).first()
        if user:
            raise ValidationError("That email is already registered. Please log in.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class AppointmentForm(FlaskForm):
    title = StringField("Appointment Title", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=500)])
    appointment_date = DateField("Date", validators=[DataRequired()])
    appointment_time = TimeField("Time", validators=[DataRequired()])
    duration_minutes = SelectField(
        "Duration",
        choices=[(15, "15 minutes"), (30, "30 minutes"), (45, "45 minutes"), (60, "1 hour"), (90, "1.5 hours"), (120, "2 hours")],
        coerce=int,
        default=30,
    )
    consultant_name = StringField("Consultant Name", validators=[DataRequired(), Length(max=150)])
    consultation_type = SelectField(
        "Consultation Type",
        choices=[
            ("general", "General"),
            ("medical", "Medical"),
            ("legal", "Legal"),
            ("financial", "Financial"),
            ("technical", "Technical"),
            ("other", "Other"),
        ],
    )
    notes = TextAreaField("Additional Notes", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Book Appointment")
