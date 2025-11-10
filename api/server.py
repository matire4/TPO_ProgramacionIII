import os
import sys

from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from server import app as flask_app  # noqa: E402

fastapi_app = FastAPI()
fastapi_app.mount("/", WSGIMiddleware(flask_app))

app = fastapi_app

