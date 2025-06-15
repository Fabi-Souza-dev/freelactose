from flask import Flask
from extensions import db, migrate, login
from flask_wtf import CSRFProtect
import pymysql
import os

pymysql.install_as_MySQLdb()

csrf = CSRFProtect()  # <- inicializa o CSRF

def criar_aplicacao():
    app = Flask(__name__)
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-padrao')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///lactoselivre.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    login.login_view = 'autenticacao.login'

    csrf.init_app(app)  # <- inicializa o CSRF no app

    from autenticacao import bp as bp_autenticacao
    app.register_blueprint(bp_autenticacao, url_prefix='/auth')
    from main import bp as bp_main
    app.register_blueprint(bp_main)

    return app

# Criação da app
app = criar_aplicacao()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
