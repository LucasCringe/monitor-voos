import os
import requests
import google.generativeai as genai

# 1. Configurar APIs com as chaves seguras do GitHub
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Configura o Gemini
genai.configure(api_key=GEMINI_KEY)

def buscar_voos():
    # PARAMETROS DA SUA VIAGEM (Altere se necessário):
    origem = "GRU"       # Código do aeroporto (ex: GRU para Guarulhos)
    destino = "MIA"      # Código do aeroporto (ex: MIA para Miami)
    data_ida = "2026-11-10"
    data_volta = "2026-11-20"

    url = f"https://serpapi.com/search.json?engine=google_flights&departure_id={origem}&arrival_id={destino}&outbound_date={data_ida}&return_date={data_volta}&currency=BRL&hl=pt&api_key={SERPAPI_KEY}"
    
    resposta = requests.get(url)
    return resposta.json()

def analisar_com_gemini(dados_voos):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Você é um assistente especialista em passagens aéreas.
    Analise os seguintes dados brutos de voos retornados pela busca:
    {str(dados_voos)[:3000]}

    Instruções:
    1. Extraia os 3 voos mais baratos.
    2. Para cada voo informe: Companhia aérea, preço total em R$, se tem escalas e duração.
    3. Escreva uma mensagem muito curta, limpa e formatada para ser enviada pelo Telegram.
    4. Diga se o valor atual parece bom ou se vale a pena esperar.
    """
    
    response = model.generate_content(prompt)
    return response.text

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    try:
        dados = buscar_voos()
        relatorio = analisar_com_gemini(dados)
        enviar_telegram(relatorio)
        print("Monitoramento concluído e mensagem enviada com sucesso!")
    except Exception as e:
        print(f"Erro ao executar: {e}")
