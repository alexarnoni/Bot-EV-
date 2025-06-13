import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
from bot_core import calcular_odd_minima, obter_probabilidade_real
from historico import registrar_alerta
from formatadores import montar_nome_mercado, extrair_odd, formatar_data_br

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

EMOJIS_POR_ESPORTE = {
    "football": "⚽",
    "tennis": "🎾",
    "basketball": "🏀",
    "baseball": "⚾",
    "hockey": "🏒",
    "mma": "🥋",
    "boxing": "🥊",
    "volleyball": "🏐",
    "esports": "🎮"
}

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
    "team total away": "Total Time Visitante",
    "bookings": "Cartões",
    "bookings spread": "Handicap de Cartões",
    "bookings totals": "Total de Cartões",
    "booking": "Cartões",
    "booking spread": "Handicap de Cartões",
    "booking totals": "Total de Cartões",
    "corners": "Cantos",
    "corners spread": "Handicap de Cantos",
    "corners totals": "Total de Cantos",
    "corner": "Cantos",
    "corner spread": "Handicap de Cantos",
    "corner totals": "Total de Cantos",
    "totals": "Total de Pontos",
    "match winner": "Vencedor da Partida",
    "set winner": "Vencedor do Set",
    "handicap games": "Handicap de Games",
    "over/under sets": "Total de Sets",
    "run line": "Handicap de Corridas",
    "total runs": "Total de Corridas",
    "fight winner": "Vencedor da Luta",
    "method of victory": "Método da Vitória",
    "round betting": "Aposta por Round"
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
        dt_br = dt_utc - timedelta(hours=3)
        return dt_br.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return dt_utc_str

def extrair_linha_mercado(evento):
    hdp = evento.get("hdp")
    total = evento.get("total")
    if isinstance(hdp, list):
        return " / ".join([f"{float(x):+g}" for x in hdp])
    if isinstance(total, list):
        return " / ".join([f"{float(x):g}" for x in total])
    if hdp is not None:
        try:
            valor = float(hdp)
            return f"{valor:+g}" if valor != 0 else "0.0"
        except Exception:
            return str(hdp)
    if total is not None:
        try:
            valor = float(total)
            return f"{valor:g}" if valor != 0 else "0.0"
        except Exception:
            return str(total)
    return ""

def montar_nome_mercado(evento):
    nome_mercado_raw = evento.get("market_name") or evento.get("market_type") or ""
    nome_raw_lower = nome_mercado_raw.lower()

    # Substituir "totals" por "Mais de Gols" se for futebol
    if nome_raw_lower == "totals" and evento.get("sport", "").lower() == "football":
        nome_mercado_pt = "Mais de Gols"
    else:
        nome_mercado_pt = TRADUCAO_MERCADOS.get(nome_raw_lower, nome_mercado_raw.title())

    linha = extrair_linha_mercado(evento)
    lado = evento.get("bet_side")
    lado_pt = TRADUCAO_LADOS.get(str(lado).lower(), lado.title() if lado else "")

    if lado_pt and nome_mercado_pt.lower() in [
        "moneyline", "empate anula", "handicap asiático", "handicap ht",
        "team total home", "team total away", "handicap de games", "handicap de corridas"
    ]:
        nome_mercado_pt += f" ({lado_pt})"

    if linha and nome_mercado_pt.lower() not in [
        "moneyline", "empate anula", "ambos marcam", "marcar a qualquer momento", "vencedor da partida"
    ]:
        nome_mercado_pt += f" {linha}"

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

def enviar_alerta(chat_id, evento, ev, stake=None, stake_sugerida=None, alerta_extra=""):
    esporte = evento.get("sport", "").lower()
    emoji_esporte = EMOJIS_POR_ESPORTE.get(esporte, "🏅")

    nome_mercado = montar_nome_mercado(evento)
    odd_especifica = extrair_odd(evento)
    url_bet = evento.get('event_url', '')
    if url_bet.startswith('https://www.bet365.com/#/'):
        url_bet = url_bet.replace('https://www.bet365.com/', 'https://www.bet365.bet.br/')
    data_jogo = evento.get("commence_time") or evento.get("date")
    data_formatada = formatar_data_br(data_jogo) if data_jogo else ""

    odd_pinnacle = evento.get("pinnacle_odds")
    prob_real = obter_probabilidade_real(odd_pinnacle) if odd_pinnacle else None
    odd_min = calcular_odd_minima(ev, prob_real) if prob_real else None

    msg = ""

    if esporte != "football":
        msg += f"{emoji_esporte} <b>{esporte.title()}</b>\n"

    msg += (
        f"⚽ <b>{evento['home']} vs {evento['away']}</b>\n"
        f"<b>Mercado:</b> <i>{nome_mercado}</i>\n"
        f"🔢 <b>Odd Bet365:</b> <i>{odd_especifica:.2f}</i>\n"
    )

    if odd_min:
        msg += f"🔻 <b>Odd mínima recomendada:</b> <i>{odd_min:.2f}</i>\n"

    msg += (
        f"💰 <b>EV:</b> <i>{ev:.2%}</i>\n"
        f"🎯 <b>Stake sugerida:</b> <i>{stake:.2f}u</i>\n"
    )

    if alerta_extra:
        msg += f"{alerta_extra}\n"

    msg += (
        f"🗓️ <b>{data_formatada}</b>\n"
        f"<a href='{url_bet}'>🔗 Link Bet365</a>"
    )

    url = (
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        f"?chat_id={chat_id}&text={requests.utils.quote(msg)}&parse_mode=HTML"
    )

    try:
        response = requests.get(url)
        if response.status_code == 403:
            print(f"⚠️ Usuário {chat_id} bloqueou o bot ou saiu.")
        else:
            # Apenas registra se o alerta foi realmente enviado
            from historico import registrar_alerta
            registrar_alerta(chat_id, evento, ev, stake, stake_sugerida)
    except Exception as e:
        print(f"❌ Erro ao enviar alerta para {chat_id}: {e}")
