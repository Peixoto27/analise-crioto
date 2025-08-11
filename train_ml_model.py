#!/usr/bin/env python3
"""
Script para treinar modelo de Machine Learning para sinais de criptomoedas
Usa dados históricos do BTC para criar o arquivo crypto_ml_model.pkl
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import pickle
import warnings
warnings.filterwarnings('ignore')

def calculate_technical_indicators(df):
    """Calcula indicadores técnicos"""
    # RSI
    def calculate_rsi(prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    # MACD
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        macd_histogram = macd - macd_signal
        return macd, macd_signal, macd_histogram
    
    # Médias móveis
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df['ema_12'] = df['close'].ewm(span=12).mean()
    df['ema_26'] = df['close'].ewm(span=26).mean()
    
    # RSI
    df['rsi'] = calculate_rsi(df['close'])
    
    # MACD
    df['macd'], df['macd_signal'], df['macd_histogram'] = calculate_macd(df['close'])
    
    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
    
    # Volume indicators
    df['volume_sma'] = df['volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_sma']
    
    # Price change indicators
    df['price_change_1h'] = df['close'].pct_change(1)
    df['price_change_4h'] = df['close'].pct_change(4)
    df['price_change_24h'] = df['close'].pct_change(24)
    
    # Volatility
    df['volatility'] = df['close'].rolling(window=24).std()
    
    # High-Low ratio
    df['hl_ratio'] = (df['high'] - df['low']) / df['close']
    
    return df

def create_target_variable(df, future_hours=4, profit_threshold=0.02):
    """Cria variável target baseada em movimentos futuros de preço"""
    # Calcula o preço máximo nas próximas 'future_hours' horas
    df['future_max'] = df['high'].rolling(window=future_hours, min_periods=1).max().shift(-future_hours)
    
    # Calcula o retorno potencial
    df['future_return'] = (df['future_max'] - df['close']) / df['close']
    
    # Cria target: 1 se o retorno for >= profit_threshold, 0 caso contrário
    df['target'] = (df['future_return'] >= profit_threshold).astype(int)
    
    return df

def prepare_features(df):
    """Prepara features para o modelo"""
    feature_columns = [
        'rsi', 'macd', 'macd_signal', 'macd_histogram',
        'sma_20', 'sma_50', 'ema_12', 'ema_26',
        'bb_position', 'volume_ratio', 'volatility', 'hl_ratio',
        'price_change_1h', 'price_change_4h', 'price_change_24h'
    ]
    
    # Adiciona features de preço normalizado
    df['close_norm'] = df['close'] / df['sma_50']
    df['volume_norm'] = df['volume'] / df['volume_sma']
    
    feature_columns.extend(['close_norm', 'volume_norm'])
    
    return df[feature_columns], df['target']

def train_model():
    """Função principal para treinar o modelo"""
    print("🚀 Iniciando treinamento do modelo ML...")
    
    # Carregar dados
    print("📊 Carregando dados históricos...")
    df = pd.read_csv('historical_data_BTC_USDT_1h.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    print(f"   📈 Dados carregados: {len(df)} registros")
    print(f"   📅 Período: {df['timestamp'].min()} até {df['timestamp'].max()}")
    
    # Calcular indicadores técnicos
    print("🔧 Calculando indicadores técnicos...")
    df = calculate_technical_indicators(df)
    
    # Criar variável target
    print("🎯 Criando variável target...")
    df = create_target_variable(df, future_hours=4, profit_threshold=0.02)
    
    # Preparar features
    print("⚙️ Preparando features...")
    X, y = prepare_features(df)
    
    # Remover NaN
    mask = ~(X.isnull().any(axis=1) | y.isnull())
    X = X[mask]
    y = y[mask]
    
    print(f"   ✅ Features preparadas: {X.shape[0]} amostras, {X.shape[1]} features")
    print(f"   📊 Distribuição target: {y.value_counts().to_dict()}")
    
    # Dividir dados
    print("🔀 Dividindo dados em treino e teste...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Normalizar features
    print("📏 Normalizando features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Treinar modelo
    print("🤖 Treinando modelo Random Forest...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Avaliar modelo
    print("📊 Avaliando modelo...")
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"   🎯 Acurácia: {accuracy:.4f}")
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
    print(f"   📈 CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n🔍 Top 10 Features mais importantes:")
    for idx, row in feature_importance.head(10).iterrows():
        print(f"   {row['feature']}: {row['importance']:.4f}")
    
    # Salvar modelo e scaler
    print("\n💾 Salvando modelo...")
    model_data = {
        'model': model,
        'scaler': scaler,
        'feature_columns': list(X.columns),
        'accuracy': accuracy,
        'cv_score': cv_scores.mean(),
        'feature_importance': feature_importance.to_dict('records')
    }
    
    with open('crypto_ml_model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    print("✅ Modelo salvo como 'crypto_ml_model.pkl'")
    
    # Relatório final
    print(f"\n🎉 Treinamento concluído!")
    print(f"   📊 Acurácia final: {accuracy:.4f}")
    print(f"   🔄 Cross-validation: {cv_scores.mean():.4f}")
    print(f"   📁 Arquivo: crypto_ml_model.pkl")
    
    return model_data

if __name__ == "__main__":
    try:
        model_data = train_model()
        print("\n🚀 Modelo pronto para uso no sistema híbrido!")
    except Exception as e:
        print(f"❌ Erro durante o treinamento: {e}")
        import traceback
        traceback.print_exc()

