"""Cadastro, edição e consulta de clientes da oficina."""

import re

import bcrypt
from flask import current_app, flash, redirect, render_template, request, url_for

from banco import obter_conexao


def validar_cpf_digitos(cpf_str: str) -> bool:
    """Valida se o CPF possui exatamente 11 dígitos numéricos."""
    return len(re.sub(r'\D', '', cpf_str)) == 11


def criptografar_cpf(cpf_str: str) -> str:
    """Gera o hash Bcrypt do CPF para armazenamento."""
    apenas_numeros = re.sub(r'\D', '', cpf_str)
    return bcrypt.hashpw(
        apenas_numeros.encode('utf-8'),
        bcrypt.gensalt(rounds=12),
    ).decode('utf-8')


def listar_clientes():
    termo_busca = request.args.get('busca', '').strip()
    conexao = obter_conexao()
    if not conexao:
        flash('Não foi possível conectar ao banco de dados.', 'erro')
        return render_template('clientes.html', clientes=[], termo_busca=termo_busca)

    try:
        cursor = conexao.cursor(dictionary=True)
        query = (
            "SELECT id, nome, telefone, email, endereco, criado_em AS data_cadastro "
            "FROM clientes"
        )
        if termo_busca:
            termo = f'%{termo_busca}%'
            query += " WHERE nome LIKE %s OR email LIKE %s OR telefone LIKE %s"
            cursor.execute(query + " ORDER BY nome ASC", (termo, termo, termo))
        else:
            cursor.execute(query + " ORDER BY nome ASC")
        clientes = cursor.fetchall()
    except Exception:
        current_app.logger.exception('Falha ao carregar os clientes')
        flash('Erro ao carregar os clientes. Consulte o log do servidor.', 'erro')
        clientes = []
    finally:
        conexao.close()

    return render_template(
        'clientes.html',
        clientes=clientes,
        termo_busca=termo_busca,
    )


def cadastrar_cliente():
    nome = request.form.get('nome', '').strip()
    cpf = request.form.get('cpf', '').strip()
    telefone = request.form.get('telefone', '').strip()
    email = request.form.get('email', '').strip()
    endereco = request.form.get('endereco', '').strip()

    if not nome or not cpf or not telefone or not email:
        flash('Preencha nome, CPF, telefone e e-mail.', 'erro')
        return redirect(url_for('clientes_view'))
    if not validar_cpf_digitos(cpf):
        flash('O CPF deve conter exatamente 11 dígitos numéricos.', 'erro')
        return redirect(url_for('clientes_view'))

    conexao = obter_conexao()
    if not conexao:
        flash('Não foi possível conectar ao banco de dados.', 'erro')
        return redirect(url_for('clientes_view'))
    try:
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO clientes (nome, cpf_hash, telefone, email, endereco) "
            "VALUES (%s, %s, %s, %s, %s)",
            (nome, criptografar_cpf(cpf), telefone, email, endereco or None),
        )
        conexao.commit()
        flash('Cliente cadastrado com sucesso.', 'sucesso')
    except Exception:
        conexao.rollback()
        current_app.logger.exception('Falha ao cadastrar cliente')
        flash('Erro ao cadastrar cliente. Consulte o log do servidor.', 'erro')
    finally:
        conexao.close()
    return redirect(url_for('clientes_view'))


def editar_cliente(cliente_id: int):
    nome = request.form.get('nome', '').strip()
    telefone = request.form.get('telefone', '').strip()
    email = request.form.get('email', '').strip()
    endereco = request.form.get('endereco', '').strip()
    if not nome or not telefone or not email:
        flash('Preencha nome, telefone e e-mail.', 'erro')
        return redirect(url_for('clientes_view'))

    conexao = obter_conexao()
    if not conexao:
        flash('Não foi possível conectar ao banco de dados.', 'erro')
        return redirect(url_for('clientes_view'))
    try:
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT id FROM clientes WHERE id = %s",
            (cliente_id,),
        )
        if not cursor.fetchone():
            flash('Cliente não encontrado.', 'erro')
        else:
            cursor.execute(
                "UPDATE clientes SET nome = %s, telefone = %s, email = %s, endereco = %s "
                "WHERE id = %s",
                (nome, telefone, email, endereco or None, cliente_id),
            )
            conexao.commit()
            flash('Cliente atualizado com sucesso.', 'sucesso')
    except Exception:
        conexao.rollback()
        current_app.logger.exception('Falha ao atualizar cliente')
        flash('Erro ao atualizar cliente. Consulte o log do servidor.', 'erro')
    finally:
        conexao.close()
    return redirect(url_for('clientes_view'))


def excluir_cliente(cliente_id: int):
    conexao = obter_conexao()
    if not conexao:
        flash('Não foi possível conectar ao banco de dados.', 'erro')
        return redirect(url_for('clientes_view'))
    try:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
        if cursor.rowcount == 0:
            flash('Cliente não encontrado.', 'erro')
        else:
            conexao.commit()
            flash('Cliente excluído com sucesso.', 'sucesso')
    except Exception:
        conexao.rollback()
        current_app.logger.exception('Falha ao excluir cliente')
        flash('Não foi possível excluir o cliente. Verifique se ele possui veículos.', 'erro')
    finally:
        conexao.close()
    return redirect(url_for('clientes_view'))
