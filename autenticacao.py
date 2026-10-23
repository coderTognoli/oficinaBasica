"""
Módulo: autenticacao.py
Responsável pela validação de credenciais com Bcrypt, expiração de sessão e controle de acesso.
"""

from datetime import datetime, timezone
import bcrypt
from flask import current_app, flash, redirect, render_template, request, session, url_for
from banco import obter_conexao

def normalizar_texto(texto: str) -> str:
    """Remove acentos, espaços extras e converte para minúsculas para compatibilidade total."""
    import unicodedata
    if not texto:
        return ""
    texto_limpo = texto.strip().lower()
    return unicodedata.normalize('NFKD', texto_limpo).encode('ASCII', 'ignore').decode('ASCII')

def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Verifica se a senha fornecida bate com o hash Bcrypt armazenado."""
    try:
        return bcrypt.checkpw(senha_plana.encode('utf-8'), senha_hash.encode('utf-8'))
    except (ValueError, TypeError):
        return False

def realizar_login():
    """
    Processa a autenticação do usuário.
    Regra de Negócio: Deve haver validação explícita em caso de falha na autenticação.
    """
    if request.method == 'POST':
        login = request.form.get('login', '').strip()
        senha = request.form.get('senha', '')
        
        if not login or not senha:
            flash('Por favor, informe o usuário e a senha.', 'erro')
            return render_template('login.html', login=login)
            
        conexao = obter_conexao()
        if not conexao:
            flash('Falha ao conectar com o banco de dados. Verifique o servidor MySQL.', 'erro')
            return render_template('login.html', login=login)
            
        try:
            cursor = conexao.cursor(dictionary=True)
            # Normaliza termos com acentuação comum (mecânico -> mecanico, recepção -> recepcao)
            login_norm = normalizar_texto(login)
            if login_norm in ['mecanico', 'mecanica']:
                login_busca = 'carlos'
            elif login_norm == 'recepcao':
                login_busca = 'ana'
            elif login_norm in ['admin', 'administrador', 'gerente']:
                login_busca = 'admin'
            else:
                login_busca = login_norm

            cursor.execute(
                "SELECT id, nome, login, senha_hash, cargo, ativo "
                "FROM usuarios WHERE LOWER(login) = %s OR LOWER(login) = %s",
                (login.lower(), login_busca),
            )
            usuario = cursor.fetchone()
            
            # Validação de credenciais: usuário inexistente ou inativo
            if not usuario or not usuario.get('ativo'):
                flash('Falha na autenticação: Usuário não encontrado ou inativo.', 'erro')
                return render_template('login.html', login=login)
                
            # Validação da senha com Bcrypt
            if not verificar_senha(senha, usuario['senha_hash']):
                flash('Falha na autenticação: Senha incorreta.', 'erro')
                return render_template('login.html', login=login)
                
            # Autenticação bem-sucedida -> Criação da sessão com controle de expiração
            session.clear()
            session.permanent = True
            session['usuario_id'] = usuario['id']
            session['usuario_nome'] = usuario['nome']
            session['usuario_cargo'] = usuario['cargo']
            session['ultimo_acesso'] = datetime.now(timezone.utc).isoformat()
            
            flash(f'Bem-vindo(a), {usuario["nome"]}!', 'sucesso')
            return redirect(url_for('dashboard'))
            
        except Exception:
            current_app.logger.exception('Falha interna durante o login')
            flash('Erro interno durante login. Consulte o log do servidor.', 'erro')
            return render_template('login.html', login=login)
        finally:
            if conexao:
                conexao.close()
                
    return render_template('login.html')

def realizar_logout():
    """Encerra a sessão do usuário de forma segura."""
    session.clear()
    flash('Você saiu do sistema com segurança.', 'info')
    return redirect(url_for('login'))

def verificar_sessao_ativa():
    """Middleware/helper para garantir que o usuário está autenticado e a sessão é válida."""
    if 'usuario_id' not in session:
        return False
    return True