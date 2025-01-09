from aon.factory import create_app
from flask import request
from flask_cors import CORS
from vercel.wsgi import VercelWSGI

app = create_app(config_name="DEVELOPMENT")
CORS(app, supports_credentials=True)

app_wsgi = VercelWSGI(app)

def main(request):
    return app_wsgi(request)