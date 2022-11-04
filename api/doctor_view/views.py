from email import message
from flask_restx import Resource,fields,Namespace
from api.models.experiences_model import Experience
from ..models.patients_model import Patient
from ..models.doctors_model import Doctor
from ..models.image_doctors import ImageDoctor
from ..models.token_doctor import TokenDoctor
from ..models.appointments_model import Appointment
from flask import  abort,request,jsonify,Response
from flask_jwt_extended import create_refresh_token,create_access_token,jwt_required,get_jwt_identity
from http import HTTPStatus
from datetime import datetime, timedelta
from flask_mail import Message
from ..utils import mail
import os
from ..models.cabinet_model import Cabinet
from werkzeug.utils import secure_filename
from flask import send_from_directory
from ..doctor_view.sendmessage import send_message




doctor_view=Namespace("doctor",description="Endpoint for Doctor user ")


####################### Authentification ########################

login_model =doctor_view.model(
    "login_request",{
        "email":fields.String(required=True),
        "password":fields.String(required=True)
    }
)
login_response = doctor_view.model(
    "login_response",{
        "status_code":fields.Integer(),
        "session":fields.Boolean(),
        "access_token":fields.String(),
        "refresh_token":fields.String(),
        "expire_in":fields.DateTime()
    }
)
########## add hash password ################
@doctor_view.route("/auth/login")
class LoginDoctor(Resource):
    @doctor_view.expect(login_model)
   
    @doctor_view.marshal_with(login_response,code=200)
    def post(self):
        data=request.get_json()
        email=data.get("email")
        password=data.get("password")
        doctor :Doctor=Doctor.query.filter_by(email=email).first()
        if doctor is not None and doctor.password== password:
            token =TokenDoctor.query.filter_by(doctor_id=doctor.id).first()
            access_token=create_access_token(identity=doctor.username)
            refresh_token=create_refresh_token(identity=doctor.username)
            expire =  datetime.utcnow()
            expire +=  timedelta(hours=23)
            if token is None:
                token=TokenDoctor(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    doctor_id=doctor.id,
                    expired_in=expire)
                token.save()
            else:
                token.access_token=access_token
                token.refresh_token=refresh_token
                token.expired_in=expire
                token.update()
            doctor.is_logged=True
            doctor.update()
            result={
                "status_code":HTTPStatus.OK,
                "access_token":access_token,
                "refresh_token":refresh_token,
                "session":True,
                "expire_in":token.expired_in
            }
            return result
        return abort(404, description="email or password wrong")

####################### Log out #################################
logout_model=doctor_view.model(
    "logout_model",{
         
        "session":fields.Boolean(),
        "message":fields.String()
    }
)
 
@doctor_view.route("/auth/logout")
class ResetPassword(Resource):
    @jwt_required()
    @doctor_view.marshal_with(logout_model)
    def post(self):
        username=get_jwt_identity()
        user:Doctor=Doctor.query.filter_by(username=username).first()
        token:TokenDoctor=TokenDoctor.query.filter_by(doctor_id=user.id).first()
        if token :
            token.delete()
        user.is_logged=False
        user.last_session=datetime.utcnow()
        user.update()
        token.delete()
        response={
        "session":False,
        "message":"user sign-out with succes"
        }
        return response

###################### Auth reset password ##############################

reset_model=doctor_view.model(
    "reset_model",{
        "email":fields.String(required=True,)
    }
)

reset_response=doctor_view.model(
    "reset_response",{
        "status_code":fields.Integer(),
        "message":fields.String()
    }
)

@doctor_view.route("/auth/reset-password")
class ResetPassword(Resource):

    @doctor_view.expect(reset_model)
    @doctor_view.marshal_with(reset_response)
    def post(self):
        data=request.get_json()
        email=data.get("email")
        user:Doctor=Doctor.query.filter_by(email=email).first()
        if user is None:
            abort(401,"user not found verifier your email")
        msg=Message("Reset password For user account",sender=os.getenv("MAIL_USERNAME"),recipients=[f"{user.email}"])
        password=f"Password123*@{user.username[0:2]}????{user.email[0:4]}"
        user.password=password
        user.update()
        msg.body=F"bienvenue chez auth OnePeace Psy api ,{user.first_name}, your password was updated with succes, please login with new password {password}"
        mail.send(msg)
        response={
            "status_code":200,
             "message":"password apdate with succes check your email and reset your password ....."
        }
        return response


###################### refresh Token ########################

