#!/usr/bin/env python3
"""
Sistema Híbrido de Sinais de Criptomoedas
Ponto de entrada principal para deploy no Railway
"""

import os
import threading
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import logging

# Importar módulos do sistema
from scanner_hybrid import main as scanner_main
from state_manager import load_open_trades
from ml_model_loader import ml_model
from ai_predictor import ai_predictor

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação Flask
app = Flask(__name__)
CORS(app)

# Estado global do sistema
system_status = {
    "running": False,
    "last_scan": None,
    "total_signals": 0,
    "open_trades": 0,
    "ml_status": "checking",
    "ai_status": "checking"
}

def update_system_status():
    """Atualiza o status do sistema"""
    try:
        # Verificar status do ML
        if ml_model.model is not None:
            system_status["ml_status"] = "active"
        else:
            system_status["ml_status"] = "inactive"
        
        # Verificar status da IA
        if hasattr(ai_predictor, 'model') and ai_predictor.model is not None:
            system_status["ai_status"] = "active"
        else:
            system_status["ai_status"] = "training"
        
        # Verificar trades abertos
        open_trades = load_open_trades()
        system_status["open_trades"] = len(open_trades)
        
    except Exception as e:
        logger.error(f"Erro ao atualizar status: {e}")

def run_scanner():
    """Executa o scanner em thread separada"""
    try:
        system_status["running"] = True
        logger.info("🚀 Iniciando scanner híbrido...")
        scanner_main()
    except Exception as e:
        logger.error(f"Erro no scanner: {e}")
        system_status["running"] = False

# Rotas da API
@app.route('/')
def home():
    """Página inicial com status do sistema"""
    return jsonify({
        "message": "Sistema Híbrido de Sinais de Criptomoedas",
        "version": "1.0.0",
        "status": "online"
    })

@app.route('/status')
def status():
    """Retorna status detalhado do sistema"""
    update_system_status()
    return jsonify(system_status)

@app.route('/health')
def health():
    """Health check para o Railway"""
    return jsonify({"status": "healthy", "timestamp": time.time()})

@app.route('/start', methods=['POST'])
def start_scanner():
    """Inicia o scanner"""
    if not system_status["running"]:
        scanner_thread = threading.Thread(target=run_scanner, daemon=True)
        scanner_thread.start()
        return jsonify({"message": "Scanner iniciado", "status": "starting"})
    else:
        return jsonify({"message": "Scanner já está rodando", "status": "running"})

@app.route('/stop', methods=['POST'])
def stop_scanner():
    """Para o scanner"""
    system_status["running"] = False
    return jsonify({"message": "Scanner parado", "status": "stopped"})

@app.route('/trades')
def get_trades():
    """Retorna trades abertos"""
    try:
        trades = load_open_trades()
        return jsonify({"trades": trades, "count": len(trades)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/config')
def get_config():
    """Retorna configuração atual"""
    config = {
        "news_api_configured": bool(os.getenv("NEWS_API_KEY")),
        "telegram_configured": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
        "ml_model_available": ml_model.model is not None,
        "ai_model_available": hasattr(ai_predictor, 'model') and ai_predictor.model is not None
    }
    return jsonify(config)

@app.route('/logs')
def get_logs():
    """Retorna logs recentes (implementação básica)"""
    return jsonify({
        "message": "Logs disponíveis via Railway dashboard",
        "status": system_status
    })

if __name__ == '__main__':
    # Configurar porta para Railway
    port = int(os.environ.get('PORT', 5000))
    
    # Atualizar status inicial
    update_system_status()
    
    # Iniciar scanner automaticamente se configurado
    auto_start = os.getenv('AUTO_START_SCANNER', 'true').lower() == 'true'
    if auto_start:
        logger.info("🔄 Iniciando scanner automaticamente...")
        scanner_thread = threading.Thread(target=run_scanner, daemon=True)
        scanner_thread.start()
    
    # Iniciar aplicação Flask
    logger.info(f"🌐 Iniciando API na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

