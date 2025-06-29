from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from extensions import db
from main import bp
from models import Receita, Produto, Avaliacao, Favorito
from .recomendacoes import recomendar_receitas_para, recomendar_produtos_para
from main.formularios import (
    FormularioReceita,
    FormularioAvaliacaoProduto,
    FormularioAvaliacaoReceita,
    FormularioBusca,
    FormularioProduto,
    FormularioExclusao
)
import os
from werkzeug.utils import secure_filename


@bp.route('/')
def index():
    receitas = Receita.query.order_by(Receita.data_criacao.desc()).limit(4).all()
    produtos = Produto.query.limit(4).all()
    return render_template('index.html', titulo='Início', receitas=receitas, produtos=produtos)


@bp.route('/receitas')
def listar_receitas():
    form_busca = FormularioBusca()
    pagina = request.args.get('page', 1, type=int)
    termo = request.args.get('termo', '')

    if termo:
        receitas = Receita.query.filter(
            Receita.titulo.contains(termo) | Receita.tags.contains(termo)
        ).order_by(Receita.data_criacao.desc()).paginate(page=pagina, per_page=10, error_out=False)
    else:
        receitas = Receita.query.order_by(Receita.data_criacao.desc()).paginate(page=pagina, per_page=10,
                                                                                error_out=False)

    return render_template('receitas.html', titulo='Receitas', receitas=receitas, form_busca=form_busca, termo=termo)


@bp.route('/produto/<int:id>', methods=['GET', 'POST'])
def detalhe_produto(id):
    produto = Produto.query.get_or_404(id)
    form = FormularioAvaliacaoProduto()
    form_exclusao = FormularioExclusao()
    termo = request.args.get('termo', '')

    # Buscar todas as avaliações deste produto
    avaliacoes = Avaliacao.query.filter_by(produto_id=produto.id).order_by(Avaliacao.data_avaliacao.desc()).all()

    if form.validate_on_submit():
        avaliacao_existente = Avaliacao.query.filter_by(
            usuario_id=current_user.id,
            produto_id=produto.id
        ).first()

        if not avaliacao_existente:
            avaliacao = Avaliacao(
                nota=form.nota.data,
                comentario=form.comentario.data,
                produto_id=produto.id,
                usuario_id=current_user.id
            )
            db.session.add(avaliacao)
            db.session.commit()
            flash('Sua avaliação foi publicada!', 'success')
        else:
            flash('Você já avaliou este produto.', 'warning')

        return redirect(url_for('main.detalhe_produto', id=produto.id, termo=termo))

    return render_template(
        'detalhe_produto.html',
        titulo=produto.nome,
        produto=produto,
        form=form,
        termo=termo,
        form_exclusao=form_exclusao,
        avaliacoes=avaliacoes
    )


@bp.route('/recomendacoes-produtos')
@login_required
def recomendacoes_produtos():
    produtos_recomendados = recomendar_produtos_para(current_user.id)
    return render_template('recomendacoes_produtos.html', produtos=produtos_recomendados)


@bp.route('/adicionar_produto', methods=['GET', 'POST'])
@login_required
def adicionar_produto():
    form = FormularioProduto()
    if form.validate_on_submit():
        imagem_arquivo = form.imagem.data
        nome_arquivo = None

        if imagem_arquivo:
            nome_arquivo = secure_filename(imagem_arquivo.filename)
            caminho = os.path.join(current_app.root_path, 'static/uploads', nome_arquivo)  # <-- aqui
            imagem_arquivo.save(caminho)

        novo_produto = Produto(
            nome=form.nome.data,
            descricao=form.descricao.data,
            marca=form.marca.data,
            categoria=form.categoria.data,
            imagem=nome_arquivo,
            usuario_id=current_user.id
        )

        db.session.add(novo_produto)
        db.session.commit()
        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('main.index'))

    return render_template('adiciona_produto.html', form=form, titulo='Adicionar Produto')


@bp.route('/receita/<int:id>', methods=['GET', 'POST'])
def detalhe_receita(id):
    receita = Receita.query.get_or_404(id)
    form = FormularioAvaliacaoReceita()
    form_exclusao = FormularioExclusao()  # instância para o token CSRF na exclusão

    if form.validate_on_submit():
        avaliacao_existente = Avaliacao.query.filter_by(usuario_id=current_user.id, receita_id=receita.id).first()
        if not avaliacao_existente:
            avaliacao = Avaliacao(
                nota=form.nota.data,
                comentario=form.comentario.data,
                receita_id=receita.id,
                usuario_id=current_user.id
            )
            db.session.add(avaliacao)
            db.session.commit()
            flash('Sua avaliação foi publicada!')
        else:
            flash('Você já avaliou esta receita.')
        return redirect(url_for('main.detalhe_receita', id=receita.id))

    avaliacoes = Avaliacao.query.filter_by(receita_id=receita.id).all()
    return render_template(
        'detalhe_receitas.html',
        titulo=receita.titulo,
        receita=receita,
        form=form,
        form_exclusao=form_exclusao,  # <-- importante passar para o template!
        avaliacoes=avaliacoes
    )



