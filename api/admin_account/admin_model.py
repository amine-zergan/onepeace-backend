


from ..utils import db ,admin
from datetime import datetime




class AdminAccount(db.Model):
    __tablename__="adminsaccounts"
    id=db.Column(db.Integer(),primary_key=True)
    username=db.Column(db.String(100),nullable=False,unique=True)
    urlimage=db.Column(db.String(100))
    email=db.Column(db.String(100),nullable=False,unique=True)
    password=db.Column(db.Text(),nullable=False)
    code=db.Column(db.Integer,nullable=False)
    number_phone=db.Column(db.Integer())
    is_active=db.Column(db.Boolean(),default=True)
    first_name=db.Column(db.String(50),nullable=False)
    last_name=db.Column(db.String(50),nullable=False)
    create_at=db.Column(db.DateTime(),default=datetime.utcnow)
    last_session=db.Column(db.DateTime(),default=datetime.utcnow)
    tokens=db.relationship("AdminToken",backref="token",cascade="all,delete",uselist=False)
    images = db.relationship('ImageAdmin',backref='images', cascade= "all, delete",lazy="dynamic")
    def __repr__(self) :
        return f"admin  {self.first_name} {self.last_name}"
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
