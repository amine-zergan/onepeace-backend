
from ..utils import db 
from flask_admin.contrib.sqla import ModelView


class Experience(db.Model):
    __tablename__="experiences"
    id=db.Column(db.Integer(),primary_key=True)
    job_occuped=db.Column(db.String(100),nullable=False)
    description=db.Column(db.String(500))
    society=db.Column(db.String())
    is_occuped=db.Column(db.Boolean(),default=False)
    date_started=db.Column(db.String(),nullable=False)
    date_finished=db.Column(db.String())
    doctor_id = db.Column(db.Integer(), db.ForeignKey('doctors.id'),
        nullable=False)
    def __repr__(self):
        return f"experience {self.job_occuped} for doctor id"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