@doctor_view.route("/refresh")
class Refresh(Resource):
    @jwt_required(refresh=True)
    @doctor_view.marshal_with(login_response,code=200)
    def post(self):
        username=get_jwt_identity()
        doctor:Doctor=Doctor.query.filter_by(username=username).first()
        access_token=create_access_token(identity=username)
        refresh_token=create_refresh_token(identity=username)
        expire =  datetime.utcnow()
        expire +=  timedelta(hours=23)
        if token is None:
            token=TokenDoctor(
            access_token=access_token,
            refresh_token=refresh_token,
            doctor_id=doctor.id,
            expired_in=expire)
            token.save()
        else:
            token.access_token=access_token
            token.refresh_token=refresh_token
            token.expired_in=expire
            token.update()
        return token 

################### experiences ###############################


#is_occuped=db.Column(db.Boolean(),default=False)

experience_model=doctor_view.model(
    "experience_doctor",{
        "id":fields.Integer(),
        "job_occuped":fields.String(),
        "description":fields.String(),
        "society":fields.String(),
        "date_started":fields.String(),
        "date_finished":fields.String(),
        "is_occuped":fields.Boolean(),
    }
)

experience_input=doctor_view.model(
    "experience_doctor",{
        "job_occuped":fields.String(),
        "description":fields.String(),
        "society":fields.String(),
        "date_started":fields.String(),
        "date_finished":fields.String(),
        "is_occuped":fields.Boolean()
    }
)

@doctor_view.route("/experiences")
class FetchExperiences(Resource):
    @jwt_required()
    @doctor_view.marshal_list_with(experience_model,code=200,envelope="experiences")
    def get(self):
        username=get_jwt_identity()
        doctor:Doctor=Doctor.query.filter_by(username=username).first()
        experience:Experience=Experience.query.filter_by(doctor_id=doctor.id).all()
        print(f"experience are {experience}")
        return experience
    
    @jwt_required()
    @doctor_view.marshal_with(experience_model,code=200)
    def post(self):
        data=request.get_json()
        username=get_jwt_identity()
        doctor:Doctor=Doctor.query.filter_by(username=username).first()
        if data.get("job_occuped") is None :
            return abort(404,"job_occuped is empty")
        if data.get("society") is None :
            return abort(404,"society is empty")
        if data.get("date_started") is None :
            return abort(404,"date_started is empty")
        experience:Experience=Experience(
            job_occuped=data.get("job_occuped"),
            description=data.get("description"),
            society=data.get("society"),
            date_started=data.get("date_started"),
            date_finished=data.get("date_finished"),
            doctor_id=doctor.id
        )
        experience.save()
        return experience

@doctor_view.route("/experience/<int:id>")
class UpdateExperience(Resource):
    @jwt_required()
    @doctor_view.marshal_with(experience_model,code=200)
    def put(self,id):
        data=request.get_json()
        experience:Experience=Experience.query.filter_by(id=id).first()
        if data.get("job_occuped") is None :
            return abort(404,"job_occuped is empty")
        if data.get("society") is None :
            return abort(404,"society is empty")
        if data.get("date_started") is None :
            return abort(404,"date_started is empty")
        experience.description=data.get("description")
        experience.job_occuped=data.get("job_occuped")
        experience.date_finished=data.get("date_finished")
        experience.is_occuped=data.get("is_occuped")
        experience.society=data.get("society")
        experience.date_started=data.get("date_started")
        experience.update()
        return experience
    @jwt_required()
    def delete(self,id):
        experience:Experience=Experience.query.filter_by(id=id).first()
        if experience is None:
            return abort(404,"experience not founded")
        experience.delete()
        return jsonify(
            message="experience was delete with success"
        )

##################### cabinet #############################
cabinet_model=doctor_view.model(
    "cabinet_model",{
        "id":fields.Integer(),
        "cabinet_address":fields.String(),
        "cabinet_contact":fields.String(),
        "time_openning":fields.String(),
        "time_closed":fields.String(),
    }
)


@doctor_view.route("/cabinets")
class CabinetFetchAndPost(Resource):
    @jwt_required()
    @doctor_view.marshal_list_with(cabinet_model,code=200,envelope="cabinets")
    def get(self):
        username=get_jwt_identity()
        doctor:Doctor=Doctor.query.filter_by(username=username).first()
        cabinet:Cabinet=Cabinet.query.filter_by(doctor_id=doctor.id).all()
        return cabinet
    
    @jwt_required()
    def post(self):
        username=get_jwt_identity()
        doctor:Doctor=Doctor.query.filter_by(username=username).first()
        data=request.get_json()
        if data.get("cabinet_address") is None :
            return abort(404,"cabinet_address is empty")
        if data.get("cabinet_contact") is None :
            return abort(404,"cabinet_contact is empty")
        if data.get("time_openning") is None :
            return abort(404,"time_openning is empty")
        if data.get("time_closing") is None :
            return abort(404,"time_closing is empty")
        cabinet_address=data.get("cabinet_address")
        cabinet_contact=data.get("cabinet_contact")
        time_opning=data.get("time_openning")
        time_closed=data.get("time_closing")
        cabinet:Cabinet=Cabinet(
            cabinet_address=cabinet_address,
            cabinet_contact=cabinet_contact,
            time_opning=time_opning,
            time_closed=time_closed,
            doctor_id=doctor.id
        )
        cabinet.save()
        return jsonify(message="cabinet add with succes")

