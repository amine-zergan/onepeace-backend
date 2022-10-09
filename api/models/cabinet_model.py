
from ..utils import db ,admin
from datetime import datetime
 

class Cabinet(db.Model):
    __tablename__="cabinets"
    id=db.Column(db.Integer(),primary_key=True)
    cabinet_address=db.Column(db.String(100))
    cabinet_contact=db.Column(db.Integer())
    time_openning=db.Column(db.String(),)
    time_closed=db.Column(db.String(),)
    doctor_id = db.Column(db.Integer(), db.ForeignKey('doctors.id'),
        nullable=False)
    def __repr__(self) :
        return f"Cabinet for adress  {self.cabinet_address} user by doctor{self.docotr_id}"
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
 