import os
import time
import requests
from textblob import TextBlob
from price_fetcher import fetch_all_data
from technical_indicators import calculate_indicators
from signal_generator_hybrid import generate_hybrid_signal
from notifier import send_signal_notification
from state_manager import load_open_trades, save_open_trades, check_and_notify_closed_trades
from ai_result_monitor import ai_result_monitor
from ml_model_loader import ml_model
from ai_predictor import ai_predictor
from ai_data_collector import ai_data_collector

# --- CONFIGURAÇÕES ---
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "TONUSDT",
    "INJUSDT", "RNDRUSDT", "ARBUSDT", "LTCUSDT", "MATICUSDT",
    "OPUSDT", "NEARUSDT", "APTUSDT", "PEPEUSDT", "SEIUSDT",
    "TRXUSDT", "DOGEUSDT", "SHIBUSDT", "FILUSDT", "SUIUSDT"
]

USAR_SENTIMENTO = True
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = "https://newsapi.org/v2/everything"

# Cache para evitar chamadas repetidas
_sentiment_cache = {}

# Mapeamento de símbolos para nomes legíveis
symbol_map = {
    "BTCUSDT": "Bitcoin", "ETHUSDT": "Ethereum", "BNBUSDT": "Binance Coin",
    "SOLUSDT": "Solana", "XRPUSDT": "XRP", "ADAUSDT": "Cardano",
    "AVAXUSDT": "Avalanche", "DOTUSDT": "Polkadot", "LINKUSDT": "Chainlink",
    "TONUSDT": "Toncoin", "INJUSDT": "Injective", "RNDRUSDT": "Render Token",
    "ARBUSDT": "Arbitrum", "LTCUSDT": "Litecoin", "MATICUSDT": "Polygon",
    "OPUSDT": "Optimism", "NEARUSDT": "Near Protocol", "APTUSDT": "Aptos",
    "PEPEUSDT": "Pepe", "SEIUSDT": "Sei Network", "TRXUSDT": "Tron",
    "DOGEUSDT": "Dogecoin", "SHIBUSDT": "Shiba Inu", "FILUSDT": "Filecoin",
    "SUIUSDT": "Sui"
}

