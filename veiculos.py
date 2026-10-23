"""Cadastro, edição e consulta de veículos da oficina."""

from flask import current_app, flash, redirect, render_template, request, url_for

from banco import obter_conexao


def listar_veiculos():
    conexao = obter_conexao()
    if not conexao:
        flash('Não foi possível conectar ao banco de dados.', 'erro')
        return render_template('veiculos.html', veiculos=[], clientes=[])

    try:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("""
            SELECT v.id, v.cliente_id, v.placa, v.marca, v.modelo, v.ano, v.cor,
                   c.nome AS cliente_nome, c.telefone AS cliente_telefone
            FROM veiculos v
            JOIN clientes c ON v.cliente_id = c.id
            ORDER BY v.modelo ASC
        """)
        veiculos = cursor.fetchall()
        cursor.execute("SELECT id, nome FROM clientes ORDER BY nome ASC")
        clientes = cursor.fetchall()
    except Exception:
        current_app.logger.exception('Falha ao carregar os veículos')
        flash('Erro ao carregar os veículos. Consulte o log do servidor.', 'erro')
        veiculos = []
        clientes = []
    finally:
        conexao.close()

    return render_template('veiculos.html', veiculos=veiculos, clientes=clientes)


def _dados_veiculo():
    cliente_id = request.form.get('cliente_id', '').strip()
    placa = request.form.get('placa', '').strip().upper()
    marca = request.form.get('marca', '').strip()
    modelo = request.form.get('modelo', '').strip()
    ano = request.form.get('ano', '').strip()
    cor = request.form.get('cor', '').strip()

    if not cliente_id.isdigit() or not placa or not marca or not modelo or not ano:
        flash('Preencha cliente, placa, marca, modelo e ano.', 'erro')
        return None
    try:
        ano_numero = int(ano)
    except ValueError:
        flash('Informe um ano válido para o veículo.', 'erro')
        return None
    if not 1886 <= ano_numero <= 2100:
        flash('O ano do veículo deve estar entre 1886 e 2100.', 'erro')
        return None
    if len(placa) > 7:
        flash('A placa deve ter no máximo 7 caracteres.', 'erro')
        return None
    return int(cliente_id), placa, marca, modelo, ano_numero, cor or None


def cadastrar_veiculo():
    dados = _dados_veiculo()
    if dados is None:
        return redirect(url_for('veiculos_view'))

    conexao = obter_conexao()
    if not conexao:
        flash('Não foi possível conectar ao banco de dados.', 'erro')
        return redirect(url_for('veiculos_view'))
    try:
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO veiculos (cliente_id, placa, marca, modelo, ano, cor) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            dados,
        )
        conexao.commit()
        flash('Veículo cadastrado com sucesso.', 'sucesso')
    except Exception:
        conexao.rollback()
        current_app.logger.exception('Falha ao cadastrar veículo')
        flash('Erro ao cadastrar veículo. Verifique os dados e consulte o log do servidor.', 'erro')
    finally:
        conexao.close()
    return redirect(url_for('veiculos_view'))


def editar_veiculo(veiculo_id: int):
    dados = _dados_veiculo()
    if dados is None:
        return redirect(url_for('veiculos_view'))

    conexao = obter_conexao()
    if not conexao:
        flash('Não foi possível conectar ao banco de dados.', 'erro')
        return redirect(url_for('veiculos_view'))
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT id FROM veiculos WHERE id = %s", (veiculo_id,))
        if not cursor.fetchone():
            flash('Veículo não encontrado.', 'erro')
        else:
            cursor.execute(
                "UPDATE veiculos SET cliente_id = %s, placa = %s, marca = %s, "
                "modelo = %s, ano = %s, cor = %s WHERE id = %s",
                (*dados, veiculo_id),
            )
            conexao.commit()
            flash('Veículo atualizado com sucesso.', 'sucesso')
    except Exception:
        conexao.rollback()
        current_app.logger.exception('Falha ao atualizar veículo')
        flash('Erro ao atualizar veículo. Verifique os dados e consulte o log do servidor.', 'erro')
    finally:
        conexao.close()
    return redirect(url_for('veiculos_view'))


def excluir_veiculo(veiculo_id: int):
    conexao = obter_conexao()
    if not conexao:
        flash('Não foi possível conectar ao banco de dados.', 'erro')
        return redirect(url_for('veiculos_view'))
    try:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM veiculos WHERE id = %s", (veiculo_id,))
        if cursor.rowcount == 0:
            flash('Veículo não encontrado.', 'erro')
        else:
            conexao.commit()
            flash('Veículo excluído com sucesso.', 'sucesso')
    except Exception:
        conexao.rollback()
        current_app.logger.exception('Falha ao excluir veículo')
        flash('Não foi possível excluir o veículo. Verifique se ele possui agendamentos.', 'erro')
    finally:
        conexao.close()
    return redirect(url_for('veiculos_view'))
