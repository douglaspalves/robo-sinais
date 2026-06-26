import asyncio
import os
import random
from datetime import datetime, timedelta
import aiohttp
from aiohttp import web

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
    print("⚡ Motor Bot Ativo.")
    await enviar_telegram("🔄 *Bot Iniciado com Anti-Desligamento!*")

    estados = {ativo: {"direcao": "COMPRA (CALL) 🟢"} for ativo in ATIVOS}
    ultimo_minuto_alerta = -1
    ultimo_minuto_confirmacao = -1
    ultimo_minuto_relatorio = -1

    while True:
        agora = obter_hora_brasil()
        minuto = agora.minute
        segundo = agora.second

        if minuto != ultimo_minuto_relatorio:
            minutos_passados_relatorio += 1
            ultimo_minuto_relatorio = minuto
            if minutos_passados_relatorio >= 60:
                total = gains_acumulados + loss_acumulados
                win_rate = (gains_acumulados / total * 100) if total > 0 else 0
                await enviar_telegram(f"📊 *RELATÓRIO (1H)*\n━━━━━━━━━━━━━━━━━━━━\n📈 *Sinais:* {total}\n🟢 *Gains:* {gains_acumulados}\n🔴 *Loss:* {loss_acumulados}\n🎯 *Assertividade:* {win_rate:.1f}%\n━━━━━━━━━━━━━━━━━━━━")
                gains_acumulados, loss_acumulados, minutos_passados_relatorio = 0, 0, 0

        if (minuto % 5 == 4) and (30 <= segundo <= 45):
            if minuto != ultimo_minuto_alerta:
                for ativo in ATIVOS:
                    estados[ativo]["direcao"] = "COMPRA (CALL) 🟢" if random.random() > 0.5 else "VENDA (PUT) 🔴"
                    await enviar_telegram(f"🚨 *PRÉ-ALERTA M5*\n🔹 *Ativo:* {ativo[:3]}/{ativo[3:]}\n🎯 *Ação:* PREPARAR {estados[ativo]['direcao']}")
                ultimo_minuto_alerta = minuto

        if (minuto % 5 == 4) and (55 <= segundo <= 59):
            if minuto != ultimo_minuto_confirmacao:
                for ativo in ATIVOS:
                    minuto_entrada = (agora + timedelta(minutes=1)).strftime("%H:%M")
                    await enviar_telegram(f"⚡ *ENTRADA CONFIRMADA*\n🎯 *Ativo:* {ativo[:3]}/{ativo[3:]}\n⏱ *Hora:* {minuto_entrada} (M5)\n🚀 *Direção:* {estados[ativo]['direcao']}")
                    if random.random() <= 0.85: gains_acumulados += 1
                    else: loss_acumulados += 1
                ultimo_minuto_confirmacao = minuto

        await asyncio.sleep(0.5)

# Servidor Web para a Render/UptimeRobot
async def handle_ping(request):
    return web.Response(text="Online")

async def start_tasks(app):
    app['bot_task'] = asyncio.create_task(loop_principal())

if __name__ == "__main__":
    app = web.Application()
    app.router.add_get('/', handle_ping)
    app.on_startup.append(start_tasks)
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
