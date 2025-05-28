from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, time  # если ещё не импортировано

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)

    def __init__(self, username, email, **kwargs):
        super().__init__(username=username, email=email.strip().lower(), **kwargs)
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    users = db.relationship('User', backref='organization', lazy=True)

class Niche(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

class Functionality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    niche_id = db.Column(db.Integer, db.ForeignKey('niche.id'), nullable=False)
    niche = db.relationship('Niche', backref=db.backref('functionalities', lazy=True))
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    notes = db.Column(db.Text)

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    reason = db.Column(db.String(255))
    
    # Связь с пациентом
    patient = db.relationship('Patient', backref='visits')

