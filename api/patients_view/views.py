from ast import Or
import code
from curses import pair_content
from email import message
from pydoc import doc
from flask_restx import Resource,fields,Namespace
from flask_jwt_extended import create_refresh_token,create_access_token,jwt_required,get_jwt_identity
from werkzeug.security import check_password_hash,generate_password_hash
from ..models.patients_model import Patient
from flask import  abort,request,jsonify,Response
from flask_jwt_extended import jwt_required,get_jwt_identity
from http import HTTPStatus
from random import randint
from ..utils import mail
from datetime import datetime,timedelta
from flask_mail import Message
from ..models.token_patient import AccesToken
from ..models.categorie_model import Category
from ..models.music_model import Musique
from ..models.appointments_model import Appointment
from ..models.image_patient import ImageModel
from ..models.doctors_model import Doctor
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory







patient_view=Namespace("patient",description="endpoint for patient ")


####################### sign up for patient ##########################

signUp_model=patient_view.model(
    "Register_Model",{
        "username":fields.String(required=True,description="username for patient, must be unique "),
        "email":fields.String(required=True,description="email for patient ,must be unique"),
        "password":fields.String(required=True,description="password for patient account"),
        "first_name":fields.String(required=True),
        "last_name":fields.String(required=True)
    }
)
signup_response=patient_view.model(
    "Register_Response",{
        "message":fields.String(),
    }
)

@patient_view.route("/auth/sign-up")
class SignUp(Resource):
    @patient_view.expect(signUp_model)
    @patient_view.marshal_with(signup_response)
    def post(self):
        data=request.get_json()
        if data is None:
            return abort(401,"data is emty")
        filter=Patient.query.filter_by(username=data.get("username")).first()
        filter_1=Patient.query.filter_by(email=data.get("email")).first()
        filter_2=Doctor.query.filter_by(email=data.get("email")).first()
        code_generate=randint(11111,99999)
        if filter is not None:
            abort(401,"username already exist")
        if filter_1 is not None:
            abort(401,"email already exist")
        if filter_2 is not None:
            abort(401,"email already used ")
        code_generate=randint(11111,99999)
        user:Patient=Patient(
            username=data.get("username"),
            email=data.get("email"),
            password=generate_password_hash(data.get("password")),
            code=code_generate,
        )
        mail.connect()
        msg=Message("registration user account",sender="onepeace2023@gmail.com",recipients=[f"{user.email}"])
        msg.body=f"bienvenue chez OnePeace Patient ,{user.first_name} {user.last_name} creat an account with succes, please verify your account before login with code identif {user.code}"
        mail.send(msg)
        user.save()
        response={
            "message":"user created with succes please check your email to verifie your  account  "
        }
        return  response
################################ login endpoint #######################

login_model=patient_view.model(
    "login_request",{
        "email":fields.String(required=True),
        "password":fields.String(required=True)
    }
)
login_response=patient_view.model(
    "login_response",{
        "session":fields.Boolean(),
        "access_token":fields.String(),
        "refresh_token":fields.String(),
        "expire_in":fields.DateTime()
    }
)

@patient_view.route("/auth/login")
class Login(Resource):
    @patient_view.expect(login_model)
    @patient_view.marshal_with(login_response)
    def post(self):
        data=request.get_json()
        email=data.get("email")
        password=data.get("password")
        user :Patient=Patient.query.filter_by(email=email).first()
        if user is not None and check_password_hash(user.password,password) :
            if user.is_verify :
                token =AccesToken.query.filter_by(patient_id=user.id).first()
                access_token=create_access_token(identity=user.username)
                refresh_token=create_refresh_token(identity=user.username)
                expire =  datetime.utcnow()
                expire +=  timedelta(hours=23)
                if token is None:
                    token=AccesToken(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    patient_id=user.id,
                    expired_in=expire)
                    token.save()
                else:
                    token.access_token=access_token
                    token.refresh_token=refresh_token
                    token.expired_in=expire
                    token.update()
                user.is_logged=True
                user.update()
                result={
                "access_token":access_token,
                "refresh_token":refresh_token,
                "session":True,
                "expire_in":token.expired_in
                }
                return result
            else:
                return abort(404,"Account patient is not verify , please check your email account and verifie your email address")
        return abort(404,"verifie your email or password wrong")

