import requests
import time

BOT_TOKEN = "7360602779:AAFIpncv7fkXaEX5PdWdEAUBb7NQ9SeA-F0"
CHAT_ID = "@botsinaistop"

def send_signal_notification(content):
    """
    Envia notificação para o Telegram - versão simples que funcionava
    """
    try:
        if isinstance(content, dict):
            symbol = content["symbol"]
            entry_price = content["entry_price"]
            target_price = content["target_price"]
            stop_loss = content["stop_loss"]
            risk_reward = content["risk_reward"]
            confidence_score = content["confidence_score"]
            strategy = content["strategy"]
            created_at = content["created_at"]

            text = f"""📢 Novo sinal detectado para {symbol}
🎯 Entrada: {entry_price} | Alvo: {target_price} | Stop: {stop_loss}
📊 R:R: {risk_reward} | Confiança: {confidence_score}%
⏱️ Estratégia: {strategy}
📅 Criado em: {created_at}"""

        elif isinstance(content, str):
            text = content
        else:
            return False

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": text
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Notificação enviada para o canal com sucesso.")
            return True
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no envio: {e}")
        return False