@bp.route('/recomendacoes')
@login_required
def recomendacoes():
    receitas_recomendadas = recomendar_receitas_para(current_user.id)
    return render_template('recomendacoes.html', receitas=receitas_recomendadas)


@bp.route('/produtos')
def listar_produtos():
    form_busca = FormularioBusca()
    form_exclusao = FormularioExclusao()
    pagina = request.args.get('page', 1, type=int)
    termo = request.args.get('termo', '')

    if termo:
        produtos = Produto.query.filter(
            Produto.nome.contains(termo) | Produto.marca.contains(termo) | Produto.categoria.contains(termo)
        ).paginate(page=pagina, per_page=10, error_out=False)
    else:
        produtos = Produto.query.paginate(page=pagina, per_page=10, error_out=False)

    return render_template('produtos.html', titulo='Produtos', produtos=produtos, form_busca=form_busca, termo=termo,
                           form_exclusao=form_exclusao)


@bp.route("/favoritos")
@login_required
def favoritos():
    favoritos_usuario = Favorito.query.filter_by(usuario_id=current_user.id).all()
    receitas_favoritas = [f for f in favoritos_usuario if f.receita]
    produtos_favoritos = [f for f in favoritos_usuario if f.produto]
    return render_template("favoritos.html", receitas=receitas_favoritas, produtos=produtos_favoritos)


@bp.route('/adicionar_receita', methods=['GET', 'POST'])
@login_required
def adicionar_receita():
    form = FormularioReceita()
    if form.validate_on_submit():
        arquivo_imagem = form.imagem.data
        nome_arquivo = None
        if arquivo_imagem:
            nome_seguro = secure_filename(arquivo_imagem.filename)
            caminho = os.path.join(current_app.root_path, 'static/uploads', nome_seguro)
            arquivo_imagem.save(caminho)
            nome_arquivo = nome_seguro

        receita = Receita(
            titulo=form.titulo.data,
            descricao=form.descricao.data,
            ingredientes=form.ingredientes.data,
            instrucoes=form.instrucoes.data,
            tags=form.tags.data,
            imagem=nome_arquivo,
            usuario_id=current_user.id
        )
        db.session.add(receita)
        db.session.commit()
        flash('Receita adicionada com sucesso!', 'success')
        return redirect(url_for('main.index'))

    return render_template('adicionar_receita.html', titulo='Adicionar Receita', form=form)


