

from ..utils import db ,admin
from datetime import datetime


class Patient(db.Model):
     __tablename__="patients"
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
     first_name=db.Column(db.String(50) )
     last_name=db.Column(db.String(50), )
     cnam_code=db.Column(db.String(50),)
     create_at=db.Column(db.DateTime(),default=datetime.utcnow)
     last_session=db.Column(db.DateTime(),default=datetime.utcnow)
     doctor_id = db.Column(db.Integer(), db.ForeignKey('doctors.id'),)
     tokens=db.relationship("AccesToken",backref="token",cascade="all,delete",uselist=False)
     images = db.relationship('ImageModel',backref='images', cascade= "all, delete",lazy="dynamic")
     appointments = db.relationship('Appointment',backref='appointment',lazy="dynamic")
     def __repr__(self) :
        return f"patient  {self.first_name} {self.last_name}"
     def save(self):
        db.session.add(self)
        db.session.commit()

     def update(self):
        db.session.commit()

     def delete(self):
        db.session.delete(self)
        db.session.commit()


 