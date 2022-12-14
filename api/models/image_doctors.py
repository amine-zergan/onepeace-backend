from ..utils import db ,admin
from datetime import datetime
 

class ImageDoctor(db.Model):
    __tablename__="imagedoctors"
    id=db.Column(db.Integer(),primary_key=True)
    filename=db.Column(db.String(),nullable=False)
    created_at=db.Column(db.DateTime(),default=datetime.utcnow)
    doctor_id = db.Column(db.Integer(), db.ForeignKey('doctors.id'),
         )
    def __repr__(self) :
        return f"image name  {self.filename}"
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
