"""
Módulo: rotas.py
Mapeia e organiza todas as rotas do sistema Flask, ligando os controladores modulares.
"""

from datetime import datetime, timezone
from flask import current_app, flash, redirect, render_template, request, session, url_for
import autenticacao
import clientes
import veiculos
import agendamento
from banco import obter_conexao

def registrar_rotas(app):
    
    # Interceptor para verificação de tempo de expiração de sessão
    @app.before_request
    def checar_expiracao_sessao():
        rotas_livres = ['login', 'static', 'index']
        if request.endpoint in rotas_livres or request.endpoint is None:
            return
            
        if not autenticacao.verificar_sessao_ativa():
            session.clear()
            return redirect(url_for('login'))
            
        # Atualiza carimbo de tempo para controle de inatividade
        session['ultimo_acesso'] = datetime.now(timezone.utc).isoformat()

    # Injeção de contexto global para os templates (exibe usuário logado em todas as páginas)
    @app.context_processor
    def injetar_usuario():
        return {
            'usuario_logado': session.get('usuario_nome'),
            'usuario_cargo': session.get('usuario_cargo'),
            'agora': datetime.now()
        }

    # ==========================
    # ROTAS DE AUTENTICAÇÃO
    # ==========================
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        return autenticacao.realizar_login()

    @app.route('/logout')
    def logout():
        return autenticacao.realizar_logout()

    # ==========================
    # FUNCIONALIDADE PRINCIPAL (DASHBOARD)
    # Regra de Negócio: Exibe o nome do usuário logado, forma de acessar os recursos e sair.
    # ==========================
    @app.route('/dashboard')
    def dashboard():
        conexao = obter_conexao()
        total_clientes = 0
        total_veiculos = 0
        total_agendamentos = 0
        proximos_servicos = []
        
        if conexao:
            try:
                cursor = conexao.cursor(dictionary=True)
                cursor.execute("SELECT COUNT(*) AS total FROM clientes")
                total_clientes = cursor.fetchone()['total']
                
                cursor.execute("SELECT COUNT(*) AS total FROM veiculos")
                total_veiculos = cursor.fetchone()['total']
                
                cursor.execute("SELECT COUNT(*) AS total FROM agendamentos")
                total_agendamentos = cursor.fetchone()['total']
                
                cursor.execute("""
                    SELECT a.id, a.data_agendamento, s.descricao AS descricao_servico,
                           a.status, c.nome AS cliente_nome, v.placa, v.modelo
                    FROM agendamentos a
                    JOIN veiculos v ON a.veiculo_id = v.id
                    JOIN clientes c ON v.cliente_id = c.id
                    JOIN servicos s ON a.servico_id = s.id
                    ORDER BY a.data_agendamento ASC
                    LIMIT 5
                """)
                proximos_servicos = cursor.fetchall()
            except Exception:
                current_app.logger.exception('Falha ao carregar os dados do painel')
                flash('Erro ao carregar o painel. Consulte o log do servidor.', 'erro')
            finally:
                conexao.close()
        else:
            flash('Não foi possível conectar ao banco de dados.', 'erro')
                
        return render_template('dashboard.html',
                               total_clientes=total_clientes,
                               total_veiculos=total_veiculos,
                               total_agendamentos=total_agendamentos,
                               proximos_servicos=proximos_servicos)

    # ==========================
    # ROTAS DE CLIENTES
    # ==========================
    @app.route('/clientes', methods=['GET'])
    def clientes_view():
        return clientes.listar_clientes()

    @app.route('/clientes/novo', methods=['POST'])
    def clientes_novo():
        return clientes.cadastrar_cliente()

    @app.route('/clientes/editar/<int:id>', methods=['POST'])
    def clientes_editar(id):
        return clientes.editar_cliente(id)

    @app.route('/clientes/excluir/<int:id>', methods=['POST', 'GET'])
    def clientes_excluir(id):
        return clientes.excluir_cliente(id)

    # ==========================
    # ROTAS DE VEÍCULOS
    # ==========================
    @app.route('/veiculos', methods=['GET'])
    def veiculos_view():
        return veiculos.listar_veiculos()

    @app.route('/veiculos/novo', methods=['POST'])
    def veiculos_novo():
        return veiculos.cadastrar_veiculo()

    @app.route('/veiculos/editar/<int:id>', methods=['POST'])
    def veiculos_editar(id):
        return veiculos.editar_veiculo(id)

    @app.route('/veiculos/excluir/<int:id>', methods=['POST', 'GET'])
    def veiculos_excluir(id):
        return veiculos.excluir_veiculo(id)

    # ==========================
    # ROTAS DE AGENDAMENTOS
    # ==========================
    @app.route('/agendamentos', methods=['GET'])
    def agendamentos_view():
        return agendamento.listar_agendamentos()

    @app.route('/agendamentos/novo', methods=['POST'])
    def agendamentos_novo():
        return agendamento.cadastrar_agendamento()

    @app.route('/agendamentos/atualizar-data/<int:id>', methods=['POST'])
    def agendamentos_atualizar_data(id):
        return agendamento.atualizar_data_agendamento(id)

    @app.route('/agendamentos/excluir/<int:id>', methods=['POST', 'GET'])
    def agendamentos_excluir(id):
        return agendamento.excluir_agendamento(id)
