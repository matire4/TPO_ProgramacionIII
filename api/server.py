import os
import sys

from vercel_python_wsgi import make_lambda_handler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from server import app  # noqa: E402

handler = make_lambda_handler(app)

