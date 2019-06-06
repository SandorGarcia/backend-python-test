from flask import Flask, g
import sqlite3
import tempfile
from flask_sqlalchemy import SQLAlchemy
import os


# configuration
DATABASE = tempfile.gettempdir() + '/alayatodo.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE
SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)


import alayatodo.views