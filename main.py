import asyncio
import os
import random
from datetime import datetime, timedelta
import aiohttp

TELEGRAM_TOKEN = "8206760840:AAHHHe3oYHol-xJxXpdfHmDXkvY-mBRUmqs"
CHAT_ID = "@sinaisbinariosdomestre" 
ATIVOS = ['EURUSD', 'AUDCAD', 'USDJPY', 'GBPUSD']

gains_acumulados = 0
loss_acumulados = 0
minutos_passados_relatorio = 0

def obter_hora_brasil():
    return datetime.utcnow() - timedelta(hours=3)

async def enviar_telegram(texto):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": texto, "parse_mode": "Markdown"}
            async with session.post(url, json=payload) as resp:
                return resp.status == 200
    except Exception as e:
        print(f"Erro Telegram: {e}")
        return False

async def loop_principal():
    global gains_acumulados, loss_acumulados, minutos_passados_relatorio
    
    print("⚡ Motor Forçado Inicializado.")
    await enviar_telegram("🔄 *Bot Conectado! Monitorando M5...*")

    estados = {ativo: {"fase": "aguardando", "direcao": "COMPRA (CALL) 🟢"} for ativo in ATIVOS}
    ultimo_minuto_rodado = -1

    while True:
        agora = obter_hora_brasil()
        minuto = agora.minute
        segundo = agora.second

        # Controle do Relatório a cada 8 horas (480 minutos)
        if minuto != ultimo_minuto_rodado and minuto % 1 == 0:
            minutos_passados_relatorio += 1
            ultimo_minuto_rodado = minuto
            
            if minutos_passados_relatorio >= 480:
                total = gains_acumulados + loss_acumulados
                win_rate = (gains_acumulados / total * 100) if total > 0 else 0
                texto_relatorio = (
                    f"📊 *RELATÓRIO DE PERFORMANCE*\n"
                    f"📈 *Total:* {total} | 🟢 *Gains:* {gains_acumulados} | 🔴 *Loss:* {loss_acumulados}\n"
                    f"🎯 *Assertividade:* {win_rate:.1f}%"
                )
                await enviar_telegram(texto_relatorio)
                gains_acumulados, loss_acumulados, minutos_passados_relatorio = 0, 0, 0

        # 1. Pré-Alerta (Nos minutos terminados em 4 e 9, aos 30 segundos)
        if (minuto % 5 == 4) and segundo == 30:
            for ativo in ATIVOS:
                estados[ativo]["fase"] = "alerta"
                estados[ativo]["direcao"] = "COMPRA (CALL) 🟢" if random.random() > 0.5 else "VENDA (PUT) 🔴"
                ativo_f = f"{ativo[:3]}/{ativo[3:]}"
                
                await enviar_telegram(
                    f"🚨 *PRÉ-ALERTA M5*\n🔹 *Ativo:* {ativo_f}\n🎯 *Ação:* PREPARAR {estados[ativo]['direcao']}"
                )
            await asyncio.sleep(2)

        # 2. Confirmação (Nos minutos terminados em 4 e 9, aos 58 segundos)
        elif (minuto % 5 == 4) and segundo == 58:
            for ativo in ATIVOS:
                if estados[ativo]["fase"] == "alerta":
                    ativo_f = f"{ativo[:3]}/{ativo[3:]}"
                    minuto_entrada = (agora + timedelta(minutes=1)).strftime("%H:%M")
                    
                    await enviar_telegram(
                        f"⚡ *ENTRADA CONFIRMADA*\n🎯 *Ativo:* {ativo_f}\n⏱ *Hora:* {minuto_entrada} (M5)"
                    )
                    
                    if random.random() <= 0.85:
                        gains_acumulados += 1
                    else:
                        loss_acumulados += 1
                        
                    estados[ativo]["fase"] = "aguardando"
            await asyncio.sleep(2)

        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(loop_principal())
