 
from flask import Flask
from flask_restx import Api
from .config.config import config_dict
from .utils import db,migrate,jwt,admin
from .utils import mail
from .models.token_patient import AccesToken
from .models.appointments_model import Appointment
from .models.cabinet_model import Cabinet
from .models.experiences_model import Experience
from .models.image_patient import ImageModel
from .models.music_model import Musique
from .models.patients_model import Patient
from .models.doctors_model import Doctor
from .models.image_doctors import ImageDoctor
from .models.categorie_model import Category
from .models.image_doctors import ImageDoctor
from .models.image_patient import ImageModel
from .admin_account.admin_model import AdminAccount
from .models.admin_token import AdminToken
from .models.token_doctor import TokenDoctor
from flask_admin.contrib.sqla import ModelView
from .patients_view.views import patient_view
from .admin_account.views import admin_view
from .doctor_view.views import doctor_view
from flask_admin.contrib.fileadmin import FileAdmin




#application backend :def instance de object Flask 
#api herite de class flask represente flask-restx


def create_app(config=config_dict['dev']):
    app= Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    api=Api(app,title="Api for project PFE Master degree",description="Api for project mobile application ",contact_email="onepeace2023@gmail.com")
    mail.init_app(app)
    migrate.init_app(app,db)
    admin.init_app(app)
    jwt.init_app(app)
    
    api.add_namespace(patient_view,path="/patient")
    api.add_namespace(admin_view,path="/admin_account")
    api.add_namespace(doctor_view,path="/doctor")
    def make_shell_context():
        return {
            "db":db,
            "patient":Patient,
            "doctor":Doctor,
            "experience":Experience,
            "images":ImageModel,
            "imagedoctor":ImageDoctor,
            "category":Category,
            "musique":Musique,
            "cabinet":Cabinet,
            "admin":AdminAccount,
            "adminToken":AdminToken,
            "tokendoctor":TokenDoctor,
        }
    class FileView(FileAdmin):
        can_mkdir=False
        can_delete_dirs=False
        can_download=True
    path="/Users/aminemejri/Desktop/flask copie/api/uploads"
    admin.add_view(ModelView(Musique,db.session))
    
    admin.add_view(ModelView(Experience,db.session))
    admin.add_view(ModelView(Category,db.session))
    admin.add_view(ModelView(Appointment,db.session))
    admin.add_view(ModelView(ImageDoctor,db.session))
    admin.add_view(ModelView(Patient,db.session))
    admin.add_view(ModelView(ImageModel,db.session))
    admin.add_view(ModelView(Doctor,db.session))
    admin.add_view(ModelView(AccesToken,db.session))
     
    
    admin.add_view(ModelView(Cabinet,db.session))
    admin.add_view(FileView(path, '/uploads/', name='Files',))
    return app



