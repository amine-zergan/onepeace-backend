from lib2to3.pgen2 import token
from flask_restx import Resource,fields,Namespace
from ..admin_account.admin_model import AdminAccount
#from ..models.patients_model import Patient
from admin_model import AdminAccount
from ..models.admin_token import AdminToken
from ..models.doctors_model import Doctor
from ..models.music_model import Musique
from ..models.categorie_model import Category
import os
 
from random import randint
from werkzeug.security import check_password_hash,generate_password_hash
from ..utils import mail
from flask_mail import Message
from flask_jwt_extended import create_refresh_token,create_access_token,jwt_required,get_jwt_identity
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import datetime,timedelta






from flask import  abort,request,jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity
from http import HTTPStatus

"""
views for Admin views CRUD for Admin Account ,add doctor , manage other endpoint
"""

admin_view=Namespace("admin",description="Endpoint for compte admin ")
####################### sign up for admin ##########################

signUp_model=admin_view.model(
    "Register_Model",{
        "username":fields.String(required=True,description="username for admin, must be unique "),
        "email":fields.String(required=True,description="email for admin ,must be unique"),
        "password":fields.String(required=True,description="password for admin account"),
        "first_name":fields.String(required=True),
        "last_name":fields.String(required=True)
    }
)
signup_response=admin_view.model(
    "Register_Response",{
        "message":fields.String(),
        "status_code":fields.Integer(),
    }
)

@admin_view.route("/auth/signup")
class SignUp(Resource):
    @admin_view.expect(signUp_model)
    @admin_view.marshal_with(signup_response)
    def post(self):
        data=request.get_json()
        filter=AdminAccount.query.filter_by(username=data.get("username")).first()
        filter_1=AdminAccount.query.filter_by(email=data.get("email")).first()
        code_generate=randint(11111,99999)
        if filter is not None:
            abort(401,"username already exist")
        if filter_1 is not None:
            abort(401,"email already exist")
        code_generate=randint(11111,99999)
        user:AdminAccount=AdminAccount(
            username=data.get("username"),
            email=data.get("email"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            password=generate_password_hash(data.get("password")),
            urlimage="",
            number_phone=0,
            cnam_code="",
            code=code_generate,
        )
        mail.connect()
        msg=Message("registration user account",sender="onepeace2023@gmail.com",recipients=[f"{user.email}"])
        msg.body=f"bienvenue chez OnePeace Patient ,{user.first_name} {user.last_name} creat an account with succes, please verify your account before login with code identif {user.code}"
        mail.send(msg)
        user.save()
        response={
            "status_code":HTTPStatus.CREATED,
            "message":"user created with succes please check your email to verifie your  account  "
        }
        return  response



################################ login endpoint #######################

login_model=admin_view.model(
    "login_request",{
        "email":fields.String(required=True),
        "password":fields.String(required=True)
    }
)
login_response=admin_view.model(
    "login_response",{
        "status_code":fields.Integer(),
        "session":fields.Boolean(),
        "access_token":fields.String(),
        "refresh_token":fields.String(),
        "expire_in":fields.DateTime()
    }
)

@admin_view.route("/auth/login")
class Login(Resource):
    @admin_view.expect(login_model)
    @admin_view.marshal_with(login_response)
    def post(self):
        data=request.get_json()
        email=data.get("email")
        password=data.get("password")
        user :AdminAccount=AdminAccount.query.filter_by(email=email).first()
        if user is not None and check_password_hash(user.password,password):
            token =AdminToken.query.filter_by(id=user.id).first()
            access_token=create_access_token(identity=user.username)
            refresh_token=create_refresh_token(identity=user.username)
            expire =  datetime.utcnow()
            expire +=  timedelta(hours=23)
            if token is None:
                token=AdminToken(
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
                "status_code":HTTPStatus.OK,
                "access_token":access_token,
                "refresh_token":refresh_token,
                "session":True,
                "expire_in":token.expired_in
            }
            return result
        return abort(HTTPStatus.NOT_FOUND,"verifie your email or password wrong")

################################ reset pw admin #######################

reset_model=admin_view.model(
    "reset_model",{
        "email":fields.String(required=True,)
    }
)

reset_response=admin_view.model(
    "reset_response",{
        "status_code":fields.Integer(),
        "message":fields.String()
    }
)

@admin_view.route("/auth/reset_password")
class ResetPassword(Resource):
    @admin_view.expect(reset_model)
    @admin_view.marshal_with(reset_response)
    def post(self):
        data=request.get_json()
        email=data.get("email")
        if email is None or "":
            return abort(401,"entrer your email address")
        user:AdminAccount=AdminAccount.query.filter_by(email=email).first()
        if user is None:
            return abort(401,"user not found verifier your email")
        msg=Message("Reset password For user account",sender=os.getenv("MAIL_USERNAME"),recipients=[f"{user.email}"])
        user.password=f"Password123*@{user.username[0:2]}????{user.email[0:4]}"
        user.update()
        msg.body=F"bienvenue chez auth flask api ,{user.first_name}, your password was updated with succes, please login with new password {user.password}"
        mail.send(msg)
        response={
            "status_code":HTTPStatus.ok,
             "message":"password apdate with succes check your email and reset your password ....."
        }
        return response

################################ reset pw admin #######################

@admin_view.route("/auth/refresh-token")
class RefreshToken(Resource):
    @jwt_required(refresh=True)
    @admin_view.marshal_with(login_response,code=200)
    def Post(self):
        username=get_jwt_identity()
        admin:AdminAccount=AdminAccount.query.filter_by(username=username).first()
        access_token=create_access_token(identity=username)
        refresh_token=create_refresh_token(identify=username)
        expire= datetime.utcnow()
        expire +=timedelta(hours=23)
        if token is None:
            access_token=access_token
            

################################ reset pw admin #######################

@admin_view.route("/auth/me")
class FetchAdmin(Resource):
    def post(self):
        pass
    
@admin_view.route("/doctors")
class Doctors(Resource):
    def get(self):
        pass
    def post(self):
        pass

@admin_view.route("/doctor/<int:id>")
class DoctorByid(Resource):
    def get(self,id):
        pass
    def put(self,id):
        pass 
    def delete(self,id):
        pass 

@admin_view.route("/doctor/<name>")
class DoctorByName(Resource):
    def get(self,name):
        pass
    def put(self,name):
        pass 
    def delete(self,name):
        pass 



@admin_view.route("/musique")
class MusiqueUpload(Resource):
    def post(self):
        pass
    


@admin_view.route("/categorie")
class CategorieUpload(Resource):
    def post(self):
        pass


@admin_view.route("/patients")
class FetchAllPatient(Resource):
    def get(self):
        pass

@admin_view.route("/patient/id")
class FetchAllPatient(Resource):
    def get(self,id):
        pass