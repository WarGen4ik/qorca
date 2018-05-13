import os

DEBUG = False

BASE_URL = 'http://www.qorca.ml'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = '587'
EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']
EMAIL_USE_TLS = True