################### log-out endpoint ######################
 
logout_model=patient_view.model(
    "logout_model",{
        "status_code":fields.Integer(),
        "session":fields.Boolean(),
        "message":fields.String()
    }
)
 
@patient_view.route("/auth/logout")
class LogOut(Resource):
    @jwt_required()
    @patient_view.marshal_with(logout_model)
    def post(self):
        username=get_jwt_identity()
        user:Patient=Patient.query.filter_by(username=username).first()
        token:AccesToken=AccesToken.query.filter_by(patient_id=user.id).first()
        if token :
            token.delete()
        user.is_logged=False
        user.last_session=datetime.utcnow()
        user.update()
        response={
        "status_code":HTTPStatus.OK,
        "session":False,
        "message":"user sign-out with succes"
        }
        return response

#################### verifie account endpoint ########################

code_model=patient_view.model(
    "sender_code",{
        "code_verification":fields.Integer(required=True)
    }
)

code_response=patient_view.model(
    "Result",{
    "message":fields.String(),
    }
)


@patient_view.route("/auth/verify-account")
class Verify(Resource):
    @patient_view.marshal_with(code_response)
    @patient_view.expect(code_model)
    def post(self):
        data=request.get_json()
        code=int(data.get("code"))
        user=Patient.query.filter_by(code=code).first()
        if user :
            user.is_verify=True
            user.update()
            response={
                "message":"Account is verifie with success",
            }
            return response
        abort(401,"try to verifie your email address to sign in")

############################## Reset password Endpoint ################################

reset_model=patient_view.model(
    "reset_model",{
        "email":fields.String(required=True,)
    }
)

reset_response=patient_view.model(
    "reset_response",{
        "message":fields.String()
    }
)

@patient_view.route("/auth/reset-password")
class LogOut(Resource):
    @patient_view.expect(reset_model)
    @patient_view.marshal_with(reset_response)
    def post(self):
        data=request.get_json()
        email=data.get("email")
        if email is None or "":
            return abort(401,"entrer your email address")
        user:Patient=Patient.query.filter_by(email=email).first()
        if user is None:
            return abort(401,"user not found verifier your email")
        msg=Message("Reset password For user account",sender=os.getenv("MAIL_USERNAME"),recipients=[f"{user.email}"])
        password=f"Password123*@{user.username[0:2]}????{user.email[0:4]}"
        user.password=generate_password_hash(password)
        user.update()
        msg.body=F"bienvenue chez auth flask api ,{user.first_name}, your password was updated with succes, please login with new password {password}"
        mail.send(msg)
        response={
             "message":"password apdate with succes check your email and reset your password ....."
        }
        return response

######################### refresh Token ##############################
@patient_view.route("/refresh")
class Refresh(Resource):
    @jwt_required(refresh=True)
    @patient_view.marshal_with(login_response,code=200)
    def post(self):
        username=get_jwt_identity()
        patient:Patient=Patient.query.filter_by(username=username).first()
        access_token=create_access_token(identity=username)
        refresh_token=create_refresh_token(identity=username)
        expire =  datetime.utcnow()
        expire +=  timedelta(hours=23)
        token:AccesToken=AccesToken.query.filter_by(patient_id=patient.id).first()
        if token is None:
            token=AccesToken(
            access_token=access_token,
            refresh_token=refresh_token,
            patient_id=patient.id,
            expired_in=expire)
            token.save()
        else:
            token.access_token=access_token
            token.refresh_token=refresh_token
            token.expired_in=expire
            token.update()
        result={
                "access_token":access_token,
                "refresh_token":refresh_token,
                "session":True,
                "expire_in":token.expired_in
                }
        return result
        

###################### complet-profil patient ##################

