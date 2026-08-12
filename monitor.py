import os
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def testar_telegram():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": "🚀 TESTE DE CONEXÃO: Seu bot está funcionando e conectado ao Telegram!",
    }
    resposta = requests.post(url, json=payload)
    print("Status do Telegram:", resposta.status_code)
    print("Resposta do Telegram:", resposta.text)

if __name__ == "__main__":
    testar_telegram()
