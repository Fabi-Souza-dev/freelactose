# main/recomendacoes.py

from flask_login import current_user
from models import Receita, Avaliacao, db
from sqlalchemy.sql import func

def recomendar_receitas_para(usuario_id, limite=5):
    # Primeiro, busca receitas avaliadas com notas altas por este usuário
    favoritas = (
        db.session.query(Receita)
        .join(Avaliacao)
        .filter(Avaliacao.usuario_id == usuario_id, Avaliacao.receita_id == Receita.id)
        .order_by(Avaliacao.nota.desc())
        .limit(limite)
        .all()
    )

    # Se não houver favoritas, mostrar mais populares da comunidade
    if not favoritas:
        populares = (
            db.session.query(Receita)
            .join(Avaliacao)
            .filter(Avaliacao.receita_id == Receita.id)
            .group_by(Receita.id)
            .order_by(func.avg(Avaliacao.nota).desc())
            .limit(limite)
            .all()
        )
        return populares

    return favoritas
