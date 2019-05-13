import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
  SECURITY_PASSWORD_SALT = os.environ.get(
      'SECURITY_PASSWORD_SALT') or 'you-will-never-guess'
  MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
  MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
  MAIL_SERVER = os.environ.get('MAIL_SERVER')
  MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
  MAIL_PORT = os.environ.get('MAIL_PORT') or 587
  MAIL_USE_TLS = True
  APPLICATION_NAME = 'Foodlist'
