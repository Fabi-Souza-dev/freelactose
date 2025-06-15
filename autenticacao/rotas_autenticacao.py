from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlparse
from extensions import db
from autenticacao import bp
from autenticacao.formularios import FormularioLogin, FormularioRegistro
from models import Usuario


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Se já estiver logado, manda direto para a index
        return redirect(url_for('main.index'))

    form = FormularioLogin()

    if form.validate_on_submit():
        # Se clicou em "Esqueci minha senha", redireciona para a rota de recuperação
        if form.recuperar_senha.data:
            return redirect(url_for('autenticacao.recuperar_senha'))

        # Busca usuário pelo email
        usuario = Usuario.query.filter_by(email=form.email.data).first()

        # Verifica se usuário existe e senha está correta
        if usuario is None or not usuario.verificar_senha(form.senha.data):
            flash('Email ou senha inválidos', 'danger')
            return redirect(url_for('autenticacao.login'))

        # Loga o usuário e mantém sessão se marcou "lembrar"
        login_user(usuario, remember=form.lembrar.data)

        # Pega a próxima página, se existir (parâmetro next)
        proxima_pagina = request.args.get('next')

        # Valida para evitar redirecionamento externo (phishing)
        if not proxima_pagina or urlparse(proxima_pagina).netloc != '':
            proxima_pagina = url_for('main.index')

        flash('Login realizado com sucesso!', 'success')
        return redirect(proxima_pagina)

    # Se GET ou falhou na validação, exibe o formulário de login
    return render_template('login.html', titulo='Login', form=form)


@bp.route('/registro', methods=['GET', 'POST'])
def registro():
    form = FormularioRegistro()
    if form.validate_on_submit():
        novo_usuario = Usuario(
            nome_usuario=form.nome_usuario.data,
            email=form.email.data
        )
        novo_usuario.set_senha(form.senha.data)

        db.session.add(novo_usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')

        return redirect(url_for('main.index'))

    return render_template('registro.html', titulo='Cadastro', form=form)



@bp.route('/logout')
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('main.index'))
