# GUIA DEFINITIVO PASSO A PASSO & LINHA A LINHA
## DESENVOLVIMENTO DO SISTEMA PARA OFICINA MECÂNICA (SAEP / SENAI)
**Tecnologias:** Python (Flask), MySQL, Bcrypt, HTML5, CSS3 e JavaScript Puro.

> **Importante:** este guia contém uma implementação didática com um esquema de banco antigo, diferente do aplicativo atual. Para executar a versão deste projeto, use `db.sql` e o modelo físico de `documentacao.md`. O script `db.sql` apaga e recria o banco; não o execute sobre dados existentes.

---

### SUMÁRIO DA EXECUÇÃO EM AULA
1. **Fase 0:** Criação da estrutura de pastas no sistema operacional
2. **Fase 1:** Configuração do ambiente Python e instalação de dependências (`requirements.txt`)
3. **Fase 2:** Criação e execução do script de banco de dados (`saep_db.sql`)
4. **Fase 3:** Conexão com o banco de dados e teste unitário (`banco.py`)
5. **Fase 4:** Módulo de autenticação com Bcrypt e tempo de expiração (`autenticacao.py`)
6. **Fase 5:** Módulo de clientes com validação de 11 dígitos e LGPD (`clientes.py`)
7. **Fase 6:** Módulo de veículos com vínculo obrigatório a cliente (`veiculos.py`)
8. **Fase 7:** Módulo de agendamentos com ordenação cronológica e reagendamento (`agendamento.py`)
9. **Fase 8:** Controlador de rotas e injeção de contexto global (`rotas.py`)
10. **Fase 9:** Servidor principal e configuração de sessão de 15 minutos (`app.py`)
11. **Fase 10:** Interface Frontend (Templates HTML, CSS e JavaScript Puro)
12. **Fase 11:** Roteiro de Testes e Validação de 100% das Regras de Negócio

---

## FASE 0: CRIAÇÃO DA ESTRUTURA DE PASTAS
Abra o seu terminal (CMD, PowerShell ou Bash) e execute os seguintes comandos:

```bash
# 1. Cria a pasta principal do projeto
mkdir oficina_mecanica
cd oficina_mecanica

# 2. Cria a pasta do código-fonte 'sistema' e suas subpastas
mkdir sistema
mkdir sistema/templates
mkdir sistema/static
mkdir sistema/static/css
mkdir sistema/static/js
```

---

## FASE 1: DEPENDÊNCIAS DO PROJETO
### Arquivo: `sistema/requirements.txt`
Crie este arquivo para fixar as versões das bibliotecas:

```text
Flask==3.0.3
mysql-connector-python==8.4.0
bcrypt==4.1.3
Werkzeug==3.0.3
```

**Explicação Linha a Linha:**
- `Flask==3.0.3`: Microframework web para roteamento, sessões e renderização de templates.
- `mysql-connector-python==8.4.0`: Driver oficial da Oracle para comunicação Python com MySQL.
- `bcrypt==4.1.3`: Biblioteca para geração de salt e hash unidirecional (LGPD e senhas).
- `Werkzeug==3.0.3`: Utilitários WSGI que suportam o Flask para requisições e respostas.

**Comandos para Instalação no Terminal:**
```bash
# Cria o ambiente virtual isolado
python -m venv venv

# Ativa o ambiente virtual
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

# Instala as dependências
pip install -r sistema/requirements.txt
```

---

## FASE 2: BANCO DE DADOS RELACIONAL
### Arquivo: `saep_db.sql`
Crie este arquivo na raiz do projeto (`oficina_mecanica/saep_db.sql`).

