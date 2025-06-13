from datetime import datetime, timedelta

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

def extrair_odd(evento):
    bet_side = (evento.get("bet_side") or "").lower()
    if bet_side in ["home", "away", "draw"]:
        campo = f"odds_{bet_side}"
        if campo in evento:
            return evento[campo]
    return evento.get("bet365_odds")

def montar_nome_mercado(evento):
    from bot_ev import TRADUCAO_MERCADOS  # importa localmente para evitar ciclo

    nome_mercado_raw = evento.get("market_name") or evento.get("market_type") or ""
    nome_raw_lower = nome_mercado_raw.lower()

    if nome_raw_lower == "totals" and evento.get("sport", "").lower() == "football":
        nome_mercado_pt = "Mais de Gols"
    else:
        nome_mercado_pt = TRADUCAO_MERCADOS.get(nome_raw_lower, nome_mercado_raw.title())

    linha = evento.get("hdp") or evento.get("total")
    if isinstance(linha, (int, float)):
        linha = f"{float(linha):+g}" if linha != 0 else "0.0"
    elif isinstance(linha, list):
        linha = " / ".join([f"{float(x):+g}" for x in linha])
    else:
        linha = ""

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

    return nome_mercado_pt
