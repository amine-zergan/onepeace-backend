from ..utils import db ,admin
from datetime import datetime
from flask_admin.contrib.sqla import ModelView


class Doctor(db.Model):
    __tablename__="doctors"
    id=db.Column(db.Integer(),primary_key=True)
    username=db.Column(db.String(100),nullable=False,unique=True)
    urlimage=db.Column(db.String(100))
    email=db.Column(db.String(100),nullable=False,unique=True)
    password=db.Column(db.Text(),nullable=False)
    code=db.Column(db.Integer,nullable=False)
    number_phone=db.Column(db.Integer())
    is_active=db.Column(db.Boolean(),default=True)
    is_blocked=db.Column(db.Boolean(),default=False)
    is_verify=db.Column(db.Boolean(),default=False)
    is_logged=db.Column(db.Boolean(),default=False)
    create_at=db.Column(db.DateTime(),default=datetime.utcnow)
    last_session=db.Column(db.DateTime(),default=datetime.utcnow)
    first_name=db.Column(db.String(50),nullable=False)
    last_name=db.Column(db.String(50),nullable=False)
    about=db.Column(db.String(300))
    is_disponible=db.Column(db.Boolean(),default=True)
    rating=db.Column(db.Integer(),)
    price=db.Column(db.Float())
    tokens=db.relationship("TokenDoctor",backref="token",cascade="all,delete",uselist=False)
    images = db.relationship('ImageDoctor',backref='images', cascade= "all, delete",lazy="dynamic")
    experiences = db.relationship('Experience',backref='experiences', cascade= "all, delete",lazy="dynamic")
    appoint = db.relationship('Appointment',backref='appointments', lazy="dynamic")
    cabinets = db.relationship('Cabinet',backref='cabinets', cascade= "all, delete",lazy="dynamic")
    patients = db.relationship('Patient',backref='patients',lazy="dynamic")
    
    def __repr__(self) :
        return f"doctor  {self.first_name} {self.last_name}"
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

 