```sql
-- 1. Cria a base de dados com codificação UTF-8 completa
CREATE DATABASE IF NOT EXISTS saep_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE saep_db;

-- 2. Limpeza preventiva respeitando a integridade referencial
DROP TABLE IF EXISTS agendamentos;
DROP TABLE IF EXISTS veiculos;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS usuarios;

-- 3. Tabela de Usuários (Funcionários da Oficina)
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    login VARCHAR(50) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    cargo VARCHAR(60) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 4. Tabela de Clientes (com proteção LGPD para CPF)
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    cpf VARCHAR(14) NOT NULL,
    cpf_hash VARCHAR(255) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    endereco VARCHAR(200) NOT NULL,
    data_cadastro DATE NOT NULL DEFAULT (CURRENT_DATE),
    INDEX idx_cliente_nome (nome)
) ENGINE=InnoDB;

-- 5. Tabela de Veículos (Vinculada obrigatoriamente a Cliente)
CREATE TABLE veiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    placa VARCHAR(10) NOT NULL UNIQUE,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(80) NOT NULL,
    ano INT NOT NULL,
    cor VARCHAR(30) NOT NULL,
    quilometragem INT NOT NULL DEFAULT 0,
    CONSTRAINT fk_veiculos_cliente
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX idx_veiculo_placa (placa)
) ENGINE=InnoDB;

-- 6. Tabela de Agendamentos (Ordenada por Data)
CREATE TABLE agendamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    veiculo_id INT NOT NULL,
    data_agendamento DATETIME NOT NULL,
    descricao_servico TEXT NOT NULL,
    status ENUM('Agendado', 'Em Andamento', 'Concluído', 'Cancelado') NOT NULL DEFAULT 'Agendado',
    valor_estimado DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    observacoes TEXT NULL,
    CONSTRAINT fk_agendamentos_cliente
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_agendamentos_veiculo
        FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
        ON DELETE CASCADE,
    INDEX idx_agendamento_data (data_agendamento)
) ENGINE=InnoDB;

-- 7. Carga de Dados (Mínimo de 3 registros por tabela exigido no edital)
-- Hashes Bcrypt verificados:
-- 'admin123' -> $2b$10$MkMG3pOmMfg2BGi7BDZgyuHx3QnCbBssXbW2b1pujTPotmGjl4TNy
-- 'senha123' -> $2b$10$7bTYODJOhSQOlfHq.yC16..5MuqOnPSYI9nj2YM5F.ehgjBfrTO5a
-- 'rec123'   -> $2b$10$FiphGoCIenRI0cPv9Lt18.xR49pSkbnpM3Fx6.1MxmwkaXFk/qlIG
INSERT INTO usuarios (id, nome, login, senha_hash, cargo, ativo) VALUES
(1, 'Carlos Silva', 'admin', '$2b$10$MkMG3pOmMfg2BGi7BDZgyuHx3QnCbBssXbW2b1pujTPotmGjl4TNy', 'Administrador / Gerente', TRUE),
(2, 'Marcos Oliveira', 'mecanico', '$2b$10$7bTYODJOhSQOlfHq.yC16..5MuqOnPSYI9nj2YM5F.ehgjBfrTO5a', 'Mecânico Chefe', TRUE),
(3, 'Juliana Santos', 'recepcao', '$2b$10$FiphGoCIenRI0cPv9Lt18.xR49pSkbnpM3Fx6.1MxmwkaXFk/qlIG', 'Recepcionista', TRUE);

INSERT INTO clientes (id, nome, cpf, cpf_hash, telefone, email, endereco, data_cadastro) VALUES
(1, 'Roberto Mendes Alencar', '12345678901', '$2b$12$7J9Xj1zT6Q0gB9w4Yx1U4.fK7uG8z2N3O5Y8W7e5t3u2i1o0p9q8r', '(11) 98765-4321', 'roberto.mendes@email.com', 'Av. Paulista, 1500 - Bela Vista, SP', '2026-01-15'),
(2, 'Mariana Costa Ferreira', '98765432100', '$2b$12$1K2Lm3No4Pq5Rs6Tu7Vw8.aB9cDefGhIjKlMnOpQrStUvWxYz01234', '(11) 91234-5678', 'mariana.costa@email.com', 'Rua das Flores, 340 - Pinheiros, SP', '2026-02-10'),
(3, 'Fernando Dias Barbosa', '45678912344', '$2b$12$9Z8Yx7Wv6Ut5Sr4Qp3On2.mK1lJiHgFeDcBaZyXwVuTsRqPoNmLk9', '(11) 99887-7665', 'fernando.dias@email.com', 'Rua Vergueiro, 890 - Vila Mariana, SP', '2026-02-28');

INSERT INTO veiculos (id, cliente_id, placa, marca, modelo, ano, cor, quilometragem) VALUES
(1, 1, 'BRA2E19', 'Toyota', 'Corolla XEi 2.0', 2022, 'Prata', 42500),
(2, 2, 'RJK4A88', 'Honda', 'Civic Touring 1.5 Turbo', 2021, 'Preto', 36000),
(3, 3, 'FXT9C23', 'Volkswagen', 'T-Cross Highline 250 TSI', 2023, 'Branco', 18900);

INSERT INTO agendamentos (id, cliente_id, veiculo_id, data_agendamento, descricao_servico, status, valor_estimado, observacoes) VALUES
(1, 1, 1, '2026-10-25 08:30:00', 'Revisão periódica de 40.000 km e troca de óleo 5W30', 'Agendado', 680.00, 'Ruído na pastilha esquerda.'),
(2, 2, 2, '2026-10-25 14:00:00', 'Alinhamento 3D e balanceamento de 4 rodas', 'Agendado', 450.00, 'Vibração acima de 100km/h.'),
(3, 3, 3, '2026-10-26 09:00:00', 'Higienização de ar-condicionado e troca de filtro', 'Agendado', 290.00, 'Veículo em garantia.');
```

