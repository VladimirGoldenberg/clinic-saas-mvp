from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity,
    set_access_cookies, unset_jwt_cookies
)
from app.extensions import db  # ✅ правильно
from app.intent import SuperChatbot
from models import User, Organization, Niche, Functionality

import json
import os
from datetime import date

from models import Visit, Patient
from datetime import datetime

routes = Blueprint("routes", __name__)
chatbot = SuperChatbot(xml_path=os.path.join("app", "static", "data", "health.xml"))
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "configs")
@routes.route("/favicon.ico")
def favicon():
    return "", 204
def load_config(niche):
    config_path = os.path.join(CONFIG_DIR, f"{niche}.json")
    if not os.path.exists(config_path):
        default_config = {
            "theme": "default",
            "role": "admin",
            "lang": "en",
            "enabled_features": [
                "change_password",
                "add_organization",
                "add_niche",
                "add_functionality"
            ]
        }
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=2)
        return default_config

    with open(config_path) as f:
        return json.load(f)

@routes.route("/<niche>/dashboard")
@jwt_required()
def dashboard(niche):
    config = load_config(niche)
    email = get_jwt_identity()
    return render_template(
        f"{niche}/dashboard.html",
        email=email,
        niche=niche,
        theme=config.get("theme", "default"),
        role=config.get("role", "admin"),
        tenant="default",
        lang=config.get("lang", "en"),
        features=config.get("enabled_features", [])
    )

@routes.route("/<niche>/change_password", methods=["GET", "POST"])
@jwt_required()
def change_password(niche):
    config = load_config(niche)
    if request.method == "GET":
        return render_template(f"{niche}/change_password.html", niche=niche, features=config.get("enabled_features", []))

    try:
        data = request.get_json(force=True)
        new_password = data.get("new_password")
    except Exception as e:
        return jsonify(msg="Invalid JSON payload", error=str(e)), 400

    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify(msg="User not found"), 404

    user.set_password(new_password)
    db.session.commit()
    return jsonify(msg="Password changed successfully.")

@routes.route("/<niche>/logout", methods=["GET", "POST"])
@jwt_required()
def logout(niche):
    if request.method == "POST":
        response = redirect(url_for("routes.login", niche=niche))
        unset_jwt_cookies(response)
        return response

    config = load_config(niche)
    return render_template(f"{niche}/logout_confirm.html", niche=niche, features=config.get("enabled_features", []))


@routes.route("/<niche>/add_organization", methods=["GET", "POST"])
@jwt_required()
def add_organization(niche):
    config = load_config(niche)
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            flash("Organization name is required.")
            return redirect(url_for("routes.add_organization", niche=niche))

        new_org = Organization(name=name)
        db.session.add(new_org)
        db.session.commit()
        flash("Organization added.")
        return redirect(url_for("routes.add_organization", niche=niche))

    organizations = Organization.query.all()
    return render_template(f"{niche}/add_organization.html", organizations=organizations, niche=niche, features=config.get("enabled_features", []))

@routes.route("/<niche>/add_niche", methods=["GET", "POST"])
@jwt_required()
def add_niche(niche):
    config = load_config(niche)
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            flash("Niche name is required.")
            return redirect(url_for("routes.add_niche", niche=niche))

        new_niche = Niche(name=name)
        db.session.add(new_niche)
        db.session.commit()
        flash("Niche added.")
        return redirect(url_for("routes.add_niche", niche=niche))

    niches = Niche.query.all()
    return render_template(f"{niche}/add_niche.html", niches=niches, niche=niche, features=config.get("enabled_features", []))

@routes.route("/<niche>/add_functionality", methods=["GET", "POST"])
@jwt_required()
def add_functionality(niche):
    config = load_config(niche)
    if request.method == "POST":
        name = request.form.get("name")
        niche_id = request.form.get("niche_id")

        if not name or not niche_id:
            flash("Name and Niche ID are required.")
            return redirect(url_for("routes.add_functionality", niche=niche))

        new_func = Functionality(name=name, niche_id=niche_id)
        db.session.add(new_func)
        db.session.commit()
        flash("Functionality added.")
        return redirect(url_for("routes.add_functionality", niche=niche))

    niches = Niche.query.all()
    functionalities = Functionality.query.all()
    return render_template(f"{niche}/add_functionality.html", niches=niches, functionalities=functionalities, niche=niche, features=config.get("enabled_features", []))

@routes.route("/<niche>/login", methods=["GET", "POST"])
def login(niche):
    config = load_config(niche)
    if request.method == "GET":
        return render_template(f"{niche}/login.html", niche=niche, features=config.get("enabled_features", []))

    email = request.form["email"].strip().lower()
    password = request.form["password"]
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        flash("Invalid credentials.")
        return redirect(url_for("routes.login", niche=niche))

    access_token = create_access_token(identity=user.email)
    response = redirect(url_for("routes.dashboard", niche=niche))
    set_access_cookies(response, access_token)
    return response

@routes.route("/<niche>/register", methods=["GET", "POST"])
def register(niche):
    config = load_config(niche)
    if request.method == "GET":
        return render_template(f"{niche}/register.html", niche=niche, features=config.get("enabled_features", []))

    username = request.form["username"]
    email = request.form["email"].strip().lower()
    password = request.form["password"]

    if User.query.filter_by(email=email).first():
        flash("Email already exists.")
        return redirect(url_for("routes.register", niche=niche))

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("routes.login", niche=niche))