# number_phone=db.Column(db.Integer())
# first_name=db.Column(db.String(50) )
 #last_name=db.Column(db.String(50), )
 #cnam_code=db.Column(db.String(50),)

complet_model=patient_view.model(
    "patient_complet_model",{
        "first_name":fields.String(requires=True),
        "last_name":fields.String(),
        "number_phone":fields.Integer(),
        "cnam_code":fields.String() ,
         
    }
)

complet_response=patient_view.model(
    "profil_complet",{
        "message":fields.String()
    }
)

@patient_view.route("/complet-profil")
class Complet(Resource):
    @jwt_required()
    @patient_view.expect(code_model)
    @patient_view.marshal_with(complet_response,200)
    def post(self):
        username=get_jwt_identity()
        filter:Patient=Patient.query.filter_by(username=username).first()
        data=request.get_json()
        filter.first_name=data.get("first_name")
        filter.last_name=data.get("last_name")
        filter.cnam_code=data.get("cnam_code")
        filter.number_phone=data.get("number_phone")
        filter.update()
        result= {
            "message":"profil completed with succes"
        }
        return result



######################## music for patient end  point ###################

musique_model=patient_view.model(
    "musique_model",{
        "id":fields.Integer(),
        "title":fields.String(),
         
        "url":fields.String(),
        "category_id":fields.Integer()
    }
)

@patient_view.route("/musiques")
class FetchAllMusic(Resource):
   # @jwt_required()
    @patient_view.marshal_list_with(musique_model,code=200,envelope="musiques")
    def get(self):
        musique=Musique.query.all()
        return musique



####################### categorie for patient end point #################
categorie_model=patient_view.model(
    "categorie_model",{
        "id":fields.Integer(),
        "name":fields.String(),
        "image_url":fields.String(),
        "create_at":fields.DateTime(),
        "musiques":fields.List(fields.Nested(musique_model))
    }
)

@patient_view.route("/categories")
class FetchAllCategorie(Resource):
   # @jwt_required()
    @patient_view.marshal_list_with(categorie_model,code=200,envelope="categories")
    def get(self):
        categorie=Category.query.all()
        return categorie

@patient_view.route("/categorie/<name>")
class FetchById(Resource):
    #@jwt_required()
    @patient_view.marshal_with(categorie_model)
    def get(self,name):
        categorie= Category.query.filter_by(name=name).first()
        if categorie is None:
            abort(404,"category not found")
        return categorie

##################### doctor endpoint :list ########################

image_cabinet_model=patient_view.model(
    "cabinet_image",{
        "id":fields.Integer(),
        "filename":fields.String(),
        "created_at":fields.DateTime()
    }
)
cabinet_model=patient_view.model(
    "cabinet_model",{
        "id":fields.Integer(),
        "cabinet_address":fields.String(),
        "cabinet_contact":fields.String(),
        "time_openning":fields.String(),
        "time_closed":fields.String(),
    }
)

experience_model=patient_view.model(
    "experience_doctor",{
        "id":fields.Integer(),
        "job_occuped":fields.String(),
        "description":fields.String(),
        "society":fields.String(),
        "date_started":fields.String(),
        "date_finished":fields.String()
    }
)

doctor_model=patient_view.model(
    "fetch_doctors",{
        "id":fields.Integer(),
        "email":fields.String(),
        "urlimage":fields.String(),
        "number_phone":fields.Integer(),
        "first_name":fields.String(),
        "last_name":fields.String(),
        "about":fields.String(),
        "is_disponible":fields.Boolean(),
        "rating":fields.Integer(),
        "price":fields.Float(),
        "cabinets":fields.List(fields.Nested(cabinet_model)),
        "experiences":fields.List(fields.Nested(experience_model))
    }
)

@patient_view.route("/doctors")
class FetchallDoctor(Resource):
   # @jwt_required()
    @patient_view.marshal_list_with(doctor_model,code=200,envelope="doctors")
    def get(self):
        doctors:Doctor=Doctor.query.all()
        return doctors