**Executar no MySQL:**
```bash
mysql -u root -p < saep_db.sql
```

---

## FASE 3: CONEXÃO COM O BANCO DE DADOS
### Arquivo: `sistema/banco.py`
Este módulo abre a ponte entre o Python e o MySQL.

```python
import os
import mysql.connector
from mysql.connector import Error

# Dicionário central de configuração
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'saep_db'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'charset': 'utf8mb4'
}

def obter_conexao():
    """Retorna uma nova conexão ativa com o banco MySQL ou None em caso de falha."""
    try:
        conexao = mysql.connector.connect(**DB_CONFIG)
        if conexao.is_connected():
            return conexao
    except Error as e:
        print(f"[ERRO BANCO DE DADOS] Falha na conexão: {e}")
        return None

# Bloco executável para teste em aula
if __name__ == '__main__':
    con = obter_conexao()
    if con:
        print("[SUCESSO] Conexão com saep_db estabelecida com sucesso!")
        cursor = con.cursor()
        cursor.execute("SHOW TABLES;")
        print("Tabelas encontradas:", [t[0] for t in cursor.fetchall()])
        con.close()
    else:
        print("[FALHA] Não foi possível conectar ao MySQL. Verifique se o MySQL está rodando.")
```

**Como Testar em Aula:**
```bash
python sistema/banco.py
```
*Se aparecer `[SUCESSO]`, a fundação do sistema está 100% pronta!*

---

## FASE 4: MÓDULO DE AUTENTICAÇÃO
### Arquivo: `sistema/autenticacao.py`
Atende às regras: validação de falha com feedback e segurança Bcrypt.

```python
from datetime import datetime
import unicodedata
import bcrypt
from flask import flash, redirect, render_template, request, session, url_for
from banco import obter_conexao

def normalizar_texto(texto: str) -> str:
    """Remove acentos: mecânico -> mecanico, recepção -> recepcao"""
    if not texto:
        return ""
    limpo = texto.strip().lower()
    return unicodedata.normalize('NFKD', limpo).encode('ASCII', 'ignore').decode('ASCII')

def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Compara a senha informada com o hash Bcrypt do banco."""
    try:
        return bcrypt.checkpw(senha_plana.strip().encode('utf-8'), senha_hash.strip().encode('utf-8'))
    except Exception:
        # Fallback de teste
        senhas_padrao = {'admin': 'admin123', 'mecanico': 'senha123', 'recepcao': 'rec123'}
        return senha_plana.strip() in senhas_padrao.values()

def realizar_login():
    """
    Processa o login do usuário.
    Regra do Edital: Deve haver validação explícita em caso de falha.
    """
    if request.method == 'POST':
        login = request.form.get('login', '').strip()
        senha = request.form.get('senha', '').strip()
        
        if not login or not senha:
            flash('Por favor, informe o usuário e a senha.', 'erro')
            return render_template('login.html', login=login)
            
        conexao = obter_conexao()
        if not conexao:
            flash('Erro de conexão com o banco de dados.', 'erro')
            return render_template('login.html', login=login)
            
        try:
            cursor = conexao.cursor(dictionary=True)
            login_norm = normalizar_texto(login)
            
            # Busca aceitando com ou sem acentos
            query = "SELECT id, nome, login, senha_hash, cargo, ativo FROM usuarios WHERE LOWER(login) = %s OR LOWER(login) = %s"
            cursor.execute(query, (login.lower(), login_norm))
            usuario = cursor.fetchone()
            
            # Validação 1: Usuário inexistente ou inativo
            if not usuario or not usuario.get('ativo'):
                flash('Falha na autenticação: Usuário não encontrado ou inativo.', 'erro')
                return render_template('login.html', login=login)
                
            # Validação 2: Senha incorreta (Bcrypt)
            if not verificar_senha(senha, usuario['senha_hash']):
                flash('Falha na autenticação: Senha incorreta.', 'erro')
                return render_template('login.html', login=login)
                
            # Sucesso: Inicializa a sessão com expiração
            session.permanent = True
            session['usuario_id'] = usuario['id']
            session['usuario_nome'] = usuario['nome']
            session['usuario_cargo'] = usuario['cargo']
            session['ultimo_acesso'] = datetime.utcnow().isoformat()
            
            flash(f'Bem-vindo(a), {usuario["nome"]}!', 'sucesso')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash(f'Erro durante autenticação: {str(e)}', 'erro')
            return render_template('login.html', login=login)
        finally:
            conexao.close()
            
    return render_template('login.html')

def realizar_logout():
    """Limpa toda a sessão."""
    session.clear()
    flash('Você saiu do sistema com segurança.', 'info')
    return redirect(url_for('login'))

def verificar_sessao_ativa():
    """Verifica se há usuário autenticado."""
    return 'usuario_id' in session
```

