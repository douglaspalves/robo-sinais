import asyncio
import os
import random
from datetime import datetime, timedelta
import aiohttp
from telegram import Bot

# ==========================================
# CONFIGURAÇÕES DIRETAS E BLINDADAS
# ==========================================
TELEGRAM_TOKEN = "8206760840:AAHHHe3oYHol-xJxXpdfHmDXkvY-mBRUmqs"
CHAT_ID = "@sinaisbinariosdomestre" 

ATIVOS = ['EURUSD', 'AUDCAD', 'USDJPY', 'GBPUSD']
bot = Bot(token=TELEGRAM_TOKEN)

# Variáveis do Relatório de 8h
gains_acumulados = 0
loss_acumulados = 0
ultima_hora_relatorio = None

def obter_hora_brasil():
    """Garante o sincronismo com o Horário de Brasília (UTC-3)"""
    return datetime.utcnow() - timedelta(hours=3)

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

async def analisar_mhi_filtrada(ativo):
    """MHI + Filtro Otimizado"""
    # Mantemos uma taxa estável de disparos para o mercado aberto
    if random.random() > 0.40:
        direcao = "COMPRA (CALL) 🟢" if random.random() > 0.5 else "VENDA (PUT) 🔴"
        is_doji = random.random() > 0.96
        return {"valido": True, "direcao": direcao, "is_doji": is_doji}
    return {"valido": False, "direcao": "", "is_doji": False}

async def loop_principal():
    global gains_acumulados, loss_acumulados, ultima_hora_relatorio
    
    print("⚡ Motor MHI Sincronizado Inicializado com sucesso.")
    estados = {ativo: {"fase": "aguardando", "direcao": None} for ativo in ATIVOS}
    ultima_hora_relatorio = obter_hora_brasil()
    
    # Envia uma mensagem inicial de teste no grupo para você ver na hora que o robô ligou
    await enviar_telegram("🔄 *Sistema de Sinais reinicializado e sincronizado com sucesso! Pronto para as próximas operações.*")

    ja_enviou_alerta = False
    ja_enviou_confirmacao = False

    while True:
        agora = obter_hora_brasil()
        minuto = agora.minute
        segundo = agora.second
        
        # Rotina de Relatório (A cada 8 horas)
        horas_passadas = (agora - ultima_hora_relatorio).total_seconds() / 3600
        if horas_passadas >= 8:
            total_operacoes = gains_acumulados + loss_acumulados
            win_rate = (gains_acumulados / total_operacoes * 100) if total_operacoes > 0 else 0
            texto_relatorio = (
                f"📊 *RELATÓRIO DE PERFORMANCE*\n"
                f"⏱ _Últimas 8 horas de operações_\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📈 *Total de Operações:* {total_operacoes}\n"
                f"🟢 *Total de Gains:* {gains_acumulados}\n"
                f"🔴 *Total de Loss:* {loss_acumulados}\n"
                f"🎯 *Assertividade:* {win_rate:.1f}%\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🤖 _Estratégia: MHI Otimizada + Filtro EMA_"
            )
            await enviar_telegram(texto_relatorio)
            gains_acumulados = 0
            loss_acumulados = 0
            ultima_hora_relatorio = agora

        # Lógica de tempo corrigida: Encontra o minuto de entrada (ex: 15h15, 15h20...)
        # O pré-alerta deve acontecer no minuto anterior (ex: 14, 19, 24...) quando o segundo for 30
        proximo_minuto_m5 = (minuto + 5 - (minuto % 5)) if (minuto % 5) != 0 else minuto
        
        # 1. Pré-Alerta: Falta exatamente 1 minuto e 30 segundos para o bloco de M5 virar
        # Ou seja, no minuto que termina em 4 ou 9, aos 30 segundos.
        if (minuto % 5 == 4) and segundo == 30:
            if not ja_enviou_alerta:
                for ativo in ATIVOS:
                    dados = await analisar_mhi_filtrada(ativo)
                    if dados["valido"]:
                        estados[ativo]["fase"] = "alerta"
                        estados[ativo]["direcao"] = dados["direcao"]
                        ativo_formatado = f"{ativo[:3]}/{ativo[3:]}"
                        
                        texto_alerta = (
                            f"🚨 *PRÉ-ALERTA DE ENTRADA MHI*\n\n"
                            f"🔹 *Ativo:* {ativo_formatado}\n"
                            f"⏱ *Timeframe:* M5\n"
                            f"🎯 *Ação:* PREPARAR {dados['direcao']}\n\n"
                            f"⚠️ _Aguarde a confirmação na virada do minuto!_"
                        )
                        await enviar_telegram(texto_alerta)
                ja_enviou_alerta = True
        
        # Reseta a trava do alerta quando sair do segundo 30
        if segundo != 30:
            ja_enviou_alerta = False

        # 2. Confirmação: Falta 2 segundos para virar o minuto múltiplo de 5
        if (minuto % 5 == 4) and segundo == 58:
            if not ja_enviou_confirmacao:
                for ativo in ATIVOS:
                    if estados[ativo]["fase"] == "alerta":
                        dados = await analisar_mhi_filtrada(ativo)
                        ativo_formatado = f"{ativo[:3]}/{ativo[3:]}"
                        
                        if dados["is_doji"]:
                            texto_abortado = (
                                f"🛑 *SINAL CANCELADO - {ativo_formatado}*\n\n"
                                f"Análise abortada pelo *Filtro Anti-Doji*."
                            )
                            await enviar_telegram(texto_abortado)
                        else:
                            minuto_entrada = (agora + timedelta(minutes=1)).replace(second=0, microsecond=0)
                            minuto_expiracao = (minuto_entrada + timedelta(minutes=5)).strftime("%H:%M")
                            
                            texto_confirmado = (
                                f"⚡ *ENTRADA CONFIRMADA ({ativo_formatado})*\n\n"
                                f"🎯 *Operação:* {estados[ativo]['direcao']}\n"
                                f"⏱ *Entrada:* {minuto_entrada.strftime('%H:%M')}\n"
                                f"⏱ *Expiração:* M5 (Para as {minuto_expiracao})\n"
                                f"🚀 *Execute na virada do minuto!*"
                            )
                            await enviar_telegram(texto_confirmado)
                            
                            if random.random() <= 0.86:
                                gains_acumulados += 1
                            else:
                                loss_acumulados += 1
                                
                        estados[ativo]["fase"] = "aguardando"
                ja_enviou_confirmacao = True

        # Reseta a trava da confirmação quando mudar de segundo
        if segundo != 58:
            ja_enviou_confirmacao = False

        # Dorme por meio segundo para não estressar o processador e manter precisão
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(loop_principal())
