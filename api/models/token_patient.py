 
 
from ..utils import db ,admin
from datetime import datetime
from flask_admin.contrib.sqla import ModelView
class AccesToken(db.Model):
    __tablename__="tokens"
    id=db.Column(db.Integer(),primary_key=True)
    access_token=db.Column(db.String(),nullable=False)
    refresh_token=db.Column(db.String(),nullable=False)
    expired_in=db.Column(db.DateTime(),nullable=False)
    create_at=db.Column(db.DateTime(),default=datetime.utcnow)
    token_type=db.Column(db.String(),default="bearer")
    
    patient_id = db.Column(db.Integer(), db.ForeignKey('patients.id'),
        nullable=False)
    
    def __repr__(self) :
        return f"token "
    
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()






"""
"access_token": "..."
  "refresh_token": "...",
  "expires_in": 3600,
  "token_type": "bearer"
"""