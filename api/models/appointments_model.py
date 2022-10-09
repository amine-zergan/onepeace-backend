

from ..utils import db ,admin
from datetime import datetime




class Appointment(db.Model):
    __tablename__="appointments"
    id=db.Column(db.Integer(),primary_key=True)
    date_appoint=db.Column(db.String(),nullable=False)
    hour_appoint=db.Column(db.String(),nullable=False)
    duration=db.Column(db.String())
    validation=db.Column(db.String(),default="waiting")
    description=db.Column(db.String(200))
    create_at=db.Column(db.DateTime(),default=datetime.utcnow)
    doctor_id = db.Column(db.Integer(), db.ForeignKey('doctors.id'),
         )
    patient_id = db.Column(db.Integer(), db.ForeignKey('patients.id'),
         )
    def __repr__(self) :
        return f" appointent {self.id}"
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

