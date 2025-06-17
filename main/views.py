from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import Produto, Avaliacao, db
from main.formularios import FormularioAvaliacaoProduto, FormularioExclusao

bp = Blueprint('main', __name__)


# === DETALHE DO PRODUTO ===
@bp.route('/produto/<int:id>', methods=['GET', 'POST'])
def detalhe_produto(id):
    produto = Produto.query.get_or_404(id)
    form = FormularioAvaliacaoProduto()
    form_exclusao = FormularioExclusao()
    termo = request.args.get('termo', '')

    if form.validate_on_submit() and current_user.is_authenticated:
        if form.avaliacao_id.data:
            # Atualiza avaliação existente
            avaliacao = Avaliacao.query.get(int(form.avaliacao_id.data))
            if avaliacao and avaliacao.usuario_id == current_user.id:
                avaliacao.nota = form.nota.data
                avaliacao.comentario = form.comentario.data
                db.session.commit()
                flash('Avaliação atualizada com sucesso!')
        else:
            # Cria nova avaliação
            avaliacao_existente = Avaliacao.query.filter_by(usuario_id=current_user.id, produto_id=produto.id).first()
            if not avaliacao_existente:
                nova_avaliacao = Avaliacao(
                    nota=form.nota.data,
                    comentario=form.comentario.data,
                    produto_id=produto.id,
                    usuario_id=current_user.id
                )
                db.session.add(nova_avaliacao)
                db.session.commit()
                flash('Sua avaliação foi publicada!')
            else:
                flash('Você já avaliou este produto.')

        return redirect(url_for('main.detalhe_produto', id=produto.id, termo=termo))

    avaliacoes = Avaliacao.query.filter_by(produto_id=produto.id).order_by(Avaliacao.data_avaliacao.desc()).all()

    return render_template(
        'detalhe_produto.html',
        titulo=produto.nome,
        produto=produto,
        form=form,
        form_exclusao=form_exclusao,
        termo=termo,
        avaliacoes=avaliacoes
    )


# === EDITAR AVALIAÇÃO ===
@bp.route('/editar_avaliacao/<int:id>', methods=['GET'])
@login_required
def editar_avaliacao(id):
    avaliacao = Avaliacao.query.get_or_404(id)
    if avaliacao.usuario_id != current_user.id:
        abort(403)

    form = FormularioAvaliacaoProduto()
    form.nota.data = avaliacao.nota
    form.comentario.data = avaliacao.comentario
    form.avaliacao_id.data = avaliacao.id

    flash('Você está editando sua avaliação.')
    return redirect(url_for('main.detalhe_produto', id=avaliacao.produto_id))


# === EXCLUIR AVALIAÇÃO ===
@bp.route('/excluir_avaliacao/<int:id>', methods=['POST'])
@login_required
def excluir_avaliacao(id):
    avaliacao = Avaliacao.query.get_or_404(id)
    if avaliacao.usuario_id != current_user.id:
        abort(403)

    produto_id = avaliacao.produto_id
    db.session.delete(avaliacao)
    db.session.commit()
    flash('Avaliação excluída com sucesso.')
    return redirect(url_for('main.detalhe_produto', id=produto_id))
