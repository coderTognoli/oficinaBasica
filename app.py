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
