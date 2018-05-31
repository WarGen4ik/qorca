import os

DEBUG = False

BASE_URL = 'http://www.qorca.ml'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = '587'
EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']
EMAIL_USE_TLS = True


AWS_USER = 'qorca-user'
AWS_ACCESS_KEY = 'AKIAIL3OGJHGMHQPRXKA'
AWS_SECRET_KEY = '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'

AWS_ACCESS_KEY_ID = 'AKIAIL3OGJHGMHQPRXKA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'qorca'
AWS_S3_CUSTOM_DOMAIN = '{}.s3.amazonaws.com'.format(AWS_STORAGE_BUCKET_NAME)
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'

STATIC_URL = 'https://{}/{}/'.format(AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'qorca.storage_backends.MediaStorage'
