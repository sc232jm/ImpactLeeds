import os

WTF_CSRF_ENABLED = True
SECRET_KEY = "abc123abc"

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True

LOCKDOWN_ENABLED = False