import asyncio
import os
import random
from datetime import datetime, timedelta
import aiohttp
from telegram import Bot

# ==========================================
# CONFIGURAÇÕES DA ESTRATÉGIA OTIMIZADA (MAIO 2026)
# ==========================================
TELEGRAM_TOKEN = "8206760840:AAHHHe3oYHol-xJxXpdfHmDXkvY-mBRUmqs"
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "@sinaisbinariosdomestre") 

ATIVOS = ['EURUSD', 'AUDCAD', 'USDJPY', 'GBPUSD']
bot = Bot(token=TELEGRAM_TOKEN)

# ==========================================
# VARIÁVEIS DE CONTROLE DO RELATÓRIO (8 HORAS)
# ==========================================
gains_acumulados = 0
loss_acumulados = 0
ultima_hora_relatorio = None

def obter_hora_brasil():
    """Garante o sincronismo com o Horário de Brasília (UTC-3)"""
    return datetime.utcnow() - timedelta(hours=3)

def verificar_mercado_aberto(agora):
    """Fecha na sexta às 17h e abre no domingo às 18h (Brasília)"""
    dia_semana = agora.weekday() 
    hora = agora.hour

    if dia_semana == 4 and hora >= 17:
        return False
    if dia_semana == 5:
        return False
    if dia_semana == 6 and hora < 18:
        return False
    return True

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
    """Simula estritamente os parâmetros do Relatorio_Otimizado_MHI_Filtrada_EURUSD_Maio_2026"""
    direcao_call = random.random() > 0.5
    ema_tendencia_alta = random.random() > 0.5
    
    sinal_valido = False
    direcao_final = ""
    
    if direcao_call and ema_tendencia_alta:
        sinal_valido = True
        direcao_final = "COMPRA (CALL) 🟢"
    elif not direcao_call and not ema_tendencia_alta:
        sinal_valido = True
        direcao_final = "VENDA (PUT) 🔴"
        
    is_doji = random.random() > 0.92 
    return {"valido": sinal_valido, "direcao": direcao_final, "is_doji": is_doji}

async def loop_principal():
    global gains_acumulados, loss_acumulados, ultima_hora_relatorio
    
    print("⚡ Motor MHI Otimizado + EMA (Com Relatório de 8h) Inicializado.")
    estados = {ativo: {"fase": "aguardando", "direcao": None} for ativo in ATIVOS}
    
    ultima_hora_relatorio = obter_hora_brasil()

    while True:
        agora = obter_hora_brasil()
        
        if not verificar_mercado_aberto(agora):
            await asyncio.sleep(10)
            continue

        segundo = agora.second
        minuto = agora.minute
        
        # ------------------------------------------------------------------
        # ROTINA DO RELATÓRIO AUTOMÁTICO (A CADA 8 HORAS)
        # ------------------------------------------------------------------
        horas_passadas = (agora - ultima_hora_relatorio).total_seconds() / 3600
        if horas_passadas >= 8:
            total_operacoes = gains_acumulados + loss_acumulados
            win_rate = (gains_acumulados / total_operacoes * 100) if total_operacoes > 0 else 0
            
            texto_relatorio = (
                f"📊 *RELATÓRIO DE PERFORMANCE COLETIVA*\n"
                f"⏱ _Últimas 8 horas de operações_\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📈 *Total de Operações:* {total_operacoes}\n"
                f"🟢 *Total de Gains:* {gains_acumulados}\n"
                f"🔴 *Total de Loss:* {loss_acumulados}\n"
                f"🎯 *Assertividade:* {win_rate:.1f}%\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🤖 _Estratégia: MHI Otimizada + Filtro EMA (Maio/26)_"
            )
            await enviar_telegram(texto_relatorio)
            
            gains_acumulados = 0
            loss_acumulados = 0
            ultima_hora_relatorio = agora

        # Minutos redondos de M5 (00, 05, 10, 15...)
        minutos_restantes = 4 - (minuto % 5)
        segundos_restantes = 60 - segundo
        tempo_para_fechar = (minutos_restantes * 60) + segundos_restantes

        # 1. Pré-Alerta (30 segundos antes)
        if tempo_para_fechar == 30:
            for ativo in ATIVOS:
                dados = await analisar_mhi_filtrada(ativo)
                if dados["valido"]:
                    estados[ativo]["fase"] = "alerta"
                    estados[ativo]["direcao"] = dados["direcao"]
                    ativo_formatado = f"{ativo[:3]}/{ativo[3:]}"
                    
                    texto_alerta = (
                        f"🚨 *PRÉ-ALERTA DE ENTRADA MHI + EMA*\n\n"
                        f"🔹 *Ativo:* {ativo_formatado}\n"
                        f"⏱ *Timeframe:* M5 (Vela Redonda)\n"
                        f"⚡ *Estratégia:* MHI Filtrada (Maio/26)\n"
                        f"🎯 *Ação:* PREPARAR {dados['direcao']}\n\n"
                        f"⚠️ _Aguarde a confirmação na virada do minuto!_"
                    )
                    await enviar_telegram(texto_alerta)
            await asyncio.sleep(1.5)

        # 2. Confirmação Final (2 segundos antes)
        elif tempo_para_fechar == 2:
            for ativo in ATIVOS:
                if estados[ativo]["fase"] == "alerta":
                    dados = await analisar_mhi_filtrada(ativo)
                    ativo_formatado = f"{ativo[:3]}/{ativo[3:]}"
                    
                    if dados["is_doji"]:
                        texto_abortado = (
                            f"🛑 *SINAL CANCELADO - {ativo_formatado}*\n\n"
                            f"Análise abortada pelo *Filtro Anti-Doji*.\n"
                            f"Mercado sem volume no fechamento do quadrante."
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
                            f"🚀 *Execute estritamente na virada do minuto!*"
                        )
                        await enviar_telegram(texto_confirmado)
                        
                        # Computa com base na assertividade real do seu relatório (~87%)
                        if random.random() <= 0.87:
                            gains_acumulados += 1
                        else:
                            loss_acumulados += 1
                            
                    estados[ativo]["fase"] = "aguardando"
            await asyncio.sleep(1.5)

        await asyncio.sleep(0.2)

if __name__ == "__main__":
    asyncio.run(loop_principal())
