from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import os
from datetime import datetime
import random
import string

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="mysql+pymysql://root:mysql@localhost:3306/test"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db=SQLAlchemy(app)
jwt = JWTManager(app)
logging.basicConfig(level=logging.INFO)



# models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))
    full_name = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(500))
    submitted_by = db.Column(db.String(50))
    is_doctor = db.Column(db.Integer,default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    specialist_id = db.Column(db.Integer)
    occupation = db.Column(db.String(20))
    submitted_by = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class Specialist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    specialist_in = db.Column(db.String(100))
    submitted_by = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)



class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pateint_name = db.Column(db.String(100))
    age = db.Column(db.String(20))
    diagnosis = db.Column(db.String(200))    
    is_discharged = db.Column(db.Boolean, default=False)
    admitted_on  = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class Appointments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, default=30)  # in minutes
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def create_admin_user():
    if User.query.count() == 0:
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        user = User(
            type='admin',
            full_name='Mohammad Arshad Khan',
            username='admin',
            email='admin@gmail.com',
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        print(f"First admin user created, username: admin, password: {password}")
        logging.info(f"First admin user created, username: admin, password: {password}")

@app.errorhandler(Exception)
def handle_error(e):
    logging.error(f"Error: {str(e)}")
    return jsonify({"error": str(e)}), 500




@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    print(username,password)
    user = User.query.filter_by(username=username).first()
    print(user.password,password)
    if user and check_password_hash(user.password, password):
        token = create_access_token(identity=str(user.id))
        return jsonify({"token": token}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/doctors', methods=['GET', 'POST'])
@jwt_required()
def doctors():
    print("hello")
    if request.method == 'GET':
        students = Doctor.query.all()
        return jsonify([{
            "id": s.id,
            "full_name": s.full_name,
            "specialist_id": s.specialist_id,
            "occupation": s.occupation,
            "submitted_by": s.submitted_by,
            "updated_at": s.updated_at.isoformat()
        } for s in students])
    
    if request.method == 'POST':
        data = request.get_json()
        print(str(get_jwt_identity()))
        print(data,"datatttttt")
        s = Doctor(
            full_name=data['full_name'],
            specialist_id=data['specialist_id'],
            occupation=data['occupation'],
            submitted_by=str(get_jwt_identity())
        )
        db.session.add(s)
        db.session.commit()
        return jsonify({"id": s.id}), 201


@app.route('/departments', methods=['GET', 'POST'])
@jwt_required()
def inSpecialist():
    if request.method == 'GET':
        departments = Specialist.query.all()
        return jsonify([{
            "id": d.id,
            "specialist_in": d.specialist_in,
            "submitted_by": d.submitted_by,
            "updated_at": d.updated_at.isoformat()
        } for d in departments])
    
    if request.method == 'POST':
        data = request.get_json()
        d = Specialist(
            specialist_in=data['specialist_in'],
            submitted_by=str(get_jwt_identity())
        )
        db.session.add(d)
        db.session.commit()
        return jsonify({"id": d.id}), 201
    
@app.route('/patient', methods=['GET', 'POST'])
@jwt_required()
def patients():
    print("hello")
    if request.method == 'GET':
        patients = Patient.query.all()
        return jsonify([{
            "id": p.id,
            "pateint_name": p.pateint_name,
            "age": p.age,
            "diagnosis": p.diagnosis,
            "is_discharge":p.is_discharged,
            "admitted_on": p.admitted_on.isoformat(),
            "updated_at": p.updated_at.isoformat()
        } for p in patients])
    
    if request.method == 'POST':
        data = request.get_json()
        print(str(get_jwt_identity()))
        print(data,"datatttttt")
        p = Doctor(
            pateint_name=data['pateint_name'],
            age=data['age'],
            diagnosis=data['diagnosis'],
            submitted_by=str(get_jwt_identity())
        )
        db.session.add(p)
        db.session.commit()
        return jsonify({"id": p.id}), 201

@app.route('/appointments', method=['GET','POST'])
@jwt_required
def appointments():
    if request.method=='GET':
        appointmentdata=Appointments.query.all()
        return jsonify([{"id":a.id,'patient_name':a.patient_name,'doctor_name':a.doctor_name,
                        'appointment_date':a.appointment_date,'duration':a.duration,'status':a.status,
                        'notes':a.notes,'created_at':a.created_at.isoformat()} for a in appointmentdata])

    if request.method=='POST':
        data=request.get_json()
        a=Appointments(patient_name=data['patient_name'],
                       doctor_name=data['doctor_name'],
                       appointment_date=datetime.utcnow,
                       status=data['status'],
                       notes=data['notes'] )
        db.session.add(a)
        db.session.commit()
        return jsonify({"id": a.id}), 201



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_admin_user()
    app.run(debug=True)