@patient_view.route("/doctor/<name>")
class FetchallDoctor(Resource):
   # @jwt_required()
    @patient_view.marshal_list_with(doctor_model,code=200,envelope="doctors")
    def get(self,name):
        doctors:Doctor=Doctor.query.filter(Doctor.first_name.startswith(name)).all()
        doctors_1:Doctor=Doctor.query.filter(Doctor.last_name.startswith(name)).all()
        if doctors  :
            return doctors
        if doctors_1:
            return doctors_1
        return abort(404,"no doctor founded")


################### appointment endpoint ########################
appoint_request=patient_view.model(
    "appoint_model",{
        "duration":fields.String(),
          "hour_appoint":fields.String(),
          "date_appoint":fields.String(),
          "description":fields.String(),
           "doctor_id":fields.Integer(),
    }
)

appoint_response=patient_view.model(
    "Appoint_Response",{
        "duration":fields.String(),
        "hour_appoint":fields.String(),
        "date_appoint":fields.String(),
        "description":fields.String(),
        "create_at":fields.DateTime(),
        "validation":fields.String(),
        "doctor_id":fields.Integer(),
        "patient_id":fields.Integer()
    }
)

@patient_view.route("/appointment")
class AppointmentPost(Resource):
    @jwt_required()
    @patient_view.marshal_with(appoint_response)
    @patient_view.expect(appoint_request)
    def post(self):
        username=get_jwt_identity()
        patient:Patient=Patient.query.filter_by(username=username).first()
        data=request.get_json()
        date_appoint=data.get("date_appoint")
        hour_appoint=data.get("hour_appoint")
        duration=data.get("duration")
        description=data.get("description")
        doctor_id=data.get("doctor_id")
        doctor:Doctor=Doctor.query.filter_by(id=doctor_id).first()
        if   hour_appoint is None:
            return abort(404,"add date appointment ")
        if  date_appoint is None:
            return abort(404,"add date appointment ")
        if  doctor_id is None:
            return abort(404,"add doctor ")
        if doctor is None :
            return abort(404,"doctor not found")
        filter:Appointment=Appointment.query.filter_by(doctor_id=doctor_id).filter_by(date_appoint=date_appoint).first()
        if filter:
            return abort(404,"doctor aleardy have an appointment")
        appointment:Appointment = Appointment(
             date_appoint=data.get("date_appoint"),
             hour_appoint=data.get("hour_appoint"),
             description=data.get("description"),
             doctor_id=data.get("doctor_id"),
             patient_id=patient.id,
             duration=data.get("duration")
        )
        appointment.save()
        return appointment
    @jwt_required()
    @patient_view.marshal_list_with(appoint_response,code=200,envelope="appoints")
    def get(self):
        username=get_jwt_identity()
        patient:Patient=Patient.query.filter_by(username=username).first()
        appoint:Appointment=Appointment.query.filter_by(patient_id=patient.id).all()
        return appoint
    
@patient_view.route("/appointment/<int:id>")
class DeleteApp(Resource):
    @jwt_required()
    def delete(self,id):
      username=get_jwt_identity()
      patient:Patient=Patient.query.filter_by(username=username).first()
      appoint:Appointment=Appointment.query.filter_by(patient_id=patient.id).filter_by(id=id).first()
      if appoint:
          appoint.delete()
          return jsonify(
              message="appoint was delete with succes"
          )
      return abort(404,"no appointment found ")
    
    @jwt_required()
    def get(self,id):
        username=get_jwt_identity()
        patient:Patient=Patient.query.filter_by(username=username).first()
        appoint:Appointment=Appointment.query.filter_by(patient_id=patient.id).filter_by(id=id).first()
        if appoint is None:
            return abort(404,"appointment not found")
        doctor:Doctor=Doctor.query.filter_by(id=appoint.doctor_id).first()
        result={
            "duration":appoint.duration,
            "hour_appoint":appoint.hour_appoint,
            "date_appoint":appoint.date_appoint,
            "description":appoint.description,
            "create_at":appoint.create_at,
            "validation":appoint.validation,
            "doctor_name":doctor.first_name,
            "doctor_last_name":doctor.last_name,
            "doctor":doctor.number_phone,
            "doctor_price":doctor.price,
        }
        return result

