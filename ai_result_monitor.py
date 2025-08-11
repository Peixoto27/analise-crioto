import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
from price_fetcher import fetch_all_data
from ai_data_collector import ai_data_collector
from ai_predictor import ai_predictor

class AIResultMonitor:
    """
    Monitora os resultados dos sinais para feedback do sistema de IA
    """
    
    def __init__(self, monitoring_file="ai_monitoring.json"):
        self.monitoring_file = monitoring_file
        self.monitoring_data = self.load_monitoring_data()
    
    def load_monitoring_data(self) -> List[Dict]:
        """Carrega dados de monitoramento"""
        if os.path.exists(self.monitoring_file):
            try:
                with open(self.monitoring_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_monitoring_data(self):
        """Salva dados de monitoramento"""
        with open(self.monitoring_file, 'w') as f:
            json.dump(self.monitoring_data, f, indent=2)
    
    def add_signal_for_monitoring(self, signal: Dict):
        """
        Adiciona um sinal para monitoramento de resultado
        """
        monitoring_entry = {
            'signal_id': signal['id'],
            'symbol': signal['symbol'],
            'entry_price': float(signal['entry_price']),
            'target_price': float(signal['target_price']),
            'stop_loss': float(signal['stop_loss']),
            'created_at': signal['created_at'],
            'status': 'monitoring',  # monitoring, completed
            'result': None,  # success, failure
            'completion_date': None,
            'days_to_result': None,
            'max_price_reached': None,
            'min_price_reached': None
        }
        
        self.monitoring_data.append(monitoring_entry)
        self.save_monitoring_data()
        print(f"[AI_MONITOR] Sinal {signal['symbol']} adicionado para monitoramento")
    
    def check_signal_results(self):
        """
        Verifica resultados dos sinais em monitoramento
        """
        print("[AI_MONITOR] Verificando resultados dos sinais...")
        
        # Filtra sinais ainda em monitoramento
        active_signals = [s for s in self.monitoring_data if s['status'] == 'monitoring']
        
        if not active_signals:
            print("[AI_MONITOR] Nenhum sinal ativo para monitorar")
            return
        
        # Agrupa por símbolo para otimizar chamadas à API
        symbols_to_check = list(set([s['symbol'] for s in active_signals]))
        
        try:
            # Busca dados atuais do mercado
            current_market_data = fetch_all_data(symbols_to_check)
            
            for signal in active_signals:
                symbol = signal['symbol']
                
                if symbol not in current_market_data or current_market_data[symbol].empty:
                    continue
                
                current_price = current_market_data[symbol]['close'].iloc[-1]
                entry_price = signal['entry_price']
                target_price = signal['target_price']
                stop_loss = signal['stop_loss']
                
                # Atualiza preços máximo e mínimo alcançados
                if signal['max_price_reached'] is None:
                    signal['max_price_reached'] = current_price
                    signal['min_price_reached'] = current_price
                else:
                    signal['max_price_reached'] = max(signal['max_price_reached'], current_price)
                    signal['min_price_reached'] = min(signal['min_price_reached'], current_price)
                
                # Verifica se atingiu alvo ou stop
                result = None
                
                if current_price >= target_price:
                    result = 'success'
                    print(f"[AI_MONITOR] ✅ {symbol} atingiu ALVO! Preço: {current_price}")
                elif current_price <= stop_loss:
                    result = 'failure'
                    print(f"[AI_MONITOR] ❌ {symbol} atingiu STOP! Preço: {current_price}")
                
                # Se há resultado, atualiza o sinal
                if result:
                    signal['status'] = 'completed'
                    signal['result'] = result
                    signal['completion_date'] = datetime.now().isoformat()
                    
                    # Calcula dias até resultado
                    created_date = datetime.fromisoformat(signal['created_at'])
                    days_to_result = (datetime.now() - created_date).days
                    signal['days_to_result'] = max(1, days_to_result)  # Mínimo 1 dia
                    
                    # Atualiza dados de treinamento
                    ai_data_collector.update_signal_result(
                        signal['signal_id'], 
                        result, 
                        signal['days_to_result']
                    )
                    
                    print(f"[AI_MONITOR] Resultado do sinal {symbol} registrado: {result}")
            
            # Verifica sinais muito antigos (mais de 7 dias) e marca como expirados
            cutoff_date = datetime.now() - timedelta(days=7)
            
            for signal in active_signals:
                created_date = datetime.fromisoformat(signal['created_at'])
                if created_date < cutoff_date and signal['status'] == 'monitoring':
                    # Determina resultado baseado no melhor preço alcançado
                    entry_price = signal['entry_price']
                    target_price = signal['target_price']
                    max_reached = signal['max_price_reached']
                    
                    # Se chegou perto do alvo (80% do caminho), considera sucesso parcial
                    target_distance = target_price - entry_price
                    achieved_distance = max_reached - entry_price
                    
                    if achieved_distance >= (target_distance * 0.8):
                        result = 'success'
                    else:
                        result = 'failure'
                    
                    signal['status'] = 'completed'
                    signal['result'] = result
                    signal['completion_date'] = datetime.now().isoformat()
                    signal['days_to_result'] = 7
                    
                    ai_data_collector.update_signal_result(signal['signal_id'], result, 7)
                    print(f"[AI_MONITOR] Sinal expirado {signal['symbol']}: {result}")
            
            self.save_monitoring_data()
            
            # Verifica se deve retreinar o modelo
            if ai_predictor.should_retrain():
                print("[AI_MONITOR] Iniciando retreinamento do modelo...")
                ai_predictor.train_model()
        
        except Exception as e:
            print(f"[AI_MONITOR] Erro ao verificar resultados: {e}")
    
    def get_monitoring_statistics(self) -> Dict:
        """Retorna estatísticas de monitoramento"""
        total_monitored = len(self.monitoring_data)
        active_monitoring = len([s for s in self.monitoring_data if s['status'] == 'monitoring'])
        completed = len([s for s in self.monitoring_data if s['status'] == 'completed'])
        successful = len([s for s in self.monitoring_data if s['result'] == 'success'])
        
        success_rate = (successful / completed * 100) if completed > 0 else 0
        
        return {
            'total_monitored': total_monitored,
            'active_monitoring': active_monitoring,
            'completed': completed,
            'successful': successful,
            'success_rate': round(success_rate, 2)
        }

# Instância global
ai_result_monitor = AIResultMonitor()

