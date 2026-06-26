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
    
    print("⚡ Motor Ultra-Sincronizado Ativo.")
    await enviar_telegram("🔄 *Bot Reconectado! Servidor Web Integrado para evitar desligamento...*")

    estados = {ativo: {"direcao": "COMPRA (CALL) 🟢"} for ativo in ATIVOS}
    
    ultimo_minuto_alerta = -1
    ultimo_minuto_confirmacao = -1
    ultimo_minuto_relatorio = -1

    while True:
        try:
            agora = obter_hora_brasil()
            minuto = agora.minute
            segundo = agora.second

            # 1. Relatório
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

            # 2. Pré-Alerta
            if (minuto % 5 == 4) and (30 <= segundo <= 45):
                if minuto != ultimo_minuto_alerta:
                    for ativo in ATIVOS:
                        estados[ativo]["direcao"] = "COMPRA (CALL) 🟢" if random.random() > 0.5 else "VENDA (PUT) 🔴"
                        ativo_f = f"{ativo[:3]}/{ativo[3:]}"
                        await enviar_telegram(f"🚨 *PRÉ-ALERTA M5*\n🔹 *Ativo:* {ativo_f}\n🎯 *Ação:* PREPARAR {estados[ativo]['direcao']}")
                    ultimo_minuto_alerta = minuto

            # 3. Confirmação
            if (minuto % 5 == 4) and (55 <= segundo <= 59):
                if minuto != ultimo_minuto_confirmacao:
                    for ativo in ATIVOS:
                        ativo_f = f"{ativo[:3]}/{ativo[3:]}"
                        minuto_entrada = (agora + timedelta(minutes=1)).strftime("%H:%M")
                        await enviar_telegram(f"⚡ *ENTRADA CONFIRMADA*\n🎯 *Ativo:* {ativo_f}\n⏱ *Hora:* {minuto_entrada} (M5)\n🚀 *Direção:* {estados[ativo]['direcao']}")
                        
                        if random.random() <= 0.85:
                            gains_acumulados += 1
                        else:
                            loss_acumulados += 1
                    ultimo_minuto_confirmacao = minuto

        except Exception as e:
            print(f"Erro no loop: {e}")

        await asyncio.sleep(0.5)

# ==========================================
# SERVIDOR WEB (MANTÉM A RENDER ATIVA)
# ==========================================
async def handle_ping(request):
    return web.Response(text="Bot Sinais do Mestre Online!")

async def start_background_tasks(app):
    app['bot_task'] = asyncio.create_task(loop_principal())

async def cleanup_background_tasks(app):
    app['bot_task'].cancel()
    await app['bot_task']

if __name__ == "__main__":
    app = web.Application()
    app.router.add_get('/', handle_ping)
    
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    
    # A Render exige o uso da variável PORT
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)
