import os
import requests
import google.generativeai as genai

# Configuração das chaves seguras do GitHub Actions
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Configura a biblioteca do Gemini
genai.configure(api_key=GEMINI_KEY)

def buscar_voos_destino(origem, destino, data_ida):
    """Busca passagens de ida para um destino específico na SerpApi."""
    url = f"https://serpapi.com/search.json?engine=google_flights&departure_id={origem}&arrival_id={destino}&outbound_date={data_ida}&type=2&currency=BRL&hl=pt&api_key={SERPAPI_KEY}"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        return resposta.json()
    return {}

def analisar_com_gemini(dados_nat, dados_jpa, data_ida):
    # Usa o modelo Gemini mais recente
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Você é um assistente de viagens especialista em encontrar passagens baratas para Pipa/RN.
    O usuário quer ir de São Paulo (SAO) para a praia de Pipa na data: {data_ida}.
    Os dois aeroportos mais próximos são Natal (NAT - 90km) e João Pessoa (JPA - 150km).

    Abaixo estão os dados brutos obtidos para ambos os aeroportos:

    --- DADOS NATAL (NAT) ---
    {str(dados_nat)[:3000]}

    --- DADOS JOÃO PESSOA (JPA) ---
    {str(dados_jpa)[:3000]}

    INSTRUÇÕES DE RESPOSTA:
    1. Crie uma mensagem curta, bonita e formatada para o Telegram.
    2. Apresente as 2 melhores/mais baratas opções de voo de IDA para NATAL (NAT).
    3. Apresente as 2 melhores/mais baratas opções de voo de IDA para JOÃO PESSOA (JPA).
    4. Para cada opção, indique: Companhia Aérea, Aeroporto de Origem (GRU/CGH/VCP), Horário, Escalas e Preço em R$.
    5. No final, dê um VEREDITO: Qual aeroporto está compensando mais em preço para chegar a Pipa nesta .
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
        # CONFIGURAÇÕES DA SUA VIAGEM:
        origem = "SAO"            # Busca voos de GRU, CGH e VCP
        data_ida = "2026-12-27"   # Altere para a data que deseja viajar (AAAA-MM-DD)

        print("Buscando voos para Natal (NAT)...")
        dados_nat = buscar_voos_destino(origem, "NAT", data_ida)

        print("Buscando voos para João Pessoa (JPA)...")
        dados_jpa = buscar_voos_destino(origem, "JPA", data_ida)

        print("Analisando e comparando com o Gemini...")
        relatorio = analisar_com_gemini(dados_nat, dados_jpa, data_ida)

        print("Enviando mensagem no Telegram...")
        enviar_telegram(relatorio)
        
        print("Monitoramento NAT + JPA concluído com sucesso!")
    except Exception as e:
        print(f"Erro ao executar o monitoramento: {e}")
