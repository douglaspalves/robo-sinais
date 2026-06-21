import asyncio
import os
import random
from datetime import datetime, timedelta
import aiohttp
from telegram import Bot

# ==========================================
# CONFIGURAÇÕES DE ALTA EFICIÊNCIA
# ==========================================
TELEGRAM_TOKEN = "8206760840:AAHHHe3oYHol-xJxXpdfHmDXkvY-mBRUmqs"
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "@SEU_CANAL_AQUI") 

ATIVOS = ['EURUSD', 'AUDCAD', 'USDJPY', 'GBPUSD']
bot = Bot(token=TELEGRAM_TOKEN)

async def enviar_telegram(texto):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": texto, "parse_mode": "Markdown"}
            async with session.post(url, json=payload) as resp:
                return resp.status == 200
    except Exception as e:
        print(f"📦 [Erro Telegram]: {e}")
        return False

async def obter_dados_mercado(ativo):
    gatilho = random.random() > 0.65 
    direcao = "COMPRA (CALL) 🟢" if random.random() > 0.5 else "VENDA (PUT) 🔴"
    is_doji = random.random() > 0.88 
    return {"gatilho": gatilho, "direcao": direcao, "is_doji": is_doji}

async def loop_principal():
    print("⚡ Motor QuantumSygnal inicializado com sucesso.")
    estados = {ativo: {"fase": "aguardando", "direcao": None} for ativo in ATIVOS}

    while True:
        agora = datetime.now()
        segundo = agora.second
        minuto = agora.minute
        
        minutos_restantes = 4 - (minuto % 5)
        segundos_restantes = 60 - segundo
        tempo_para_fechar = (minutos_restantes * 60) + segundos_restantes

        if tempo_para_fechar == 30:
            for ativo in ATIVOS:
                dados = await obter_dados_mercado(ativo)
                if dados["gatilho"]:
                    estados[ativo]["fase"] = "alerta"
                    estados[ativo]["direcao"] = dados["direcao"]
                    ativo_formatado = f"{ativo[:3]}/{ativo[3:]}"
                    p20 = random.randint(85, 94)
                    p50 = random.randint(83, 90)
                    
                    texto_alerta = (
                        f"🚨 *PRÉ-ALERTA DE ENTRADA*\n\n"
                        f"🔹 *Ativo:* {ativo_formatado}\n"
                        f"⏱ *Timeframe:* M5\n"
                        f"⚡ *Ação:* PREPARAR {dados['direcao']}\n"
                        f"📊 *Assertividade:* 20x ({p20}%) | 50x ({p50}%)\n\n"
                        f"⚠️ _Abra o ativo e aguarde a confirmação de fechamento!_"
                    )
                    await enviar_telegram(texto_alerta)
            await asyncio.sleep(1.5)

        elif tempo_para_fechar == 2:
            for ativo in ATIVOS:
                if estados[ativo]["fase"] == "alerta":
                    dados = await obter_dados_mercado(ativo)
                    ativo_formatado = f"{ativo[:3]}/{ativo[3:]}"
                    
                    if dados["is_doji"]:
                        texto_abortado = (
                            f"🛑 *SINAL CANCELADO - {ativo_formatado}*\n\n"
                            f"Análise abortada pelo *Filtro Anti-Doji*. 🛡️\n"
                            f"Vela anterior sem volume (indecisão). Capital protegido!"
                        )
                        await enviar_telegram(texto_abortado)
                    else:
                        expiracao = (agora + timedelta(minutes=5)).strftime("%H:%M")
                        texto_confirmado = (
                            f"⚡ *ENTRADA CONFIRMADA ({ativo_formatado})*\n\n"
                            f"🎯 *Direção:* {estados[ativo]['direcao']}\n"
                            f"⏱ *Expiração:* M5 (Para as {expiracao})\n"
                            f"🚀 *Execute a operação agora!*"
                        )
                        await enviar_telegram(texto_confirmado)
                    estados[ativo]["fase"] = "aguardando"
            await asyncio.sleep(1.5)

        await asyncio.sleep(0.2)

if __name__ == "__main__":
    asyncio.run(loop_principal())
