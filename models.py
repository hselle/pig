from app import db
from sqlalchemy.dialects.postgresql import JSON


class Result(db.Model):
    __tablename__ = 'formulas'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    sheet_id = db.Column(db.String())


    def __init__(self, title, sheet_id):
        self.title = title
        self.sheet_id = sheet_id

    def __repr__(self):
        return '<id {}>'.format(self.id)