@bp.route('/avaliacao-produto/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_avaliacao_produto(id):
    avaliacao = Avaliacao.query.get_or_404(id)

    if avaliacao.usuario_id != current_user.id:
        flash("Você não tem permissão para editar esta avaliação.", "danger")
        return redirect(url_for('main.index'))

    form = FormularioAvaliacaoProduto(obj=avaliacao)

    if form.validate_on_submit():
        avaliacao.nota = form.nota.data
        avaliacao.comentario = form.comentario.data
        db.session.commit()
        flash("Avaliação atualizada com sucesso!", "success")
        return redirect(url_for('main.detalhe_produto', id=avaliacao.produto_id))

    return render_template('editar_avaliacao_produto.html', form=form, avaliacao=avaliacao)


@bp.route('/adicionar_favorito/<tipo>/<int:id>')
@login_required
def adicionar_favorito(tipo, id):
    favorito_existente = None
    if tipo == 'receita':
        favorito_existente = Favorito.query.filter_by(usuario_id=current_user.id, receita_id=id).first()
        if not favorito_existente:
            novo = Favorito(usuario_id=current_user.id, receita_id=id)
            db.session.add(novo)
            db.session.commit()
            flash('Receita adicionada aos favoritos!')
        else:
            flash('Essa receita já está nos seus favoritos.')
    elif tipo == 'produto':
        favorito_existente = Favorito.query.filter_by(usuario_id=current_user.id, produto_id=id).first()
        if not favorito_existente:
            novo = Favorito(usuario_id=current_user.id, produto_id=id)
            db.session.add(novo)
            db.session.commit()
            flash('Produto adicionado aos favoritos!')
        else:
            flash('Esse produto já está nos seus favoritos.')
    else:
        flash('Tipo inválido para favorito.')

    return redirect(request.referrer or url_for('main.index'))


@bp.route('/receita/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_receita(id):
    receita = Receita.query.get_or_404(id)

    if receita.usuario_id != current_user.id:
        flash('Você não tem permissão para editar esta receita.', 'danger')
        return redirect(url_for('main.listar_receitas'))

    form = FormularioReceita(obj=receita)

    if form.validate_on_submit():
        receita.titulo = form.titulo.data
        receita.descricao = form.descricao.data
        receita.ingredientes = form.ingredientes.data
        receita.instrucoes = form.instrucoes.data
        receita.tags = form.tags.data

        arquivo_imagem = form.imagem.data
        if arquivo_imagem and hasattr(arquivo_imagem, 'filename') and arquivo_imagem.filename != '':
            nome_seguro = secure_filename(arquivo_imagem.filename)
            caminho = os.path.join(current_app.root_path, 'static/uploads', nome_seguro)
            arquivo_imagem.save(caminho)
            receita.imagem = nome_seguro

        db.session.commit()
        flash('Receita atualizada com sucesso!', 'success')
        return redirect(url_for('main.detalhe_receita', id=receita.id))

    return render_template('editar_receita.html', titulo='Editar Receita', form=form, receita=receita)


@bp.route('/receita/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_receita(id):
    receita = Receita.query.get_or_404(id)
    if receita.usuario_id != current_user.id:
        flash('Você não tem permissão para excluir esta receita.', 'danger')
        return redirect(url_for('main.listar_receitas'))

    db.session.delete(receita)
    db.session.commit()
    flash('Receita excluída com sucesso.', 'success')
    return redirect(url_for('main.listar_receitas'))


@bp.route('/produto/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_produto(id):
    produto = Produto.query.get_or_404(id)
    if produto.usuario_id != current_user.id:
        flash('Você não tem permissão para editar este produto.', 'danger')
        return redirect(url_for('main.listar_produtos'))

    form = FormularioProduto(obj=produto)
    if form.validate_on_submit():
        # Atualiza dados do produto
        form.populate_obj(produto)

        # Atualiza imagem se for enviada
        arquivo_imagem = form.imagem.data
        if arquivo_imagem and hasattr(arquivo_imagem, 'filename') and arquivo_imagem.filename != '':
            nome_arquivo = secure_filename(arquivo_imagem.filename)
            caminho = os.path.join(current_app.root_path, 'static/uploads', nome_arquivo)  # <-- aqui também
            arquivo_imagem.save(caminho)
            produto.imagem = nome_arquivo

        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('main.detalhe_produto', id=produto.id))

    return render_template('editar_produto.html', form=form, produto=produto)


@bp.route('/produto/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_produto(id):
    produto = Produto.query.get_or_404(id)
    if produto.usuario_id != current_user.id:
        flash('Você não tem permissão para excluir este produto.', 'danger')
        return redirect(url_for('main.listar_produtos'))

    db.session.delete(produto)
    db.session.commit()
    flash('Produto excluído com sucesso.', 'success')
    return redirect(url_for('main.listar_produtos'))


@bp.route('/meus-comentarios')
@login_required
def meus_comentarios():
    termo_busca = request.args.get('busca', '')

    avaliacoes_receitas = (
        Avaliacao.query
        .filter(Avaliacao.usuario_id == current_user.id, Avaliacao.receita_id != None)
        .join(Receita, Avaliacao.receita_id == Receita.id)
        .filter(Receita.titulo.ilike(f'%{termo_busca}%'))
        .add_columns(Receita.titulo.label('nome_item'), Receita.id.label('item_id'))
        .all()
    )

    avaliacoes_produtos = (
        Avaliacao.query
        .filter(Avaliacao.usuario_id == current_user.id, Avaliacao.produto_id != None)
        .join(Produto, Avaliacao.produto_id == Produto.id)
        .filter(Produto.nome.ilike(f'%{termo_busca}%'))
        .add_columns(Produto.nome.label('nome_item'), Produto.id.label('item_id'))
        .all()
    )

    return render_template(
        'meus_comentarios.html',
        avaliacoes_receitas=avaliacoes_receitas,
        avaliacoes_produtos=avaliacoes_produtos,
        termo_busca=termo_busca
    )




@bp.route('/avaliacao/<int:avaliacao_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_avaliacao(avaliacao_id):
    avaliacao = Avaliacao.query.get_or_404(avaliacao_id)
    if avaliacao.usuario_id != current_user.id:
        flash("Você não tem permissão para editar esta avaliação.", "danger")
        return redirect(url_for('main.meus_comentarios'))

    form = FormularioAvaliacaoProduto(obj=avaliacao)  # Preenche o form com dados existentes

    if form.validate_on_submit():
        avaliacao.nota = form.nota.data
        avaliacao.comentario = form.comentario.data
        db.session.commit()
        flash("Avaliação atualizada com sucesso!", "success")
        return redirect(url_for('main.meus_comentarios'))

    return render_template('editar_avaliacao.html', avaliacao=avaliacao, form=form)



@bp.route('/avaliacao/<int:avaliacao_id>/excluir')
@login_required
def excluir_avaliacao(avaliacao_id):
    avaliacao = Avaliacao.query.get_or_404(avaliacao_id)
    if avaliacao.usuario_id != current_user.id:
        flash("Você não tem permissão para excluir esta avaliação.", "danger")
        return redirect(url_for('main.meus_comentarios'))

    db.session.delete(avaliacao)
    db.session.commit()
    flash("Avaliação excluída com sucesso!", "success")
    return redirect(url_for('main.meus_comentarios'))
