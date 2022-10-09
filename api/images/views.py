 
from flask_restx import Resource,fields,Namespace
from ..models.image_patient import ImageModel
from ..models.patients_model import Patient
from flask import  abort,request,jsonify
from flask_jwt_extended import jwt_required,get_jwt_identity
from http import HTTPStatus
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory


"""
__ View_Done__
views for Images views CRUD for users 
 id=db.Column(db.Integer(),primary_key=True)
    filename=db.Column(db.String(100),nullable=False)
    created_at=db.Column(db.DateTime(),default=datetime.utcnow)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'),
        nullable=False)
"""

imageView=Namespace("images",description="Endpoint for Images view")
ALLOWED_EXTENSIONS = {  'png', 'jpg', 'jpeg', 'gif'}
BASE_DIR=os.path.dirname(os.path.realpath(__file__))
#model will be save to documentation for Api
image_model=imageView.model(
    "ImageModel",{
        "id":fields.Integer(),
        "filename":fields.String(),
        "created_at":fields.DateTime(),
        "user_id":fields.Integer()
    }
)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@imageView.route("")
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
        name=file.filename
        image=ImageModel.query.filter_by(filename=name).first()
        if image :
            return abort(404,"file already exist")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join("/Users/aminemejri/Desktop/flask/api/uploads", filename))
            imageModel=ImageModel(
                filename=name,
                user_id=patient.id
            ).save()
        return jsonify(message="file upload witth success",filename=filename)
     



@imageView.route('/<filename>')
class Download(Resource):
    @jwt_required()
    def get(self,filename):
        imageModel=ImageModel.query.filter_by(filename=filename).first()
        if imageModel is None:
            abort(401,f"file {filename} not founded")
        return send_from_directory("uploads",
                               filename)
    def put(self,filename):
        pass
    @jwt_required()
    def delete(self,filename):
        file=str(filename)
        path_file=os.path.join("/Users/aminemejri/Desktop/flask/api/uploads/",file)
        image:ImageModel= ImageModel.query.filter_by(filename=file).first()
        if image is None:
            abort(401,"image does not existe")
        if os.path.exists(path_file):
            os.remove(path_file)
            image.delete()
            print("########### ok ")
        else:
            print(f"The file {file} does not exist")
        return "file deleted with succes"
        

@imageView.route('/<int:id>')
class Download(Resource):
    @jwt_required()
    def get(self,id):
        imageModel=ImageModel.query.filter_by(id=id).first()
        if imageModel is None:
            abort(401,f"file not founded")
        return send_from_directory("uploads",
                               imageModel.id)
    def put(self,id):
        #va modifier le nom de image 
        pass
    