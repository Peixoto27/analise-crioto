import pandas as pd
import datetime
import uuid
from ml_model_loader import ml_model
from ai_predictor import ai_predictor
from ai_data_collector import ai_data_collector

PONTUACAO_MINIMA_PARA_SINAL = 70

PESO_SMA = 35
PESO_VOLUME = 30
PESO_MACD = 25
PESO_RSI = 10

def generate_hybrid_signal(df_with_indicators, symbol, sentiment_score=0.0):
    """
    Gera sinal usando sistema híbrido:
    1. Análise técnica tradicional
    2. Modelo ML treinado com 2 anos de dados (PRINCIPAL)
    3. Sistema de IA adaptativo (SECUNDÁRIO)
    """
    if df_with_indicators.empty:
        return None

    latest = df_with_indicators.iloc[-1]
    
    # ETAPA 1: Análise técnica tradicional (filtro inicial)
    confidence_score = 0
    
    if latest["close"] > latest["sma_50"]:
        confidence_score += PESO_SMA
        
    if latest["volume"] > latest["volume_sma_20"]:
        confidence_score += PESO_VOLUME
        
    if latest["macd_diff"] > 0:
        confidence_score += PESO_MACD
        
    if latest["rsi"] < 70:
        confidence_score += PESO_RSI

    # Verifica se passa no filtro técnico básico
    if confidence_score < PONTUACAO_MINIMA_PARA_SINAL:
        return None
    
    # ETAPA 2: Modelo ML com 2 anos de dados (PRINCIPAL)
    ml_probability, ml_recommendation, ml_details = ml_model.predict_signal_quality(df_with_indicators)
    
    # ETAPA 3: Sistema de IA adaptativo (SECUNDÁRIO)
    signal_dict = {
        "id": str(uuid.uuid4()),
        "signal_type": "BUY",
        "symbol": symbol,
        "entry_price": f"{latest['close']:.4f}",
        "target_price": f"{latest['close'] * 1.04:.4f}",
        "stop_loss": f"{latest['close'] * 0.98:.4f}",
        "risk_reward": "1:2.0",
        "confidence_score": f"{confidence_score}",
        "strategy": "Hybrid ML + IA",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    ai_probability, ai_recommendation = ai_predictor.predict_signal_quality(
        df_with_indicators, signal_dict, sentiment_score
    )
    
    # ETAPA 4: Decisão híbrida
    print(f"[HYBRID] {symbol} - Análise completa:")
    print(f"   📊 Técnico: {confidence_score}%")
    print(f"   🤖 ML (2 anos): {ml_probability:.2%} | {ml_recommendation}")
    print(f"   🧠 IA Adaptativa: {ai_probability:.2%} | {ai_recommendation}")
    
    # Lógica de decisão híbrida
    final_decision = "SKIP"
    strategy_used = "Hybrid ML + IA"
    
    if ml_model.is_loaded:
        # Se modelo ML está carregado, ele tem prioridade
        if ml_recommendation in ["STRONG_BUY", "BUY"]:
            if ai_recommendation != "SKIP":
                final_decision = "SEND"
                strategy_used = f"ML Primary ({ml_recommendation}) + IA ({ai_recommendation})"
            elif ml_recommendation == "STRONG_BUY":
                # ML muito confiante, envia mesmo se IA diz skip
                final_decision = "SEND"
                strategy_used = f"ML Override ({ml_recommendation})"
        elif ml_recommendation == "WEAK_BUY":
            # ML incerto, deixa IA decidir
            if ai_recommendation in ["SEND", "SEND_WITH_CAUTION"]:
                final_decision = "SEND"
                strategy_used = f"IA Decision ({ai_recommendation})"
    else:
        # Fallback para IA se ML não está disponível
        if ai_recommendation in ["SEND", "SEND_WITH_CAUTION"]:
            final_decision = "SEND"
            strategy_used = f"IA Fallback ({ai_recommendation})"
    
    if final_decision == "SKIP":
        print(f"[HYBRID] ❌ Sinal de {symbol} rejeitado pelo sistema híbrido")
        return None
    
    # Atualiza informações do sinal
    signal_dict.update({
        "ml_probability": f"{ml_probability:.2%}",
        "ml_recommendation": ml_recommendation,
        "ai_probability": f"{ai_probability:.2%}",
        "ai_recommendation": ai_recommendation,
        "strategy": strategy_used,
        "hybrid_confidence": f"{(ml_probability + ai_probability) / 2:.2%}"
    })
    
    # Coleta dados para treinamento futuro da IA
    market_features = {
        'rsi': latest.get('rsi', 50),
        'macd_diff': latest.get('macd_diff', 0),
        'sma_50': latest.get('sma_50', latest['close']),
        'volume_sma_20': latest.get('volume_sma_20', latest['volume']),
        'close': latest['close'],
        'volume': latest['volume']
    }
    
    ai_data_collector.add_signal_data(signal_dict, market_features, sentiment_score)
    
    print(f"[HYBRID] ✅ Sinal aprovado para {symbol} - Estratégia: {strategy_used}")
    
    return signal_dict

# Função de compatibilidade
def generate_signal(df_with_indicators, symbol):
    """Função de compatibilidade - usa sistema híbrido"""
    return generate_hybrid_signal(df_with_indicators, symbol, sentiment_score=0.0)