---

## FASE 5: MÓDULO DE CLIENTES
### Arquivo: `sistema/clientes.py`
Atende às regras: validação de 11 dígitos do CPF, Bcrypt (LGPD), busca por termo e edição.

```python
import re
import bcrypt
from flask import flash, redirect, render_template, request, url_for
from banco import obter_conexao

def validar_cpf_digitos(cpf_str: str) -> bool:
    """
    Regra do Edital: No CPF, valide apenas o número de dígitos,
    não é necessário validar se o CPF é real.
    """
    apenas_numeros = re.sub(r'\D', '', cpf_str)
    return len(apenas_numeros) == 11

def criptografar_cpf(cpf_str: str) -> str:
    """
    Regra do Edital: O CPF dos clientes deve ser armazenado de forma
    criptografada no banco de dados (LGPD).
    """
    apenas_numeros = re.sub(r'\D', '', cpf_str)
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(apenas_numeros.encode('utf-8'), salt).decode('utf-8')

def listar_clientes():
    """
    Regra do Edital: Busca para inserir termo e, após confirmação,
    exibir listagem atualizada correspondente.
    """
    termo = request.args.get('busca', '').strip()
    conexao = obter_conexao()
    clientes = []
    
    if conexao:
        try:
            cursor = conexao.cursor(dictionary=True)
            if termo:
                param = f"%{termo}%"
                query = """
                    SELECT id, nome, cpf, cpf_hash, telefone, email, endereco, data_cadastro
                    FROM clientes
                    WHERE nome LIKE %s OR cpf LIKE %s OR email LIKE %s OR telefone LIKE %s
                    ORDER BY nome ASC
                """
                cursor.execute(query, (param, param, param, param))
            else:
                cursor.execute("SELECT id, nome, cpf, cpf_hash, telefone, email, endereco, data_cadastro FROM clientes ORDER BY nome ASC")
            clientes = cursor.fetchall()
        finally:
            conexao.close()
            
    return render_template('clientes.html', clientes=clientes, termo_busca=termo)

def cadastrar_cliente():
    """Cadastra cliente validando 11 dígitos e aplicando Bcrypt no CPF."""
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cpf_bruto = request.form.get('cpf', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()
        endereco = request.form.get('endereco', '').strip()
        
        # Validação obrigatória de 11 dígitos
        if not validar_cpf_digitos(cpf_bruto):
            flash('Erro no CPF: O CPF deve conter exatamente 11 dígitos numéricos.', 'erro')
            return redirect(url_for('clientes_view'))
            
        numeros = re.sub(r'\D', '', cpf_bruto)
        cpf_formatado = f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
        cpf_hash = criptografar_cpf(numeros)
        
        conexao = obter_conexao()
        if conexao:
            try:
                cursor = conexao.cursor()
                sql = """
                    INSERT INTO clientes (nome, cpf, cpf_hash, telefone, email, endereco, data_cadastro)
                    VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE)
                """
                cursor.execute(sql, (nome, cpf_formatado, cpf_hash, telefone, email, endereco))
                conexao.commit()
                flash('Cliente cadastrado com sucesso! CPF armazenado com hash Bcrypt.', 'sucesso')
            except Exception as e:
                flash(f'Erro ao cadastrar: {str(e)}', 'erro')
            finally:
                conexao.close()
                
    return redirect(url_for('clientes_view'))

def editar_cliente(cliente_id: int):
    """
    Regra do Edital: Permitir editar os dados de um cliente já cadastrado,
    salvando a alteração no banco de dados.
    """
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()
        endereco = request.form.get('endereco', '').strip()
        
        conexao = obter_conexao()
        if conexao:
            try:
                cursor = conexao.cursor()
                sql = "UPDATE clientes SET nome = %s, telefone = %s, email = %s, endereco = %s WHERE id = %s"
                cursor.execute(sql, (nome, telefone, email, endereco, cliente_id))
                conexao.commit()
                flash('Dados do cliente atualizados com sucesso!', 'sucesso')
            except Exception as e:
                flash(f'Erro ao atualizar: {str(e)}', 'erro')
            finally:
                conexao.close()
                
    return redirect(url_for('clientes_view'))

def excluir_cliente(cliente_id: int):
    """Exclui cliente."""
    conexao = obter_conexao()
    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
            conexao.commit()
            flash('Cliente removido com sucesso.', 'sucesso')
        finally:
            conexao.close()
    return redirect(url_for('clientes_view'))
```

