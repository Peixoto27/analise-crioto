import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime
from typing import Dict, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from ai_data_collector import ai_data_collector

class AIPredictor:
    """
    Modelo de IA para prever a qualidade dos sinais de trading
    """
    
    def __init__(self, model_file="ai_model.pkl"):
        self.model_file = model_file
        self.model = None
        self.feature_columns = [
            'rsi', 'macd_diff', 'sma_ratio', 'volume_ratio', 
            'volatility', 'momentum', 'sentiment_score',
            'hour_of_day', 'day_of_week', 'confidence_score'
        ]
        self.is_trained = False
        self.last_training_date = None
        self.training_accuracy = 0.0
        
        # Tenta carregar modelo existente
        self.load_model()
    
    def prepare_features(self, market_data: Dict, signal_data: Dict, sentiment_score: float = 0.0) -> np.array:
        """
        Prepara features para predição
        """
        latest = market_data.iloc[-1] if isinstance(market_data, pd.DataFrame) else market_data
        
        features = [
            latest.get('rsi', 50),
            latest.get('macd_diff', 0),
            latest['close'] / latest.get('sma_50', latest['close']),  # sma_ratio
            latest['volume'] / latest.get('volume_sma_20', latest['volume']),  # volume_ratio
            self.calculate_volatility(market_data),
            self.calculate_momentum(market_data),
            sentiment_score,
            datetime.now().hour,
            datetime.now().weekday(),
            float(signal_data.get('confidence_score', 70))
        ]
        
        return np.array(features).reshape(1, -1)
    
    def calculate_volatility(self, market_data) -> float:
        """Calcula volatilidade recente"""
        if isinstance(market_data, pd.DataFrame) and len(market_data) >= 20:
            returns = market_data['close'].pct_change().dropna()
            return returns.tail(20).std() * 100
        return 0.0
    
    def calculate_momentum(self, market_data) -> float:
        """Calcula momentum recente"""
        if isinstance(market_data, pd.DataFrame) and len(market_data) >= 10:
            recent_close = market_data['close'].iloc[-1]
            old_close = market_data['close'].iloc[-10]
            return (recent_close - old_close) / old_close * 100
        return 0.0
    
    def train_model(self, min_samples: int = 50) -> bool:
        """
        Treina o modelo com dados disponíveis
        """
        print("[AI_PREDICTOR] Iniciando treinamento do modelo...")
        
        # Obtém dados de treinamento
        training_data = ai_data_collector.get_training_data()
        
        if len(training_data) < min_samples:
            print(f"[AI_PREDICTOR] Dados insuficientes para treinamento. Necessário: {min_samples}, Disponível: {len(training_data)}")
            return False
        
        # Separa features e target
        X = training_data[self.feature_columns]
        y = training_data['target']
        
        # Divide em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Treina modelo
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        # Avalia modelo
        y_pred = self.model.predict(X_test)
        self.training_accuracy = accuracy_score(y_test, y_pred)
        
        print(f"[AI_PREDICTOR] Modelo treinado com sucesso!")
        print(f"[AI_PREDICTOR] Acurácia: {self.training_accuracy:.2%}")
        print(f"[AI_PREDICTOR] Amostras de treinamento: {len(training_data)}")
        
        # Salva modelo
        self.save_model()
        self.is_trained = True
        self.last_training_date = datetime.now()
        
        return True
    
    def predict_signal_quality(self, market_data: Dict, signal_data: Dict, sentiment_score: float = 0.0) -> Tuple[float, str]:
        """
        Prediz a qualidade de um sinal
        
        Returns:
            Tuple[float, str]: (probabilidade_sucesso, recomendacao)
        """
        if not self.is_trained or self.model is None:
            # Se não há modelo treinado, usa heurística simples
            confidence = float(signal_data.get('confidence_score', 70))
            probability = confidence / 100.0
            recommendation = "SEND" if probability > 0.7 else "SKIP"
            return probability, recommendation
        
        # Prepara features
        features = self.prepare_features(market_data, signal_data, sentiment_score)
        
        # Faz predição
        probability = self.model.predict_proba(features)[0][1]  # Probabilidade da classe positiva
        
        # Determina recomendação
        if probability >= 0.75:
            recommendation = "SEND"
        elif probability >= 0.6:
            recommendation = "SEND_WITH_CAUTION"
        else:
            recommendation = "SKIP"
        
        return probability, recommendation
    
    def get_feature_importance(self) -> Dict:
        """Retorna importância das features"""
        if not self.is_trained or self.model is None:
            return {}
        
        importance = self.model.feature_importances_
        return dict(zip(self.feature_columns, importance))
    
    def save_model(self):
        """Salva modelo treinado"""
        if self.model is not None:
            model_data = {
                'model': self.model,
                'feature_columns': self.feature_columns,
                'training_accuracy': self.training_accuracy,
                'last_training_date': self.last_training_date,
                'is_trained': self.is_trained
            }
            with open(self.model_file, 'wb') as f:
                pickle.dump(model_data, f)
            print(f"[AI_PREDICTOR] Modelo salvo em {self.model_file}")
    
    def load_model(self):
        """Carrega modelo salvo"""
        if os.path.exists(self.model_file):
            try:
                with open(self.model_file, 'rb') as f:
                    model_data = pickle.load(f)
                
                self.model = model_data['model']
                self.feature_columns = model_data['feature_columns']
                self.training_accuracy = model_data.get('training_accuracy', 0.0)
                self.last_training_date = model_data.get('last_training_date')
                self.is_trained = model_data.get('is_trained', False)
                
                print(f"[AI_PREDICTOR] Modelo carregado com sucesso. Acurácia: {self.training_accuracy:.2%}")
            except Exception as e:
                print(f"[AI_PREDICTOR] Erro ao carregar modelo: {e}")
    
    def should_retrain(self, new_signals_threshold: int = 20) -> bool:
        """Verifica se deve retreinar o modelo"""
        stats = ai_data_collector.get_statistics()
        
        # Retreina se há muitos sinais novos sem retreinamento
        if stats['completed_signals'] >= new_signals_threshold:
            return True
        
        # Retreina se nunca foi treinado e há dados suficientes
        if not self.is_trained and stats['completed_signals'] >= 50:
            return True
        
        return False

# Instância global
ai_predictor = AIPredictor()

