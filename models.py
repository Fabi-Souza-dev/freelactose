from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db, login
from sqlalchemy.sql import func


# === MODELO USUARIO ===
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    senha_hash = db.Column(db.String(128))

    # Relacionamentos
    receitas = db.relationship('Receita', back_populates='autor', lazy='dynamic')
    avaliacoes = db.relationship('Avaliacao', back_populates='autor', lazy='dynamic')
    favoritos = db.relationship('Favorito', back_populates='usuario', lazy='dynamic')
    produtos = db.relationship('Produto', back_populates='usuario', lazy='dynamic')

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f'<Usuario {self.nome_usuario}>'

# === MODELO RECEITA ===
class Receita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    ingredientes = db.Column(db.Text, nullable=False)
    instrucoes = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(200))
    imagem = db.Column(db.String(200))
    data_criacao = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', name='fk_receita_usuario'), nullable=False)

    # Relacionamentos
    autor = db.relationship('Usuario', back_populates='receitas')
    avaliacoes = db.relationship('Avaliacao', back_populates='receita', lazy='dynamic')
    favoritos = db.relationship('Favorito', back_populates='receita', lazy='dynamic')

    def __repr__(self):
        return f'<Receita {self.titulo}>'

# === MODELO PRODUTO ===
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    marca = db.Column(db.String(100), nullable=True)
    categoria = db.Column(db.String(100), nullable=True)
    imagem = db.Column(db.String(100), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    # Relacionamentos
    usuario = db.relationship('Usuario', back_populates='produtos')
    avaliacoes = db.relationship('Avaliacao', back_populates='produto', lazy='dynamic')
    favoritos = db.relationship('Favorito', back_populates='produto', lazy='dynamic')

    def __repr__(self):
        return f'<Produto {self.nome}>'

# === MODELO AVALIACAO ===
class Avaliacao(db.Model):
    __tablename__ = 'avaliacao'
    id = db.Column(db.Integer, primary_key=True)
    nota = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text, nullable=True)
    data_avaliacao = db.Column(db.DateTime, default=datetime.utcnow)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    receita_id = db.Column(db.Integer, db.ForeignKey('receita.id'), nullable=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=True)

    autor = db.relationship('Usuario', back_populates='avaliacoes')
    receita = db.relationship('Receita', back_populates='avaliacoes')
    produto = db.relationship('Produto', back_populates='avaliacoes')



# === MODELO FAVORITO ===
class Favorito(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', name='fk_favorito_usuario'), nullable=False)
    receita_id = db.Column(db.Integer, db.ForeignKey('receita.id', name='fk_favorito_receita'), nullable=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id', name='fk_favorito_produto'), nullable=True)
    data_favorito = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # Relacionamentos
    usuario = db.relationship('Usuario', back_populates='favoritos')
    receita = db.relationship('Receita', back_populates='favoritos')
    produto = db.relationship('Produto', back_populates='favoritos')

    def __repr__(self):
        return f'<Favorito {self.id}>'

# === LOADER PARA LOGIN ===
@login.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))