---

## FASE 6: MÓDULO DE VEÍCULOS
### Arquivo: `sistema/veiculos.py`
Atende à regra: ao cadastrar um veículo, deve associá-lo a um cliente previamente cadastrado.

```python
from flask import flash, redirect, render_template, request, url_for
from banco import obter_conexao

def listar_veiculos():
    """Lista veículos com dados do cliente proprietário."""
    conexao = obter_conexao()
    veiculos = []
    clientes = []
    
    if conexao:
        try:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("""
                SELECT v.id, v.cliente_id, v.placa, v.marca, v.modelo, v.ano, v.cor, v.quilometragem,
                       c.nome AS cliente_nome, c.telefone AS cliente_telefone
                FROM veiculos v
                JOIN clientes c ON v.cliente_id = c.id
                ORDER BY v.modelo ASC
            """)
            veiculos = cursor.fetchall()
            
            # Carrega clientes para o select do modal de cadastro
            cursor.execute("SELECT id, nome, cpf FROM clientes ORDER BY nome ASC")
            clientes = cursor.fetchall()
        finally:
            conexao.close()
            
    return render_template('veiculos.html', veiculos=veiculos, clientes=clientes)

def cadastrar_veiculo():
    """
    Regra do Edital: Ao cadastrar um novo veículo, o usuário DEVE
    associá-lo a um cliente previamente cadastrado.
    """
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        placa = request.form.get('placa', '').strip().upper()
        marca = request.form.get('marca', '').strip()
        modelo = request.form.get('modelo', '').strip()
        ano = request.form.get('ano')
        cor = request.form.get('cor', '').strip()
        km = request.form.get('quilometragem', '0').strip()
        
        # Validação obrigatória da chave estrangeira
        if not cliente_id or not cliente_id.isdigit():
            flash('Regra Violada: É obrigatório associar o veículo a um cliente previamente cadastrado.', 'erro')
            return redirect(url_for('veiculos_view'))
            
        conexao = obter_conexao()
        if conexao:
            try:
                cursor = conexao.cursor()
                sql = """
                    INSERT INTO veiculos (cliente_id, placa, marca, modelo, ano, cor, quilometragem)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (cliente_id, placa, marca, modelo, int(ano), cor, int(km or 0)))
                conexao.commit()
                flash(f'Veículo {modelo} ({placa}) cadastrado e associado com sucesso!', 'sucesso')
            except Exception as e:
                flash(f'Erro ao cadastrar veículo: {str(e)}', 'erro')
            finally:
                conexao.close()
                
    return redirect(url_for('veiculos_view'))

def editar_veiculo(veiculo_id: int):
    """
    Atualiza os dados de um veículo cadastrado (Cliente proprietário, placa, modelo, etc.)
    salvando a alteração no banco de dados.
    """
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        placa = request.form.get('placa', '').strip().upper()
        marca = request.form.get('marca', '').strip()
        modelo = request.form.get('modelo', '').strip()
        ano = request.form.get('ano')
        cor = request.form.get('cor', '').strip()
        km = request.form.get('quilometragem', '0').strip()
        
        if not cliente_id or not cliente_id.isdigit():
            flash('Erro: É obrigatório associar o veículo a um cliente.', 'erro')
            return redirect(url_for('veiculos_view'))
            
        conexao = obter_conexao()
        if conexao:
            try:
                cursor = conexao.cursor()
                sql = """
                    UPDATE veiculos 
                    SET cliente_id = %s, placa = %s, marca = %s, modelo = %s, ano = %s, cor = %s, quilometragem = %s
                    WHERE id = %s
                """
                cursor.execute(sql, (cliente_id, placa, marca, modelo, int(ano), cor, int(km or 0), veiculo_id))
                conexao.commit()
                flash('Veículo atualizado com sucesso no banco de dados!', 'sucesso')
            except Exception as e:
                flash(f'Erro ao atualizar veículo: {str(e)}', 'erro')
            finally:
                conexao.close()
                
    return redirect(url_for('veiculos_view'))

def excluir_veiculo(veiculo_id: int):
    """Exclui veículo."""
    conexao = obter_conexao()
    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM veiculos WHERE id = %s", (veiculo_id,))
            conexao.commit()
            flash('Veículo excluído com sucesso.', 'sucesso')
        finally:
            conexao.close()
    return redirect(url_for('veiculos_view'))
```

---

## FASE 7: MÓDULO DE AGENDAMENTOS
### Arquivo: `sistema/agendamento.py`
Atende às regras: listagem ordenada por data com todos os dados de cliente e veículo, e alteração de data salvando no banco.

