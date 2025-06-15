from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from models import Usuario

class FormularioLogin(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    lembrar = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')
    recuperar_senha = SubmitField('Esqueci minha senha')

class FormularioRegistro(FlaskForm):
    nome_usuario = StringField('Nome de usuário', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    confirmar_senha = PasswordField('Repita a senha', validators=[DataRequired(), EqualTo('senha')])
    cadastrar = SubmitField('Cadastrar')

    def validate_nome_usuario(self, nome_usuario):
        usuario = Usuario.query.filter_by(nome_usuario=nome_usuario.data).first()
        if usuario:
            raise ValidationError('Este nome de usuário já está em uso.')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Este email já está em uso.')
