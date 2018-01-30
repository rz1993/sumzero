import os

_base_path = os.path.dirname(os.path.realpath(__file__))

DEBUG = True
SECRET_KEY = "SECRET"

# Database configuration
# sqlite path needs to be absolute
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

# MongoDB config
MONGO_DB_URI = "mongodb://rzhou93:Number1son!@sumcluster-shard-00-00-eam9d.mongodb.net:27017,sumcluster-shard-00-01-eam9d.mongodb.net:27017,sumcluster-shard-00-02-eam9d.mongodb.net:27017/test?ssl=true&replicaSet=sumcluster-shard-0&authSource=admin"

# Flask-Mail configuration
# Note that currently gmail will not allow third party app access without OAuth2
# unless we turn down security settings for all apps
MAIL_ASCII_ATTACHMENTS = False
MAIL_DEFAULT_SENDER = "roland.zhou93@gmail.com"
MAIL_MAX_EMAILS = 100
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USERNAME = "roland.zhou93@gmail.com"
MAIL_PASSWORD = "Number1son"
MAIL_SUPPRESS_SEND = False
MAIL_USE_SSL = True

# Flask-User settings
USER_APP_NAME = "SumZero"           # Used in email templates
