# Credit to The Flask Mega-Tutorial Part IV: Database

from alayatodo import db
from werkzeug.security import check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    todos = db.relationship('Todo', backref='user', lazy='dynamic')

    def check_password(self, password):
        return check_password_hash(self.password, password)
		
    def to_dict(self):
        return dict(
            id=self.id,
            username=self.username
        )
		
    def __repr__(self):
        return '<User {}>'.format(self.username)
		
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String)
    completed = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        return dict(
            id=self.id,
            user_id=self.user_id,
            description=self.description,
            completed=self.completed
        )	
		
    def __repr__(self):
        return '<Todo {}>'.format(self.description)