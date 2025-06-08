import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
from bot_core import calcular_odd_minima, obter_probabilidade_real

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Tradução dos mercados e dos lados (bet_side)
TRADUCAO_MERCADOS = {
    "spread": "Handicap Asiático",
    "spread ht": "Handicap HT",
    "ml": "Moneyline",
    "ou": "Over/Under",
    "dnb": "Empate Anula",
    "btts": "Ambos Marcam",
    "team_total": "Total do Time",
    "anytime_goalscorer": "Marcar a Qualquer Momento",
    "team total home": "Total Time da Casa",
    "team total away": "Total Time Visitante"
}
TRADUCAO_LADOS = {
    "home": "Casa",
    "away": "Fora",
    "draw": "Empate",
    "over": "Over",
    "under": "Under"
}

def formatar_data_br(dt_utc_str):
    try:
        dt_utc = datetime.strptime(dt_utc_str.replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
        dt_br = dt_utc - timedelta(hours=3)  # UTC-3 (Brasília)
        return dt_br.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return dt_utc_str

def extrair_linha_mercado(evento):
    hdp = None
    total = None
    market = evento.get("market", {})
    if isinstance(market, dict):
        hdp = market.get("hdp")
        total = market.get("total")
    if hdp is None:
        hdp = evento.get("hdp")
    if total is None:
        total = evento.get("total")
    if hdp is not None:
        if isinstance(hdp, list):
            return " / ".join([f"{float(x):+g}" for x in hdp])
        try:
            return f"{float(hdp):+g}"
        except Exception:
            return str(hdp)
    if total is not None:
        if isinstance(total, list):
            return " / ".join([f"{float(x):g}" for x in total])
        try:
            return f"{float(total):g}"
        except Exception:
            return str(total)
    return ""

def montar_nome_mercado(evento):
    nome_mercado_raw = evento.get("market_name") or evento.get("market_type") or ""
    nome_mercado_pt = TRADUCAO_MERCADOS.get(nome_mercado_raw.lower(), nome_mercado_raw)
    linha = extrair_linha_mercado(evento)
    lado = evento.get("bet_side")
    lado_pt = TRADUCAO_LADOS.get(str(lado).lower(), None)

    # Mostra o lado nos mercados relevantes (ML, DNB, Handicap etc)
    if lado_pt and nome_mercado_pt.lower() in [
        "moneyline", "empate anula", "handicap asiático", "handicap ht",
        "team total home", "team total away"
    ]:
        nome_mercado_pt += f" ({lado_pt})"
    # Linha só onde faz sentido
    if linha and nome_mercado_pt.lower() not in ["moneyline", "empate anula", "ambos marcam", "marcar a qualquer momento"]:
        nome_mercado_pt += f" {linha}"
    # Para Over/Under, inclui lado + linha
    if nome_mercado_pt.lower().startswith("over/under") and lado_pt:
        nome_mercado_pt = f"{nome_mercado_pt} [{lado_pt}]"
    return nome_mercado_pt

def extrair_odd(evento):
    bet_side = (evento.get("bet_side") or "").lower()
    if bet_side in ["home", "away", "draw"]:
        campo = f"odds_{bet_side}"
        if campo in evento:
            return evento[campo]
    return evento.get("bet365_odds")

def enviar_alerta(evento, ev, stake=None, stake_sugerida=None, alerta_extra=""):
    nome_mercado = montar_nome_mercado(evento)
    odd_especifica = extrair_odd(evento)
    url_bet = evento.get('event_url', '')
    if url_bet.startswith('https://www.bet365.com/#/'):
        url_bet = url_bet.replace('https://www.bet365.com/', 'https://www.bet365.bet.br/')
    data_jogo = evento.get("commence_time") or evento.get("date")
    data_formatada = formatar_data_br(data_jogo) if data_jogo else ""

    # Cálculo da odd mínima (requer odd de referência - pinnacle_odds)
    odd_pinnacle = evento.get("pinnacle_odds")
    prob_real = obter_probabilidade_real(odd_pinnacle) if odd_pinnacle else None
    odd_min = calcular_odd_minima(ev, prob_real) if prob_real else None

    msg = (
        f"⚽ <b>{evento['home']} vs {evento['away']}</b>\n"
        f"<b>Mercado:</b> <i>{nome_mercado}</i>\n"
        f"🔢 <b>Odd Bet365:</b> <i>{evento['bet365_odds']:.2f}</i>\n"
    )
    if odd_min:
        msg += f"🔻 <b>Odd mínima recomendada:</b> <i>{odd_min:.2f}</i>\n"
    msg += (
        f"💰 <b>EV:</b> <i>{ev:.2%}</i>\n"
        f"🎯 <b>Stake sugerida:</b> <i>{stake:.2f}u</i>\n"
    )
    if alerta_extra:
        msg += f"{alerta_extra}\n"  # Alerta vem aqui!
    msg += (
        f"🗓️ <b>{data_formatada}</b>\n"
        f"<a href='{url_bet}'>🔗 Link Bet365</a>"
    )

    url = (
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        f"?chat_id={TELEGRAM_CHAT_ID}&text={requests.utils.quote(msg)}&parse_mode=HTML"
    )
    requests.get(url)
