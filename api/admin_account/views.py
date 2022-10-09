from flask_restx import Resource,fields,Namespace
from ..admin_account.admin_model import AdminAccount
from ..models.patients_model import Patient
from ..models.doctors_model import Doctor
from ..models.music_model import Musique
from ..models.categorie_model import Category

from flask import  abort,request,jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity
from http import HTTPStatus

"""
views for Admin views CRUD for Admin Account ,add doctor , manage other endpoint
"""

admin_view=Namespace("admin",description="Endpoint for compte admin ")





@admin_view.route("/auth/signup")
class SignUpAdmin(Resource):
    def post(self):
        pass


@admin_view.route("/auth/login")
class LoginAmin(Resource):
    def post(self):
        pass


@admin_view.route("/auth/reset_password")
class ResetPassword(Resource):
    def post(self):
        pass

@admin_view.route("/auth/refresh-token")
class RefreshToken(Resource):
    def Post(self):
        pass

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