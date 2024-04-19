from uhr import db,app,login_manager
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text, BLOB, Enum
from sqlalchemy.orm import relationship
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


class Patient(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  reports = relationship("MedicalReport", backref="patient", cascade="all, delete-orphan")
  diagnoses = relationship("DiagnosisHistory", backref="patient",cascade="all, delete-orphan")
  user = relationship("User", backref="patient", uselist=False, cascade="all, delete-orphan")  # One-to-One with User

class Doctor(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  diagnoses = relationship("DiagnosisHistory", backref="doctor", cascade="all, delete-orphan")
  user = relationship("User", backref="doctor", uselist=False, cascade="all, delete-orphan")  # One-to-One with User

class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  user_type = db.Column(db.Enum("patient", "doctor"))
  name = db.Column(db.String(50))
  patient_id = db.Column(db.Integer, ForeignKey("patient.id"))
  doctor_id = db.Column(db.Integer, ForeignKey("doctor.id"))
  username = db.Column(db.String(25), unique=True)
  password = db.Column(db.String(255))  # Store hashed password using a secure algorithm


class MedicalReport(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  patient_id = db.Column(db.Integer, ForeignKey("patient.id"))
  # report_file = db.Column(db.BLOB)  # Or db.String(255) depending on storage method
  report_file = db.Column(db.String(2550)) 
 
class DiagnosisHistory(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  patient_id = db.Column(db.Integer, ForeignKey("patient.id"))
  doctor_id = db.Column(db.Integer, ForeignKey("doctor.id"))
  diagnosis_text = db.Column(Text)

with app.app_context():
  db.create_all()