######################## profile enf point me ######################

image_model=patient_view.model(
    "image_model",{
        "id":fields.Integer(),
        "filename":fields.String(),
        "created_at":fields.DateTime(),
    }
)

patient_model=patient_view.model(
    "patient model",{
        "id":fields.Integer(),
        "email":fields.String(),
        "first_name":fields.String(),
        "last_name":fields.String(),
        "number_phone":fields.Integer(),
        "cnam_code":fields.String(),
        "is_active":fields.Boolean(),
        "is_verify":fields.Boolean(),
        "is_logged":fields.Boolean(),
        "urlimage":fields.String(),
        "is_blocked":fields.Boolean(),
        "images":fields.List(fields.Nested(image_model)),
        "appointments":fields.List(fields.Nested(appoint_response))
    }
)
patient_update=patient_view.model(
    "patient_update",{
         "first_name":fields.String(),
        "last_name":fields.String(),
        "number_phone":fields.Integer(),
        "cnam_code":fields.String(),
        "is_active":fields.Boolean(),
    }
)

@patient_view.route("/me")
class FetchPatient(Resource):
    @jwt_required()
    @patient_view.marshal_with(patient_model)
    def get(self):
        username=get_jwt_identity()
        patient:Patient=Patient.query.filter_by(username=username).first()
        return patient
    
    @jwt_required()
    @patient_view.marshal_with(patient_model,code=200)
    @patient_view.expect(patient_update)
    def put(self):
        data=request.get_json()
        username=get_jwt_identity()
        patient:Patient=Patient.query.filter_by(username=username).first()
        first_name=data.get("first_name")
        last_name=data.get("last_name")
        number_phone=data.get("number_phone")
        cnam_code=data.get("cnam_code")
        is_active=data.get("is_active")
        patient.first_name=first_name
        patient.last_name=last_name
        patient.number_phone=number_phone
        patient.cnam_code=cnam_code
        patient.is_active=is_active
        patient.update()
        return patient
    @jwt_required()
    def delete(self):
        username=get_jwt_identity()
        patient:Patient=Patient.query.filter_by(username=username).first()
        return jsonify(message="patient deleted with succes")



########## update profil , upload image, cnam ,num telephon, ############### 

imageView=Namespace("images",description="Endpoint for Images view")
ALLOWED_EXTENSIONS = {  'png', 'jpg', 'jpeg', 'gif'}

BASE_DIR=os.path.dirname(os.path.realpath(__file__))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@patient_view.route("/upload")
class Upload(Resource):
    @jwt_required()
    def post(self):
        username=get_jwt_identity()
        patient:Patient=Patient.query.filter_by(username=username).first()
        if 'file' not in request.files:
            return abort(404,"No file part")
        file=request.files["file"]
        if file.filename == '':
            return abort(401,"no selected file")
        name=secure_filename(file.filename)
        image:ImageModel=ImageModel.query.filter_by(filename=name).first()
        if image :
            return abort(404,"file already exist")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join("/Users/aminemejri/Desktop/flask copie/api/uploads", filename))
            imageModel=ImageModel(
             filename=filename,
             patient_id=patient.id
                ).save()
            patient.urlimage=filename
            patient.update()
        else:
            return  abort(404,"file is not image")
        return jsonify(message="file upload witth success",filename=filename)




@patient_view.route("/uploads/<filename>")
class Download(Resource):
    @jwt_required()
    def get(self,filename):
        return send_from_directory("uploads",
                           filename)

    @jwt_required()
    def delete(self,filename):
        file=str(filename)
        path_file=os.path.join("/Users/aminemejri/Desktop/flask/api/uploads/",file)
        image:ImageModel= ImageModel.query.filter_by(filename=file).first()
        if image is None:
            return abort(401,"image does not existe")
        if os.path.exists(path_file):
            os.remove(path_file)
            image.delete()
            print("########### ok ")
        else:
            print(f"The file {file} does not exist")
        return "file deleted with succes"