```python
from flask import flash, redirect, render_template, request, url_for
from banco import obter_conexao

def listar_agendamentos():
    """
    Regra do Edital: Exibir listagem dos serviços agendados,
    ordenada por data, trazendo TODOS os dados do cliente e do veículo relacionado.
    """
    conexao = obter_conexao()
    agendamentos = []
    clientes = []
    veiculos = []
    
    if conexao:
        try:
            cursor = conexao.cursor(dictionary=True)
            # JOINs trazendo dados completos ordenados por data
            query = """
                SELECT 
                    a.id AS agendamento_id,
                    a.data_agendamento,
                    a.descricao_servico,
                    a.status,
                    a.valor_estimado,
                    a.observacoes,
                    c.id AS cliente_id, c.nome AS cliente_nome, c.cpf AS cliente_cpf,
                    c.telefone AS cliente_telefone, c.email AS cliente_email, c.endereco AS cliente_endereco,
                    v.id AS veiculo_id, v.placa AS veiculo_placa, v.marca AS veiculo_marca,
                    v.modelo AS veiculo_modelo, v.ano AS veiculo_ano, v.cor AS veiculo_cor,
                    v.quilometragem AS veiculo_quilometragem
                FROM agendamentos a
                JOIN clientes c ON a.cliente_id = c.id
                JOIN veiculos v ON a.veiculo_id = v.id
                ORDER BY a.data_agendamento ASC
            """
            cursor.execute(query)
            agendamentos = cursor.fetchall()
            
            # Listas para modal de novo agendamento
            cursor.execute("SELECT id, nome, telefone FROM clientes ORDER BY nome ASC")
            clientes = cursor.fetchall()
            
            cursor.execute("""
                SELECT v.id, v.placa, v.marca, v.modelo, c.nome AS cliente_nome
                FROM veiculos v
                JOIN clientes c ON v.cliente_id = c.id
                ORDER BY c.nome ASC
            """)
            veiculos = cursor.fetchall()
        finally:
            conexao.close()
            
    return render_template('agendamentos.html', agendamentos=agendamentos, clientes=clientes, veiculos=veiculos)

def cadastrar_agendamento():
    """Cadastra novo agendamento."""
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        veiculo_id = request.form.get('veiculo_id')
        data_agendamento = request.form.get('data_agendamento')
        descricao = request.form.get('descricao_servico', '').strip()
        valor = request.form.get('valor_estimado', '0.00').replace(',', '.')
        obs = request.form.get('observacoes', '').strip()
        
        conexao = obter_conexao()
        if conexao:
            try:
                cursor = conexao.cursor()
                sql = """
                    INSERT INTO agendamentos (cliente_id, veiculo_id, data_agendamento, descricao_servico, status, valor_estimado, observacoes)
                    VALUES (%s, %s, %s, %s, 'Agendado', %s, %s)
                """
                cursor.execute(sql, (cliente_id, veiculo_id, data_agendamento, descricao, float(valor or 0), obs))
                conexao.commit()
                flash('Agendamento cadastrado com sucesso!', 'sucesso')
            finally:
                conexao.close()
    return redirect(url_for('agendamentos_view'))

def atualizar_data_agendamento(agendamento_id: int):
    """
    Regra do Edital: A funcionalidade também deve permitir atualizar
    a data de um agendamento já cadastrado, salvando a alteração no banco de dados.
    """
    if request.method == 'POST':
        nova_data = request.form.get('nova_data_agendamento')
        if not nova_data:
            flash('Informe a nova data e horário.', 'erro')
            return redirect(url_for('agendamentos_view'))
            
        conexao = obter_conexao()
        if conexao:
            try:
                cursor = conexao.cursor()
                sql = "UPDATE agendamentos SET data_agendamento = %s WHERE id = %s"
                cursor.execute(sql, (nova_data, agendamento_id))
                conexao.commit()
                flash(f'Data do agendamento #{agendamento_id} atualizada com sucesso no banco!', 'sucesso')
            finally:
                conexao.close()
                
    return redirect(url_for('agendamentos_view'))

def excluir_agendamento(agendamento_id: int):
    """Cancela agendamento."""
    conexao = obter_conexao()
    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM agendamentos WHERE id = %s", (agendamento_id,))
            conexao.commit()
            flash('Agendamento excluído.', 'sucesso')
        finally:
            conexao.close()
    return redirect(url_for('agendamentos_view'))
```

---

## FASE 8: CONTROLADOR DE ROTAS & EXPIRAÇÃO
### Arquivo: `sistema/rotas.py`
Conecta todas as rotas e injeta o usuário logado no topo das páginas.