@routes.route("/<niche>/")
def home(niche):
    config = load_config(niche)
    return render_template(f"{niche}/home.html", niche=niche, features=config.get("enabled_features", []))

@routes.route("/")
def redirect_to_default():
    return redirect(url_for("routes.login", niche="health"))
from flask import request, redirect, url_for, render_template, flash
from models import Patient

@routes.route("/<niche>/add_patient", methods=["GET", "POST"])
@jwt_required()  # Если хотите временно отключить защиту — закомментируйте
def add_patient(niche):
    config = load_config(niche)
    if request.method == "POST":
        full_name = request.form.get("full_name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        notes = request.form.get("notes")

        new_patient = Patient(full_name=full_name, phone=phone, email=email, notes=notes)
        db.session.add(new_patient)
        db.session.commit()
        flash("Patient added successfully.")
        return redirect(url_for("routes.patients", niche=niche))

    return render_template(f"{niche}/add_patient.html", niche=niche)
@routes.route("/<niche>/patients")
@jwt_required()
def patients(niche):
    all_patients = Patient.query.all()
    return render_template(f"{niche}/patients.html", patients=all_patients, niche=niche)
from models import Visit, Patient
from datetime import datetime

@routes.route("/<niche>/add_visit", methods=["GET", "POST"])
@jwt_required()
def add_visit(niche):
    config = load_config(niche)

    if request.method == "POST":
        patient_id = request.form.get("patient_id")
        date_str = request.form.get("date")
        time_str = request.form.get("time")
        reason = request.form.get("reason")

        # Преобразуем строку в объекты даты и времени
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        time_obj = datetime.strptime(time_str, "%H:%M").time()

        new_visit = Visit(
            patient_id=patient_id,
            date=date_obj,
            time=time_obj,
            reason=reason
        )
        db.session.add(new_visit)
        db.session.commit()

        flash("Visit scheduled successfully.")
        return redirect(url_for("routes.patients", niche=niche))

    # GET: отобразить форму
    patients = Patient.query.order_by(Patient.full_name).all()
    return render_template(f"{niche}/add_visit.html", patients=patients, niche=niche)
# routes.py


@routes.route('/get_booked_slots', methods=['GET'])
def get_booked_slots():
    selected_date = request.args.get("date")  # e.g. '2025-05-13'
    visits = Visit.query.filter_by(date=selected_date).all()
    booked_times = [visit.time.strftime('%H:%M') for visit in visits]
    return jsonify(booked_times)
@routes.route("/<niche>/schedule_visit")
@jwt_required()
def schedule_visit(niche):
    config = load_config(niche)
    return render_template(f"{niche}/schedule_visit.html", niche=niche, features=config.get("enabled_features", []))

@routes.route("/<niche>/schedule_visit", methods=["POST"])
@jwt_required()
def post_schedule_visit(niche):
    data = request.get_json()
    date_str = data.get("date")
    time_str = data.get("time")

    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        time_obj = datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        return jsonify(msg="Invalid date or time format."), 400

    email = get_jwt_identity()

    # Найдём или создадим пациента
    patient = Patient.query.filter_by(email=email).first()
    if not patient:
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify(msg="User not found."), 404

        patient = Patient(full_name=user.username, email=user.email)
        db.session.add(patient)
        db.session.commit()

    # Проверим, занят ли слот
    existing = Visit.query.filter_by(date=date_obj, time=time_obj).first()
    if existing:
        return jsonify(msg="This slot is already booked."), 409

    # Записываем визит
    visit = Visit(
        patient_id=patient.id,
        date=date_obj,
        time=time_obj,
        reason="Online self-booking"
    )
    db.session.add(visit)
    db.session.commit()

    return jsonify(msg="Visit booked.")
@routes.route("/<niche>/visits")
@jwt_required()
def visits(niche):
    config = load_config(niche)
    email = get_jwt_identity()

    # Получим текущего пользователя
    user = User.query.filter_by(email=email).first()

    # Если пользователь — врач, видит всё (пока роль не реализована — считаем всех пациентами)
    # Можно временно указать список "врачей" вручную
    doctor_emails = ["admin@clinic.com", "vladimir.goldenberg@hotmail.com"]
    is_doctor = email in doctor_emails

    if is_doctor:
        visits = Visit.query.join(Patient).add_columns(
            Visit.date, Visit.time, Visit.reason,
            Patient.full_name, Patient.email
        ).order_by(Visit.date, Visit.time).all()
    else:
        visits = Visit.query.join(Patient).filter(Patient.email == email).add_columns(
            Visit.date, Visit.time, Visit.reason,
            Patient.full_name, Patient.email
        ).order_by(Visit.date, Visit.time).all()

    return render_template(f"{niche}/visits.html", visits=visits, niche=niche)

@routes.route("/<niche>/chatbot")
@jwt_required()
def chatbot(niche):
    config = load_config(niche)
    return render_template(
        f"{niche}/chatbot.html",
        niche=niche,
        features=config.get("enabled_features", [])
    )
from flask import request, jsonify
from app.intent import SuperChatbot

# Инициализация чатбота
chatbot = SuperChatbot(xml_path=os.path.join(os.path.dirname(__file__), "static", "data", "health.xml"))

# Маршрут для обработки запроса
@routes.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("question", "")
    answer = chatbot.answer_question(question)
    return jsonify({"answer": answer})
