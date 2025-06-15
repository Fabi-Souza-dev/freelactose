from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField, FloatField
from wtforms.validators import DataRequired, Length, NumberRange
from flask_wtf.file import FileField, FileAllowed

class FormularioReceita(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    ingredientes = TextAreaField('Ingredientes', validators=[DataRequired()])
    instrucoes = TextAreaField('Instruções', validators=[DataRequired()])
    tags = StringField('Tags')
    imagem = FileField('Imagem da Receita', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Apenas imagens são permitidas.')])
    submit = SubmitField('Adicionar Receita')


class FormularioAvaliacaoProduto(FlaskForm):
    nota = IntegerField('Avaliação (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5, message='A avaliação deve ser entre 1 e 5')])
    imagem = FileField('Imagem', validators=[FileAllowed(['jpg', 'png'], 'Apenas imagens!')])
    comentario = TextAreaField('Comentário', validators=[Length(max=500, message='O comentário não pode ter mais de 500 caracteres')])
    enviar = SubmitField('Enviar Avaliação')

class FormularioAvaliacaoReceita(FlaskForm):
    nota = IntegerField('Avaliação (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5, message='A avaliação deve ser entre 1 e 5')])
    comentario = TextAreaField('Comentário', validators=[Length(max=500, message='O comentário não pode ter mais de 500 caracteres')])
    enviar = SubmitField('Enviar Avaliação')

class FormularioBusca(FlaskForm):
    termo = StringField('Buscar', validators=[Length(max=100)])
    buscar = SubmitField('Pesquisar')


class FormularioProduto(FlaskForm):

    avaliacao = FloatField(
        "Avaliação",
        validators=[NumberRange(min=0, max=5, message="A avaliação deve estar entre 0 e 5.")]
    )

    nome = StringField(
        "Nome do Produto",
        validators=[
            DataRequired(message="O nome é obrigatório."),
            Length(max=100, message="O nome deve ter no máximo 100 caracteres.")
        ]
    )

    descricao = TextAreaField(
        "Descrição",
        validators=[
            DataRequired(message="A descrição é obrigatória."),
            Length(max=500, message="A descrição deve ter no máximo 500 caracteres.")
        ]
    )

    marca = StringField(  # alterado de TextAreaField para StringField
        "Marca",
        validators=[
            DataRequired(message="A marca é obrigatória."),
            Length(max=100, message="A marca deve ter no máximo 100 caracteres.")
        ]
    )

    categoria = StringField(
        "Categoria",
        validators=[
            DataRequired(message="A categoria é obrigatória."),
            Length(max=100, message="A categoria deve ter no máximo 100 caracteres.")
        ]
    )

    imagem = FileField(
        "Imagem do Produto",
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png'], 'Apenas arquivos de imagem são permitidos.')
        ]
    )

    submit = SubmitField("Cadastrar Produto")