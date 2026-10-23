"""Cadastro, edição e consulta de agendamentos da oficina."""

from datetime import datetime

from flask import current_app, flash, redirect, render_template, request, url_for

from banco import obter_conexao


def listar_agendamentos():
    conexao = obter_conexao()
    if not conexao:
        flash('Não foi possível conectar ao banco de dados.', 'erro')
        return render_template(
            'agendamentos.html',
            agendamentos=[],
            veiculos=[],
            servicos=[],
        )

    try:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("""
            SELECT a.id AS agendamento_id, a.data_agendamento, a.status,
                   a.observacao AS observacoes, s.descricao AS descricao_servico,
                   s.valor AS valor_estimado,
                   c.id AS cliente_id, c.nome AS cliente_nome,
                   c.telefone AS cliente_telefone, c.email AS cliente_email,
                   c.endereco AS cliente_endereco,
                   v.id AS veiculo_id, v.placa AS veiculo_placa,
                   v.marca AS veiculo_marca, v.modelo AS veiculo_modelo,
                   v.ano AS veiculo_ano, v.cor AS veiculo_cor
            FROM agendamentos a
            JOIN veiculos v ON a.veiculo_id = v.id
            JOIN clientes c ON v.cliente_id = c.id
            JOIN servicos s ON a.servico_id = s.id
            ORDER BY a.data_agendamento ASC
        """)
        agendamentos = cursor.fetchall()
        cursor.execute("""
            SELECT v.id, v.placa, v.marca, v.modelo, c.nome AS cliente_nome
            FROM veiculos v
            JOIN clientes c ON v.cliente_id = c.id
            ORDER BY c.nome ASC
        """)
        veiculos = cursor.fetchall()
        cursor.execute("SELECT id, descricao, valor FROM servicos ORDER BY descricao ASC")
        servicos = cursor.fetchall()
    except Exception:
        current_app.logger.exception('Falha ao carregar os agendamentos')
        flash('Erro ao carregar os agendamentos. Consulte o log do servidor.', 'erro')
        agendamentos = []
        veiculos = []
        servicos = []
    finally:
        conexao.close()

    return render_template(
        'agendamentos.html',
        agendamentos=agendamentos,
        veiculos=veiculos,
        servicos=servicos,
    )


def cadastrar_agendamento():
    veiculo_id = request.form.get('veiculo_id', '').strip()
    servico_id = request.form.get('servico_id', '').strip()
    data_agendamento = request.form.get('data_agendamento', '').strip()
    observacao = request.form.get('observacoes', '').strip()

    if not veiculo_id.isdigit() or not servico_id.isdigit() or not data_agendamento:
        flash('Selecione veículo, serviço e data para o agendamento.', 'erro')
        return redirect(url_for('agendamentos_view'))
    try:
        data_normalizada = datetime.fromisoformat(
            data_agendamento.replace('T', ' ')
        )
    except ValueError:
        flash('Informe uma data e horário válidos para o agendamento.', 'erro')
        return redirect(url_for('agendamentos_view'))

    conexao = obter_conexao()
    if not conexao:
        flash('Não foi possível conectar ao banco de dados.', 'erro')
        return redirect(url_for('agendamentos_view'))
    try:
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO agendamentos (veiculo_id, servico_id, data_agendamento, observacao) "
            "VALUES (%s, %s, %s, %s)",
            (int(veiculo_id), int(servico_id), data_normalizada, observacao or None),
        )
        conexao.commit()
        flash('Agendamento cadastrado com sucesso.', 'sucesso')
    except Exception:
        conexao.rollback()
        current_app.logger.exception('Falha ao cadastrar agendamento')
        flash('Erro ao cadastrar agendamento. Verifique os dados e consulte o log do servidor.', 'erro')
    finally:
        conexao.close()
    return redirect(url_for('agendamentos_view'))


def atualizar_data_agendamento(agendamento_id: int):
    nova_data = request.form.get('nova_data_agendamento', '').strip()
    if not nova_data:
        flash('Informe a nova data e horário.', 'erro')
        return redirect(url_for('agendamentos_view'))
    try:
        data_normalizada = datetime.fromisoformat(nova_data.replace('T', ' '))
    except ValueError:
        flash('Informe uma data e horário válidos.', 'erro')
        return redirect(url_for('agendamentos_view'))

    conexao = obter_conexao()
    if not conexao:
        flash('Não foi possível conectar ao banco de dados.', 'erro')
        return redirect(url_for('agendamentos_view'))
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT id FROM agendamentos WHERE id = %s", (agendamento_id,))
        if not cursor.fetchone():
            flash('Agendamento não encontrado.', 'erro')
        else:
            cursor.execute(
                "UPDATE agendamentos SET data_agendamento = %s WHERE id = %s",
                (data_normalizada, agendamento_id),
            )
            conexao.commit()
            flash('Data do agendamento atualizada com sucesso.', 'sucesso')
    except Exception:
        conexao.rollback()
        current_app.logger.exception('Falha ao atualizar data do agendamento')
        flash('Erro ao atualizar data. Consulte o log do servidor.', 'erro')
    finally:
        conexao.close()
    return redirect(url_for('agendamentos_view'))


def excluir_agendamento(agendamento_id: int):
    conexao = obter_conexao()
    if not conexao:
        flash('Não foi possível conectar ao banco de dados.', 'erro')
        return redirect(url_for('agendamentos_view'))
    try:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM agendamentos WHERE id = %s", (agendamento_id,))
        if cursor.rowcount == 0:
            flash('Agendamento não encontrado.', 'erro')
        else:
            conexao.commit()
            flash('Agendamento excluído com sucesso.', 'sucesso')
    except Exception:
        conexao.rollback()
        current_app.logger.exception('Falha ao excluir agendamento')
        flash('Erro ao excluir agendamento. Consulte o log do servidor.', 'erro')
    finally:
        conexao.close()
    return redirect(url_for('agendamentos_view'))
