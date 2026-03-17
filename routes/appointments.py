from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from models import Appointment
from forms import AppointmentForm
from datetime import datetime

appointments_bp = Blueprint("appointments", __name__)


def _require_user_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.user_id != current_user.id:
        abort(403)
    return appointment


def _build_appointment_from_form(form):
    return Appointment(
        user_id=current_user.id,
        title=form.title.data.strip(),
        description=form.description.data,
        appointment_date=form.appointment_date.data,
        appointment_time=form.appointment_time.data,
        duration_minutes=form.duration_minutes.data,
        consultant_name=form.consultant_name.data.strip(),
        consultation_type=form.consultation_type.data,
        notes=form.notes.data,
        status="confirmed",
    )


def _apply_form_to_appointment(appointment, form):
    appointment.title = form.title.data.strip()
    appointment.description = form.description.data
    appointment.appointment_date = form.appointment_date.data
    appointment.appointment_time = form.appointment_time.data
    appointment.duration_minutes = form.duration_minutes.data
    appointment.consultant_name = form.consultant_name.data.strip()
    appointment.consultation_type = form.consultation_type.data
    appointment.notes = form.notes.data
    appointment.updated_at = datetime.utcnow()


@appointments_bp.route("/dashboard")
@login_required
def dashboard():
    today = datetime.today().date()
    upcoming = (
        Appointment.query
        .filter_by(user_id=current_user.id)
        .filter(Appointment.appointment_date >= today)
        .filter(Appointment.status != "cancelled")
        .order_by(Appointment.appointment_date, Appointment.appointment_time)
        .all()
    )
    past = (
        Appointment.query
        .filter_by(user_id=current_user.id)
        .filter(Appointment.appointment_date < today)
        .order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc())
        .limit(10)
        .all()
    )
    cancelled = (
        Appointment.query
        .filter_by(user_id=current_user.id, status="cancelled")
        .order_by(Appointment.appointment_date.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "appointments/dashboard.html",
        upcoming=upcoming,
        past=past,
        cancelled=cancelled,
        today=today,
        title="My Dashboard",
    )


@appointments_bp.route("/appointments/new", methods=["GET", "POST"])
@login_required
def new_appointment():
    form = AppointmentForm()
    if form.validate_on_submit():
        appointment = _build_appointment_from_form(form)
        db.session.add(appointment)
        db.session.commit()
        flash("Appointment booked successfully!", "success")
        return redirect(url_for("appointments.dashboard"))
    return render_template("appointments/form.html", form=form, title="Book Appointment", action="Book")


@appointments_bp.route("/appointments/<int:appointment_id>")
@login_required
def view_appointment(appointment_id):
    appointment = _require_user_appointment(appointment_id)
    return render_template("appointments/view.html", appointment=appointment, title="Appointment Details")


@appointments_bp.route("/appointments/<int:appointment_id>/edit", methods=["GET", "POST"])
@login_required
def edit_appointment(appointment_id):
    appointment = _require_user_appointment(appointment_id)
    if appointment.status == "cancelled":
        flash("Cancelled appointments cannot be edited.", "warning")
        return redirect(url_for("appointments.dashboard"))

    form = AppointmentForm(obj=appointment)
    if form.validate_on_submit():
        _apply_form_to_appointment(appointment, form)
        db.session.commit()
        flash("Appointment updated successfully!", "success")
        return redirect(url_for("appointments.view_appointment", appointment_id=appointment.id))

    return render_template(
        "appointments/form.html", form=form, title="Edit Appointment",
        action="Update", appointment=appointment
    )


@appointments_bp.route("/appointments/<int:appointment_id>/cancel", methods=["POST"])
@login_required
def cancel_appointment(appointment_id):
    appointment = _require_user_appointment(appointment_id)
    if appointment.status == "cancelled":
        flash("This appointment is already cancelled.", "info")
    else:
        appointment.status = "cancelled"
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Appointment cancelled.", "info")
    return redirect(url_for("appointments.dashboard"))
