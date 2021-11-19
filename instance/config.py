import os

SECRET_KEY = "6921e04b465ea228c15bc09328d48d4314e117909c04ddbf6505043c878d3391"
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_ENGINE_OPTIONS = {
    'connect_args': {
        'connect_timeout': 5
    }
}