import datetime
import cred
from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import (
    create_access_token, get_jwt_identity, jwt_required, JWTManager)
from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://{0}:{1}@{2}/{3}".format(
    cred.user, cred.passwrd, cred.host, cred.name)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JSON_SORT_KEYS"] = False
app.config["JWT_SECRET_KEY"] = "super-secretjhjhgh"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
# app.config['MAIL_PORT'] = 587
app.config['MAIL_DEFAULT_SENDER'] = "tresatritto28@gmail.com"
app.config['MAIL_USERNAME'] = 'tresatritto28@gmail.com'
app.config['MAIL_PASSWORD'] = 'mypassword'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
db = SQLAlchemy(app)
jwt = JWTManager(app)
mail = Mail(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique=True)
    password = db.Column(db.String(120), nullable=False)

    def to_json(self):
        return {"id": self.id, "name": self.name, "email": self.email}


class Student(db.Model):
    __tablename__ = 'student'
    usn = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(128))
    branch = db.Column(db.String(128))
    college = db.Column(db.String(128))
    marks = db.Column(db.String(128))

    def to_json(self):
        return {"usn": self.usn, "name": self.name, "email": self.email, "branch": self.branch,
                "college": self.college, "marks": self.marks}


@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        name = data['name']
        email = data['email']
        password = data['password']
        if not email:
            return 'Missing email',
        if not password:
            return 'Missing password', 400
        new_user = User(name=name, email=email,
                        password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_json())
    except:
        db.session.rollback()
        raise


@app.route("/login", methods=["POST"])
def login():
    email = request.args.get('email')
    password = request.args.get('password')
    user = User.query.filter_by(email=email).first()
    if not user:
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
        )
    if check_password_hash(user.password, password):
        access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)


@app.route("/register_student", methods=["POST"])
@jwt_required()
def register_student():
    try:
        data = request.get_json()
        usn = data["usn"]
        name = data['name']
        email = data['email']
        branch = data['branch']
        college = data['college']
        marks = data['marks']

        new_stud = Student(usn=usn, name=name, email=email,
                           branch=branch, college=college, marks=marks)
        msg = Message('Student Registration',
                      recipients=[new_stud.email])
        msg.body = name+" with email id: "+email+" has registered sucessfully."
        mail.send(msg)
        db.session.add(new_stud)
        db.session.commit()
        return jsonify(new_stud.to_json())
    except:
        db.session.rollback()
        raise


@app.route("/get_student/<int:usn>", methods=["GET"])
@jwt_required()
def get_student(usn):
    student = Student.query.filter_by(usn=usn).first()
    if not student:
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
        )
    return jsonify(student.to_json())


@app.route("/get_students", methods=["GET"])
@jwt_required()
def get_students():
    students = Student.query.all()
    return jsonify([s.to_json() for s in students])


@app.route("/edit_student/<int:usn>", methods=["GET"])
@jwt_required()
def edit_student(usn):
    student = Student.query.filter_by(usn=usn).first()
    data = request.get_json()
    if "email" in data:
        student.email = data["email"]
    if "name" in data:
        student.name = data["name"]
    if "branch" in data:
        student.branch = data["branch"]
    if "college" in data:
        student.college = data["college"]
    if "marks" in data:
        student.marks = data["marks"]
    db.session.commit()
    return jsonify(student.to_json())


@app.route("/delete_student/<int:usn>", methods=["GET"])
@jwt_required()
def delete_student(usn):
    student = Student.query.filter_by(usn=usn).first()
    db.session.delete(student)
    db.session.commit()
    return jsonify({"msg": "Record of student with usn "+usn+" has been deleted sucessfully."})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