@doctor_view.route("/cabinet/<int:id>")
class Cabinet(Resource):
    @jwt_required()
    def get(self,id):
        username=get_jwt_identity()
        doctor:Doctor=Doctor.query.filter_by(username=username).first()
        cabinet:Cabinet=Cabinet.query.filter_by(doctor_id=doctor.id).filter_by(id=id).first()
        return cabinet
        
    @jwt_required()
    def put(self,id):
        cabinet:Cabinet=Cabinet.query.filter_by(id=id).first()
        data=request.get_json()
        cabinet_address=data.get("cabinet_address")
        cabinet_contact=data.get("cabinet_contact")
        time_opning=data.get("time_openning")
        time_closed=data.get("time_closing")
        if cabinet_address is None or cabinet_address==" ":
            return abort(404,"cabinet_address is empty")
        if cabinet_contact is None or int(cabinet_contact)<8:
            return abort(404,"cabinet_contact is invalide")
        if time_opning is None or time_opning==" " :
            return abort(404,"time_openning is empty")
        if time_closed is None or time_closed==" " :
            return abort(404,"time_closed is empty")
        cabinet.cabinet_address=cabinet_address,
        cabinet.cabinet_contact=cabinet_contact,
        cabinet.time_opning=time_opning,
        cabinet.time_closed=time_closed,
        cabinet.upadate()
        return jsonify(
            message="cabinet update with success"
        )

    @jwt_required()
    def delete(self,id):
        username=get_jwt_identity()
        doctor:Doctor=Doctor.query.filter_by(username=username).first()
        cabinet:Cabinet=Cabinet.query.filter_by(doctor_id=doctor.id).filter_by(id=id).first()
        if cabinet is None:
            cabinet.delete()
            return jsonify(message="cabinet address delete with success")
        return abort(404,"cabinet not found")
###################### appointment #############################

appoint_response=doctor_view.model(
    "Appoint_Response",{
        "id":fields.Integer(),
        "duration":fields.String(),
        "hour_appoint":fields.String(),
        "date_appoint":fields.String(),
        "description":fields.String(),
        "create_at":fields.DateTime(),
        "validation":fields.String(),
        "patient_id":fields.Integer()
    }
)
@doctor_view.route("/appointments")
class FetchAppointment(Resource):
    @jwt_required()
    #@doctor_view.marshal_list_with(appoint_response,code=200)
    def get(self):
        resultapp=[]
        username=get_jwt_identity()
        doctor:Doctor=Doctor.query.filter_by(username=username).first()
        appoint:Appointment=Appointment.query.filter_by(doctor_id=doctor.id).order_by(Appointment.validation).all()
        for app in appoint:
            patient:Patient=Patient.query.filter_by(id=app.patient_id).first()
            result={
                "id":app.id,
                "duration":app.duration,
                "date_appoint":app.date_appoint,
                "hour_appoint":app.hour_appoint,
                "patient_name":patient.first_name,
                "patient_lastname":patient.last_name,
                "number_phone":patient.number_phone,
                "is_logged":patient.is_logged,
                "cnam_code":patient.cnam_code,
                "urlimage":patient.urlimage,
                "validation":app.validation
            }
            resultapp.append(result)
        return resultapp

@doctor_view.route("/appointment")
class FetchAppointment(Resource):
    @jwt_required()
    def get(self):
        username=get_jwt_identity()
        doctor:Doctor=Doctor.query.filter_by(username=username).first()
        data=request.get_json()
        id=data.get("id")
        if id is None:
            return abort(404,"Appointment is not exist")
        appoint:Appointment=Appointment.query.filter_by(doctor_id=doctor.id).filter_by(id=id).first()
        if appoint is None:
            return abort(404,"not appointment found")
        patient:Patient=Patient.query.filter_by(id=appoint.patient_id).first()
        result={
            "duration":appoint.duration,
            "date_appoint":appoint.date_appoint,
            "hour_appoint":appoint.hour_appoint,
            "patient_name":patient.first_name,
            "patient_lastname":patient.last_name,
            "number_phone":patient.number_phone,
            "is_logged":patient.is_logged,
            "cnam_code":patient.cnam_code,
            "urlimage":patient.urlimage,
            "validation":appoint.validation
        }
        return result
    
    @jwt_required()
    def put(self):
        username=get_jwt_identity()
        doctor:Doctor=Doctor.query.filter_by(username=username).first()
        data=request.get_json()
        id=data.get("id")
        if id is None:
            return abort(404,"Appointment is not exist")
        validation=data.get("validation")
        if validation is None:
            return abort(404,"validation is empty")
        appoint:Appointment=Appointment.query.filter_by(doctor_id=doctor.id).filter_by(id=id).first()
        if appoint is None:
            return abort(404,"there is not appointment to updated")
        appoint.validation=validation
        appoint.update()
        if appoint.validation=="validate":
            send_message(27916650,appoint.date_appoint)
        result={
            "message":" Appointment was update with success",
            "validation":appoint.validation
        }
        return result
    
   