def get_sentiment_score(symbol):
    """Obtém score de sentimento para um símbolo"""
    if symbol in _sentiment_cache:
        return _sentiment_cache[symbol]

    if not NEWS_API_KEY:
        _sentiment_cache[symbol] = 0
        return 0

    query = symbol_map.get(symbol, symbol)
    try:
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5,
            "apiKey": NEWS_API_KEY
        }
        resp = requests.get(NEWS_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("articles"):
            _sentiment_cache[symbol] = 0
            return 0

        sentiment_sum = 0
        for article in data["articles"]:
            text = (article.get("title") or "") + " " + (article.get("description") or "")
            analysis = TextBlob(text)
            sentiment_sum += analysis.sentiment.polarity

        score = sentiment_sum / len(data["articles"])
        _sentiment_cache[symbol] = score
        return score

    except Exception as e:
        print(f"⚠️ Erro ao buscar sentimento para {symbol}: {e}")
        _sentiment_cache[symbol] = 0
        return 0

def print_system_status():
    """Imprime status completo do sistema híbrido"""
    print("\n" + "="*60)
    print("🚀 SISTEMA HÍBRIDO ML + IA - STATUS COMPLETO")
    print("="*60)
    
    # Status do modelo ML (2 anos de dados)
    ml_info = ml_model.get_model_info()
    print(f"🤖 MODELO ML (2 ANOS DE DADOS):")
    if ml_info['is_loaded']:
        print(f"   ✅ Status: ATIVO")
        print(f"   📊 Acurácia: {ml_info['accuracy']:.2%}")
        print(f"   🔧 Tipo: {ml_info['model_type']}")
        print(f"   📁 Features: {len(ml_info['features'])}")
    else:
        print(f"   ❌ Status: INATIVO")
        print(f"   📁 Arquivo esperado: {ml_info['model_path']}")
    
    # Status da IA adaptativa
    data_stats = ai_data_collector.get_statistics()
    print(f"\n🧠 IA ADAPTATIVA:")
    print(f"   📈 Sinais coletados: {data_stats['total_signals']}")
    print(f"   ✅ Com resultado: {data_stats['completed_signals']}")
    print(f"   🎯 Taxa de sucesso: {data_stats['success_rate']}%")
    
    if ai_predictor.is_trained:
        print(f"   🤖 Status: ATIVO (Acurácia: {ai_predictor.training_accuracy:.2%})")
    else:
        print(f"   🤖 Status: COLETANDO DADOS")
    
    # Status do monitoramento
    monitor_stats = ai_result_monitor.get_monitoring_statistics()
    print(f"\n👁️ MONITORAMENTO:")
    print(f"   📊 Total monitorado: {monitor_stats['total_monitored']}")
    print(f"   🔄 Ativo: {monitor_stats['active_monitoring']}")
    
    # Estratégia híbrida
    print(f"\n⚙️ ESTRATÉGIA HÍBRIDA:")
    if ml_info['is_loaded']:
        print(f"   🥇 Principal: Modelo ML (2 anos)")
        print(f"   🥈 Secundário: IA Adaptativa")
        print(f"   🔄 Fallback: Análise Técnica")
    else:
        print(f"   🥇 Principal: IA Adaptativa")
        print(f"   🔄 Fallback: Análise Técnica")
        print(f"   ⚠️ Para ativar ML: adicione arquivo crypto_ml_model.pkl")
    
    print("="*60)

def run_scanner():
    print("\n--- SCANNER HÍBRIDO ML + IA INICIADO ---")
    
    # Imprime status do sistema
    print_system_status()
    
    try:
        # Fase 0: Verificar resultados de sinais anteriores
        print("\n🔍 Fase 0: Verificando resultados de sinais anteriores...")
        ai_result_monitor.check_signal_results()
        
        # Fase 1: Monitoramento de trades abertos
        print("\n🔍 Fase 1: Monitorando trades abertos...")
        open_trades = load_open_trades()
        if open_trades:
            print(f"📊 Monitorando {len(open_trades)} trades abertos...")
            market_data_for_monitoring = fetch_all_data(list(open_trades.keys()))
            check_and_notify_closed_trades(open_trades, market_data_for_monitoring, send_signal_notification)
        else:
            print("📊 Nenhum trade aberto para monitorar.")
    except Exception as e:
        print(f"⚠️ Erro nas fases de monitoramento: {e}")
        open_trades = {}

    print("\n🔍 Fase 2: Buscando novos sinais com sistema híbrido...")
    all_symbols_to_fetch = list(set(SYMBOLS) - set(open_trades.keys()))
    if not all_symbols_to_fetch:
        print("⚪ Não há novas moedas para analisar, todos os trades estão abertos.")
        return

    print("🚚 Buscando dados brutos do mercado (OHLCV)...")
    try:
        market_data = fetch_all_data(all_symbols_to_fetch)
    except Exception as e:
        print(f"🚨 Erro ao buscar dados de mercado: {e}")
        return

    signals_found = 0
    signals_sent = 0

    for symbol, df in market_data.items():
        try:
            if df is None or df.empty:
                print(f"⚪ Sem dados para {symbol}, pulando...")
                continue

            print("-" * 40)
            print(f"🔬 Analisando {symbol} com sistema híbrido...")

            df_with_indicators = calculate_indicators(df)
            if df_with_indicators.empty:
                print(f"⚠️ Não foi possível calcular indicadores para {symbol}. Pulando...")
                continue
            print("✅ Indicadores calculados com sucesso.")

            # Análise de sentimento
            sentiment_score = 0.0
            if USAR_SENTIMENTO:
                sentiment_score = get_sentiment_score(symbol)
                print(f"🧠 Sentimento para {symbol}: {sentiment_score:.2f}")
                
                if sentiment_score < -0.3:
                    print(f"⚪ Sentimento muito negativo ({sentiment_score:.2f}) para {symbol}. Pulando...")
                    continue
            
            # Geração de sinal com sistema híbrido
            signal = generate_hybrid_signal(df_with_indicators, symbol, sentiment_score)
            
            if signal:
                signals_found += 1
                print(f"🔥 SINAL HÍBRIDO ENCONTRADO PARA {symbol}!")
                print(f"   🤖 ML: {signal.get('ml_probability', 'N/A')} | {signal.get('ml_recommendation', 'N/A')}")
                print(f"   🧠 IA: {signal.get('ai_probability', 'N/A')} | {signal.get('ai_recommendation', 'N/A')}")
                print(f"   ⚙️ Estratégia: {signal['strategy']}")
                
                try:
                    # Formatação da mensagem
                    signal_text = (
                        f"🚀 *SINAL HÍBRIDO ML + IA*\n\n"
                        f"📌 *Par:* {signal['symbol']}\n"
                        f"🎯 *Entrada:* `{signal['entry_price']}`\n"
                        f"🎯 *Alvo:* `{signal['target_price']}`\n"
                        f"🛑 *Stop Loss:* `{signal['stop_loss']}`\n\n"
                        f"📊 *Risco/Retorno:* `{signal['risk_reward']}`\n"
                        f"📈 *Confiança Técnica:* `{signal['confidence_score']}%`\n"
                        f"🤖 *ML (2 anos):* `{signal.get('ml_probability', 'N/A')}`\n"
                        f"🧠 *IA Adaptativa:* `{signal.get('ai_probability', 'N/A')}`\n"
                        f"🎯 *Confiança Híbrida:* `{signal.get('hybrid_confidence', 'N/A')}`\n\n"
                        f"⚙️ Estratégia: `{signal['strategy']}`\n"
                        f"📅 Criado em: `{signal['created_at']}`\n"
                        f"🆔 ID: `{signal['id']}`"
                    )
                    
                    if send_signal_notification(signal_text):
                        signals_sent += 1
                        
                        # Adiciona para monitoramento de resultado
                        ai_result_monitor.add_signal_for_monitoring(signal)
                        
                        # Salva trade aberto
                        open_trades[symbol] = {
                            'entry_price': float(signal['entry_price']),
                            'target_price': float(signal['target_price']),
                            'stop_loss': float(signal['stop_loss']),
                            'created_at': signal['created_at'],
                            'signal_id': signal['id']
                        }
                        save_open_trades(open_trades)
                        
                        print(f"✅ Sinal híbrido enviado e monitorado")
                    else:
                        print(f"⚠️ Falha ao enviar sinal para {symbol}")
                        
                except Exception as e:
                    print(f"🚨 Erro ao enviar notificação para {symbol}: {e}")
            else:
                print(f"⚪ Sem sinal para {symbol} após análise híbrida.")

        except Exception as e:
            print(f"🚨 Erro inesperado ao processar {symbol}: {e}")

    print(f"\n📊 Resumo do ciclo híbrido:")
    print(f"   🔍 Sinais encontrados: {signals_found}")
    print(f"   📤 Sinais enviados: {signals_sent}")
    print(f"   🤖 ML Status: {'ATIVO' if ml_model.is_loaded else 'AGUARDANDO ARQUIVO'}")
    print(f"   🧠 IA Status: {'ATIVO' if ai_predictor.is_trained else 'COLETANDO DADOS'}")

def main():
    """Função principal para execução contínua do scanner"""
    while True:
        try:
            run_scanner()
        except Exception as e:
            print(f"🚨 ERRO CRÍTICO NO LOOP PRINCIPAL: {e}")
        print("\n--- Ciclo concluído. Aguardando 15 minutos... ---")
        time.sleep(900)

if __name__ == "__main__":
    main()