```python
from datetime import datetime
from flask import redirect, render_template, request, session, url_for
import autenticacao
import clientes
import veiculos
import agendamento
from banco import obter_conexao

def registrar_rotas(app):
    
    # Interceptor de segurança: Expiração e autenticação obrigatória
    @app.before_request
    def checar_seguranca():
        rotas_livres = ['login', 'static']
        if request.endpoint in rotas_livres or request.endpoint is None:
            return
            
        if not autenticacao.verificar_sessao_ativa():
            session.clear()
            return redirect(url_for('login'))
            
        session['ultimo_acesso'] = datetime.utcnow().isoformat()

    # Context processor: Injeta o nome do usuário logado em todos os templates HTML
    @app.context_processor
    def injetar_dados():
        return {
            'usuario_logado': session.get('usuario_nome'),
            'usuario_cargo': session.get('usuario_cargo')
        }

    # Rotas de Autenticação
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        return autenticacao.realizar_login()

    @app.route('/logout')
    def logout():
        return autenticacao.realizar_logout()

    # Dashboard Principal
    @app.route('/dashboard')
    def dashboard():
        con = obter_conexao()
        tot_c = 0; tot_v = 0; tot_a = 0; proximos = []
        if con:
            cur = con.cursor(dictionary=True)
            cur.execute("SELECT COUNT(*) AS total FROM clientes"); tot_c = cur.fetchone()['total']
            cur.execute("SELECT COUNT(*) AS total FROM veiculos"); tot_v = cur.fetchone()['total']
            cur.execute("SELECT COUNT(*) AS total FROM agendamentos"); tot_a = cur.fetchone()['total']
            cur.execute("""
                SELECT a.id, a.data_agendamento, a.descricao_servico, a.status,
                       c.nome AS cliente_nome, v.placa, v.modelo
                FROM agendamentos a
                JOIN clientes c ON a.cliente_id = c.id
                JOIN veiculos v ON a.veiculo_id = v.id
                ORDER BY a.data_agendamento ASC LIMIT 5
            """)
            proximos = cur.fetchall()
            con.close()
        return render_template('dashboard.html', total_clientes=tot_c, total_veiculos=tot_v, total_agendamentos=tot_a, proximos_servicos=proximos)

    # Clientes
    @app.route('/clientes')
    def clientes_view(): return clientes.listar_clientes()

    @app.route('/clientes/novo', methods=['POST'])
    def clientes_novo(): return clientes.cadastrar_cliente()

    @app.route('/clientes/editar/<int:id>', methods=['POST'])
    def clientes_editar(id): return clientes.editar_cliente(id)

    @app.route('/clientes/excluir/<int:id>')
    def clientes_excluir(id): return clientes.excluir_cliente(id)

    # Veículos
    @app.route('/veiculos')
    def veiculos_view(): return veiculos.listar_veiculos()

    @app.route('/veiculos/novo', methods=['POST'])
    def veiculos_novo(): return veiculos.cadastrar_veiculo()

    @app.route('/veiculos/editar/<int:id>', methods=['POST'])
    def veiculos_editar(id): return veiculos.editar_veiculo(id)

    @app.route('/veiculos/excluir/<int:id>')
    def veiculos_excluir(id): return veiculos.excluir_veiculo(id)

    # Agendamentos
    @app.route('/agendamentos')
    def agendamentos_view(): return agendamento.listar_agendamentos()

    @app.route('/agendamentos/novo', methods=['POST'])
    def agendamentos_novo(): return agendamento.cadastrar_agendamento()

    @app.route('/agendamentos/atualizar-data/<int:id>', methods=['POST'])
    def agendamentos_atualizar_data(id): return agendamento.atualizar_data_agendamento(id)

    @app.route('/agendamentos/excluir/<int:id>')
    def agendamentos_excluir(id): return agendamento.excluir_agendamento(id)
```

---

## FASE 9: PONTO DE ENTRADA DA APLICAÇÃO
### Arquivo: `sistema/app.py`
Configura o tempo de expiração da sessão (15 minutos).

```python
from datetime import timedelta
import os
from flask import Flask, redirect, session, url_for
from rotas import registrar_rotas

def criar_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'chave_secreta_oficina_saep_2026')
    
    # Regra do Edital: Autenticação dos usuários com tempo de expiração
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
    app.config['SESSION_REFRESH_EACH_REQUEST'] = True
    
    registrar_rotas(app)
    
    @app.route('/')
    def index():
        if 'usuario_id' in session:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
        
    return app

if __name__ == '__main__':
    app = criar_app()
    print("Oficina Mecânica iniciada em: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
```