########################### profil doctor #######################

image_model=doctor_view.model(
    "image_model",{
        "id":fields.Integer(),
        "filename":fields.String(),
        "created_at":fields.DateTime(),
    }
)

doctor_model=doctor_view.model(
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
        "images":fields.List(fields.Nested(image_model)),
        "cabinets":fields.List(fields.Nested(cabinet_model)),
        "experiences":fields.List(fields.Nested(experience_model)),
        "appoint":fields.List(fields.Nested(appoint_response)),
    }
)
doctor_update=doctor_view.model(
    "patient_update",{
        "first_name":fields.String(),
        "last_name":fields.String(),
        "number_phone":fields.Integer(),
        "about":fields.String(),
        "is_active":fields.Boolean(),
        "is_disponible":fields.Boolean(),
         "price":fields.Float(),
    }
)

imageView=Namespace("images",description="Endpoint for Images view")
ALLOWED_EXTENSIONS = {  'png', 'jpg', 'jpeg', 'gif'}

BASE_DIR=os.path.dirname(os.path.realpath(__file__))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@doctor_view.route("/upload")
class Upload(Resource):
    @jwt_required()
    def post(self):
        username=get_jwt_identity()
        doctor:Doctor=Doctor.query.filter_by(username=username).first()
        if 'file' not in request.files:
            return abort(404,"No file part")
        file=request.files["file"]
        if file.filename == '':
            return abort(401,"no selected file")
        name=file.filename
        image=ImageDoctor.query.filter_by(filename=name).first()
        if image :
            return abort(404,"file already exist")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join("/Users/aminemejri/Desktop/flask copie/api/uploads", filename))
            imageModel=ImageDoctor(
             filename=filename,
             patient_id=doctor.id
                ).save()
            doctor.urlimage=filename
            doctor.update()
        return jsonify(message="file upload witth success",filename=filename)




@doctor_view.route("/uploads/<filename>")
class Download(Resource):
   # @jwt_required()
    def get(self,filename):
        return send_from_directory("uploads",
                           filename)

    @jwt_required()
    def delete(self,filename):
        file=str(filename)
        path_file=os.path.join("/Users/aminemejri/Desktop/flask/api/uploads/",file)
        image:ImageDoctor= ImageDoctor.query.filter_by(filename=file).first()
        if image is None:
            return abort(401,"image does not existe")
        if os.path.exists(path_file):
            os.remove(path_file)
            image.delete()
            print("########### ok ")
        else:
            print(f"The file {file} does not exist")
        return "file deleted with succes"



@doctor_view.route("/auth/me")
class FetchDoctor(Resource):
    @jwt_required()
    @doctor_view.marshal_with(doctor_model)
    def get(self):
        username=get_jwt_identity()
        doctor:Doctor=Doctor.query.filter_by(username=username).first()
        return doctor

    @jwt_required()
    @doctor_view.marshal_with(doctor_model,code=200)
    @doctor_view.expect(doctor_update)
    def put(self):
        data=request.get_json()
        username=get_jwt_identity()
        doctor:Doctor=Doctor.query.filter_by(username=username).first()
        first_name=data.get("first_name")
        last_name=data.get("last_name")
        number_phone=data.get("number_phone")
        about=data.get("about")
        is_active=data.get("is_active")
        is_disponible=data.get("is_disponible")
        doctor.first_name=first_name
        doctor.last_name=last_name
        doctor.number_phone=number_phone
        doctor.about=about
        doctor.is_active=is_active
        doctor.is_disponible=is_disponible
        doctor.update()
        return doctor
    @jwt_required()
    def delete(self):
        username=get_jwt_identity()
        doctor:Doctor=Doctor.query.filter_by(username=username).first()
        if doctor:
            doctor.delete()
            return jsonify(message="patient deleted with succes")
        return abort(404,"doctor account not found")

