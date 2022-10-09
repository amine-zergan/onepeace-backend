from ..utils import db ,admin
from datetime import datetime
from flask_admin.contrib.sqla import ModelView



class Category(db.Model):
    __tablename__="categories"
    id=db.Column(db.Integer(),primary_key=True,)
    name=db.Column(db.String(50),nullable=False)
    image_url=db.Column(db.String(),)
    create_at=db.Column(db.DateTime(),default=datetime.utcnow)
    musiques = db.relationship('Musique',backref='musique', cascade= "all, delete",lazy="dynamic")

    def __repr__(self):
        return f" category {self.name}"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

