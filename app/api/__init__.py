from flask import Blueprint
bp = Blueprint('api', __name__)
from app.api import routes
from app.api.routes_new import init_new_routes
init_new_routes(bp)
