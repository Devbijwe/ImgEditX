
from __init__ import db
from datetime import datetime
from sqlalchemy import inspect


class Users(db.Model):
    __tablename__ = 'users'
    id=db.Column(db.String(50),nullable=False,primary_key=True,unique=True)
    name=db.Column(db.String(50),nullable=False)
    mobile=db.Column(db.String(15),nullable=True,unique=True)
    email=db.Column(db.String(75),nullable=True,unique=True)
    password=db.Column(db.String(50),nullable=False)
    picture=db.Column(db.String(300),nullable=True)
    date=db.Column(db.DateTime, default=datetime.now(),nullable=True)
    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

# class Images(db.Model):
#     __tablename__ = 'images'
#     id=db.Column(db.String(50),nullable=False,primary_key=True,unique=True)
#     userId=db.Column(db.String(50),db.ForeignKey('Users.id'),nullable=False)
#     image=db.Column(db.String(200),nullable=False)
#     details=db.Column(db.String(100),nullable=True)
#     date=db.Column(db.DateTime, default=datetime.now(),nullable=True) 
#     user = db.relationship('Users', backref='images')
#     def toDict(self):
#         return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }  
     
class Images(db.Model):
    __tablename__ = 'images'
    id=db.Column(db.String(50),nullable=False,primary_key=True,unique=True)
    userId=db.Column(db.String(50),db.ForeignKey('users.id'),nullable=False)
    image=db.Column(db.String(200),nullable=False)
    details=db.Column(db.String(100),nullable=True)
    date=db.Column(db.DateTime, default=datetime.now(),nullable=True) 
    user = db.relationship('Users', backref='images')
    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

class Chats(db.Model):
    __tablename__ = 'chats'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True,unique=True)
    userId=db.Column(db.String(50),db.ForeignKey('users.id'),nullable=False)
    sender=db.Column(db.String(50),nullable=False)
    receiver=db.Column(db.String(50),nullable=False)
    msg=db.Column(db.String(250),nullable=False)
    date=db.Column(db.DateTime, default=datetime.now(),nullable=True)
    user = db.relationship('Users', backref='chats')
    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }
