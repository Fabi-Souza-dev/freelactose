from flask import Blueprint

bp = Blueprint('autenticacao', __name__)

from autenticacao import rotas_autenticacao