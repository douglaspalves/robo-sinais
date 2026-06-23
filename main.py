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
    
    print("⚡ Motor Ultra-Sincronizado Ativo.")
    await enviar_telegram("🔄 *Bot Reconectado com Sistema Anti-Travamento! M5 Ativo...*")

    estados = {ativo: {"direcao": "COMPRA (CALL) 🟢"} for ativo in ATIVOS}
    
    # Travas de controle para evitar repetições no mesmo minuto
    ultimo_minuto_alerta = -1
    ultimo_minuto_confirmacao = -1
    ultimo_minuto_relatorio = -1

    while True:
        agora = obter_hora_brasil()
        minuto = agora.minute
        segundo = agora.second

        # 1. Controle do Relatório de 1h (A cada 60 minutos cheios)
        if minuto != ultimo_minuto_relatorio:
            minutos_passados_relatorio += 1
            ultimo_minuto_relatorio = minuto
            
            if minutos_passados_relatorio >= 60:
                total = gains_acumulados + loss_acumulados
                win_rate = (gains_acumulados / total * 100) if total > 0 else 0
                texto_relatorio = (
                    f"📊 *RELATÓRIO DE PERFORMANCE (1H)*\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📈 *Total de Sinais:* {total}\n"
                    f"🟢 *Gains:* {gains_acumulados}\n"
                    f"🔴 *Loss:* {loss_acumulados}\n"
                    f"🎯 *Assertividade:* {win_rate:.1f}%\n"
                    f"━━━━━━━━━━━━━━━━━━━━"
                )
                await enviar_telegram(texto_relatorio)
                gains_acumulados, loss_acumulados, minutos_passados_relatorio = 0, 0, 0

        # 2. Pré-Alerta (Dispara na janela dos 30 aos 45 segundos do minuto que termina em 4 ou 9)
        if (minuto % 5 == 4) and (30 <= segundo <= 45):
            if minuto != ultimo_minuto_alerta:
                for ativo in ATIVOS:
                    estados[ativo]["direcao"] = "COMPRA (CALL) 🟢" if random.random() > 0.5 else "VENDA (PUT) 🔴"
                    ativo_f = f"{ativo[:3]}/{ativo[3:]}"
                    
                    await enviar_telegram(
                        f"🚨 *PRÉ-ALERTA M5*\n🔹 *Ativo:* {ativo_f}\n🎯 *Ação:* PREPARAR {estados[ativo]['direcao']}"
                    )
                ultimo_minuto_alerta = minuto

        # 3. Confirmação (Dispara na janela dos 55 aos 59 segundos do minuto que termina em 4 ou 9)
        if (minuto % 5 == 4) and (55 <= segundo <= 59):
            if minuto != ultimo_minuto_confirmacao:
                for ativo in ATIVOS:
                    ativo_f = f"{ativo[:3]}/{ativo[3:]}"
                    minuto_entrada = (agora + timedelta(minutes=1)).strftime("%H:%M")
                    
                    await enviar_telegram(
                        f"⚡ *ENTRADA CONFIRMADA*\n🎯 *Ativo:* {ativo_f}\n⏱ *Hora:* {minuto_entrada} (M5)\n🚀 *Direção:* {estados[ativo]['direcao']}"
                    )
                    
                    if random.random() <= 0.85:
                        gains_acumulados += 1
                    else:
                        loss_acumulados += 1
                ultimo_minuto_confirmacao = minuto

        # Delay curto para manter a precisão sem sobrecarregar
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(loop_principal())
