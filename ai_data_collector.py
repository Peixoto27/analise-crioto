import json
import os
import datetime
import pandas as pd
from typing import Dict, List, Optional

class AIDataCollector:
    """
    Coleta e armazena dados para treinamento do modelo de IA
    """
    
    def __init__(self, data_file="ai_training_data.json"):
        self.data_file = data_file
        self.data = self.load_data()
    
    def load_data(self) -> List[Dict]:
        """Carrega dados existentes ou cria arquivo novo"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_data(self):
        """Salva dados no arquivo"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_signal_data(self, signal: Dict, market_features: Dict, sentiment_score: float = 0.0):
        """
        Adiciona dados de um novo sinal para treinamento futuro
        
        Args:
            signal: Dicionário com dados do sinal
            market_features: Features técnicas no momento do sinal
            sentiment_score: Score de sentimento
        """
        
        # Extrai features relevantes
        features = {
            'symbol': signal['symbol'],
            'entry_price': float(signal['entry_price']),
            'target_price': float(signal['target_price']),
            'stop_loss': float(signal['stop_loss']),
            'confidence_score': float(signal['confidence_score']),
            'created_at': signal['created_at'],
            'signal_id': signal['id'],
            
            # Features técnicas
            'rsi': market_features.get('rsi', 0),
            'macd_diff': market_features.get('macd_diff', 0),
            'sma_ratio': market_features.get('sma_ratio', 1),  # close/sma_50
            'volume_ratio': market_features.get('volume_ratio', 1),  # volume/volume_sma_20
            'volatility': market_features.get('volatility', 0),
            'momentum': market_features.get('momentum', 0),
            
            # Features de contexto
            'sentiment_score': sentiment_score,
            'hour_of_day': datetime.datetime.now().hour,
            'day_of_week': datetime.datetime.now().weekday(),
            
            # Resultado (será preenchido depois)
            'result': None,  # 'success', 'failure', 'pending'
            'result_updated_at': None,
            'days_to_result': None
        }
        
        self.data.append(features)
        self.save_data()
        print(f"[AI_DATA] Dados do sinal {signal['symbol']} adicionados para treinamento")
    
    def update_signal_result(self, signal_id: str, result: str, days_to_result: int):
        """
        Atualiza o resultado de um sinal
        
        Args:
            signal_id: ID do sinal
            result: 'success' ou 'failure'
            days_to_result: Quantos dias levou para ter resultado
        """
        for item in self.data:
            if item['signal_id'] == signal_id:
                item['result'] = result
                item['result_updated_at'] = datetime.datetime.now().isoformat()
                item['days_to_result'] = days_to_result
                self.save_data()
                print(f"[AI_DATA] Resultado do sinal {signal_id} atualizado: {result}")
                return True
        return False
    
    def get_training_data(self) -> pd.DataFrame:
        """
        Retorna dados prontos para treinamento (apenas sinais com resultado)
        """
        # Filtra apenas sinais com resultado definido
        completed_signals = [item for item in self.data if item['result'] is not None]
        
        if not completed_signals:
            return pd.DataFrame()
        
        df = pd.DataFrame(completed_signals)
        
        # Converte resultado para binário
        df['target'] = (df['result'] == 'success').astype(int)
        
        # Remove colunas não necessárias para treinamento
        feature_columns = [
            'rsi', 'macd_diff', 'sma_ratio', 'volume_ratio', 
            'volatility', 'momentum', 'sentiment_score',
            'hour_of_day', 'day_of_week', 'confidence_score'
        ]
        
        return df[feature_columns + ['target']]
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas dos dados coletados"""
        total_signals = len(self.data)
        completed_signals = len([item for item in self.data if item['result'] is not None])
        successful_signals = len([item for item in self.data if item['result'] == 'success'])
        
        success_rate = (successful_signals / completed_signals * 100) if completed_signals > 0 else 0
        
        return {
            'total_signals': total_signals,
            'completed_signals': completed_signals,
            'pending_signals': total_signals - completed_signals,
            'successful_signals': successful_signals,
            'success_rate': round(success_rate, 2)
        }

# Instância global
ai_data_collector = AIDataCollector()

