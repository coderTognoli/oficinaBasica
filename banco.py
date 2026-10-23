"""
Módulo: banco.py
Gerencia a conexão com o banco de dados MYSQL para a aplicação
"""

import os
import mysql.connector 
from mysql.connector import Error

# Configurações do Banco de Dados MySQL
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'Senai@118'),
    'database': os.environ.get('DB_NAME', 'saep_db'),
    'port': int(os.environ.get('DB_PORT', '3306')),
    'charset': 'utf8mb4'
}

def obter_conexao():
    """
    Retorna uma conexão ativa com o banco MySQL
    Em caso de falha, exibe uma mensagem no terminal
    """
    try:
        conexao = mysql.connector.connect(**DB_CONFIG)
        if conexao.is_connected():
            return conexao

    except Error as e:
        print(f"[ERRO BANCO DE DADOS] Não foi possível conectar ao MySQL: {e}")
        return None

def testar_conexao():
    """Função utilizada para testar a conexão passo a passo."""
    conexao = obter_conexao()
    if conexao:
        print(f"[SUCESSO] Conexão com o banco de dados MySQL 'saep_db' realizada com sucesso")
        cursor = conexao.cursor()
        cursor.execute('SHOW TABLES;')
        tabelas = cursor.fetchall()
        print(f"Tabelas encontradas: {[t[0] for t in tabelas]}")
        conexao.close()
        return True
    else:
        print("[FALHA] Não foi possível conexão com o MySQL.")
        return False

if __name__ == '__main__':
    testar_conexao()