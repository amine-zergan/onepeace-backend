from ..utils import db  
 
 

class Musique(db.Model):
    __tablename__="musiques"
    id=db.Column(db.Integer(),primary_key=True)
    title=db.Column(db.String(),nullable=False)
    url=db.Column(db.String(100),nullable=False)
    category_id = db.Column(db.Integer(), db.ForeignKey('categories.id'),
        nullable=False)
    def __repr__(self):
        return f"musique {self.title}"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

