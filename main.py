from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("appointments.dashboard"))
    return render_template("main/index.html", title="ConsultBook – Book Your Consultation")


@main_bp.app_errorhandler(403)
def forbidden(e):
    return render_template("errors/403.html"), 403


@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404
