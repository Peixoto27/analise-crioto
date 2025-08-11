import pickle
import numpy as np
import pandas as pd
import os
from typing import Dict, Tuple, Optional

class MLModelLoader:
    """
    Carrega e usa o modelo de ML treinado com 2 anos de dados históricos
    """
    
    def __init__(self, model_path="crypto_ml_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.is_loaded = False
        self.model_accuracy = 0.0
        
        # Tenta carregar o modelo
        self.load_model()
    
    def load_model(self):
        """Carrega o modelo treinado com 2 anos de dados"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                
                # Extrai componentes do modelo
                self.model = model_data.get('model')
                self.scaler = model_data.get('scaler')
                self.feature_columns = model_data.get('feature_columns', [
                    'rsi', 'macd', 'bb_upper', 'bb_lower', 'volume_ratio',
                    'price_change', 'volatility', 'momentum'
                ])
                self.model_accuracy = model_data.get('accuracy', 0.0)
                
                self.is_loaded = True
                print(f"[ML_MODEL] ✅ Modelo carregado com sucesso!")
                print(f"[ML_MODEL] 📊 Acurácia do modelo: {self.model_accuracy:.2%}")
                print(f"[ML_MODEL] 🔧 Features: {len(self.feature_columns)}")
                
            except Exception as e:
                print(f"[ML_MODEL] ❌ Erro ao carregar modelo: {e}")
                self.is_loaded = False
        else:
            print(f"[ML_MODEL] ⚠️ Arquivo do modelo não encontrado: {self.model_path}")
            print(f"[ML_MODEL] 📁 Para usar o modelo treinado, coloque o arquivo na pasta do projeto")
            self.is_loaded = False
    
    def prepare_features(self, market_data: pd.DataFrame) -> np.array:
        """
        Prepara features para o modelo baseado nos dados de mercado
        """
        if market_data.empty:
            return None
        
        latest = market_data.iloc[-1]
        
        # Calcula features baseadas no modelo original
        features = {}
        
        # RSI
        features['rsi'] = latest.get('rsi', 50)
        
        # MACD
        features['macd'] = latest.get('macd_diff', 0)
        
        # Bandas de Bollinger (se disponível)
        close_price = latest['close']
        sma_20 = market_data['close'].tail(20).mean()
        std_20 = market_data['close'].tail(20).std()
        
        features['bb_upper'] = sma_20 + (2 * std_20)
        features['bb_lower'] = sma_20 - (2 * std_20)
        
        # Posição nas Bandas de Bollinger
        bb_position = (close_price - features['bb_lower']) / (features['bb_upper'] - features['bb_lower'])
        features['bb_position'] = max(0, min(1, bb_position))
        
        # Volume ratio
        features['volume_ratio'] = latest['volume'] / latest.get('volume_sma_20', latest['volume'])
        
        # Price change (últimos 5 períodos)
        if len(market_data) >= 5:
            price_5_ago = market_data['close'].iloc[-5]
            features['price_change'] = (close_price - price_5_ago) / price_5_ago * 100
        else:
            features['price_change'] = 0
        
        # Volatilidade (últimos 20 períodos)
        if len(market_data) >= 20:
            returns = market_data['close'].pct_change().dropna()
            features['volatility'] = returns.tail(20).std() * 100
        else:
            features['volatility'] = 0
        
        # Momentum (últimos 10 períodos)
        if len(market_data) >= 10:
            price_10_ago = market_data['close'].iloc[-10]
            features['momentum'] = (close_price - price_10_ago) / price_10_ago * 100
        else:
            features['momentum'] = 0
        
        # Converte para array na ordem correta
        feature_array = []
        for col in self.feature_columns:
            feature_array.append(features.get(col, 0))
        
        return np.array(feature_array).reshape(1, -1)
    
    def predict_signal_quality(self, market_data: pd.DataFrame) -> Tuple[float, str, Dict]:
        """
        Prediz a qualidade do sinal usando o modelo treinado com 2 anos de dados
        
        Returns:
            Tuple[float, str, Dict]: (probabilidade, recomendacao, detalhes)
        """
        if not self.is_loaded:
            return 0.5, "FALLBACK", {"error": "Modelo não carregado"}
        
        try:
            # Prepara features
            features = self.prepare_features(market_data)
            if features is None:
                return 0.5, "FALLBACK", {"error": "Dados insuficientes"}
            
            # Normaliza features se há scaler
            if self.scaler is not None:
                features = self.scaler.transform(features)
            
            # Faz predição
            if hasattr(self.model, 'predict_proba'):
                # Modelo com probabilidades
                probabilities = self.model.predict_proba(features)[0]
                probability = probabilities[1] if len(probabilities) > 1 else probabilities[0]
            else:
                # Modelo simples
                prediction = self.model.predict(features)[0]
                probability = float(prediction)
            
            # Determina recomendação baseada na probabilidade
            if probability >= 0.8:
                recommendation = "STRONG_BUY"
            elif probability >= 0.65:
                recommendation = "BUY"
            elif probability >= 0.5:
                recommendation = "WEAK_BUY"
            else:
                recommendation = "SKIP"
            
            details = {
                "model_accuracy": self.model_accuracy,
                "features_used": len(self.feature_columns),
                "data_source": "2_years_historical"
            }
            
            return probability, recommendation, details
            
        except Exception as e:
            print(f"[ML_MODEL] ❌ Erro na predição: {e}")
            return 0.5, "FALLBACK", {"error": str(e)}
    
    def get_model_info(self) -> Dict:
        """Retorna informações sobre o modelo"""
        return {
            "is_loaded": self.is_loaded,
            "model_path": self.model_path,
            "accuracy": self.model_accuracy,
            "features": self.feature_columns,
            "model_type": type(self.model).__name__ if self.model else None
        }

# Instância global
ml_model = MLModelLoader()