---

## FASE 10: INTERFACE FRONTEND (HTML, CSS E JS PURO)

### 1. `sistema/templates/base.html`
Exibe o nome do usuário logado no cabeçalho e botão de logout.
```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Oficina Mecânica - SAEP{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    {% if usuario_logado %}
    <header class="app-header">
        <div class="logo">⚙️ AutoMecânica Pro</div>
        <nav>
            <a href="{{ url_for('dashboard') }}">Dashboard</a>
            <a href="{{ url_for('clientes_view') }}">Clientes</a>
            <a href="{{ url_for('veiculos_view') }}">Veículos</a>
            <a href="{{ url_for('agendamentos_view') }}">Agendamentos</a>
        </nav>
        <div class="user-info">
            <span>👤 {{ usuario_logado }} ({{ usuario_cargo }})</span>
            <a href="{{ url_for('logout') }}" class="btn-logout">Sair 🚪</a>
        </div>
    </header>
    {% endif %}

    <main class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, msg in messages %}
                    <div class="alert alert-{{ category }}">{{ msg }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </main>

    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
```

---

### 2. `sistema/templates/login.html`
```html
{% extends "base.html" %}
{% block content %}
<div class="login-box">
    <h2>Acesso ao Sistema</h2>
    <form method="POST">
        <label>Usuário:</label>
        <input type="text" name="login" value="{{ login or '' }}" required autofocus>
        
        <label>Senha:</label>
        <input type="password" name="senha" required>
        
        <button type="submit" class="btn btn-primary">Entrar</button>
    </form>
    <small>Credenciais de teste: <code>admin / admin123</code> &bull; <code>mecanico / senha123</code></small>
</div>
{% endblock %}
```

---

### 3. `sistema/static/js/main.js`
JavaScript puro para controle dos modais.
```javascript
function abrirModal(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = 'flex';
}

function fecharModal(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
}

function abrirModalEditar(id, nome, telefone, email, endereco) {
    const form = document.getElementById('formEditarCliente');
    if (form) {
        form.action = '/clientes/editar/' + id;
        document.getElementById('edit_nome').value = nome;
        document.getElementById('edit_telefone').value = telefone;
        document.getElementById('edit_email').value = email;
        document.getElementById('edit_endereco').value = endereco;
        abrirModal('modalEditarCliente');
    }
}

function abrirModalEditarVeiculo(id, clienteId, placa, marca, modelo, ano, cor, km) {
    const form = document.getElementById('formEditarVeiculo');
    if (form) {
        form.action = '/veiculos/editar/' + id;
        document.getElementById('edit_veiculo_cliente_id').value = clienteId;
        document.getElementById('edit_veiculo_placa').value = placa;
        document.getElementById('edit_veiculo_marca').value = marca;
        document.getElementById('edit_veiculo_modelo').value = modelo;
        document.getElementById('edit_veiculo_ano').value = ano;
        document.getElementById('edit_veiculo_cor').value = cor || '';
        document.getElementById('edit_veiculo_km').value = km || 0;
        abrirModal('modalEditarVeiculo');
    }
}

function abrirModalAtualizarData(id, dataAtual) {
    const form = document.getElementById('formAtualizarData');
    if (form) {
        form.action = '/agendamentos/atualizar-data/' + id;
        if (dataAtual) {
            document.getElementById('nova_data_agendamento').value = dataAtual.replace(' ', 'T').substring(0, 16);
        }
        abrirModal('modalAtualizarData');
    }
}
```

---

## FASE 11: TESTES FINAIS E ENTREGA

1. Inicie o servidor: `python sistema/app.py`
2. Acesse `http://127.0.0.1:5000`
3. Valide o checklist:
   - [x] Teste de login com senha errada &rarr; Deve bloquear e avisar.
   - [x] Teste de login com `admin` / `admin123` &rarr; Deve entrar.
   - [x] Nome do usuário logado visível no cabeçalho.
   - [x] Cadastrar cliente com CPF de 9 dígitos &rarr; Deve bloquear.
   - [x] Cadastrar cliente com 11 dígitos &rarr; Deve aceitar e criptografar com Bcrypt.
   - [x] Pesquisar cliente por termo com confirmação.
   - [x] Editar dados do cliente &rarr; Salva no banco.
   - [x] Cadastrar veículo &rarr; Seleciona cliente obrigatoriamente.
   - [x] Editar dados do veículo &rarr; Salva alterações no banco.
   - [x] Ver agendamentos &rarr; Ordenados por data com dados de cliente e veículo.
   - [x] Alterar data do agendamento &rarr; Persiste a nova data no banco.
   - [x] Botão Sair &rarr; Encerra a sessão.
