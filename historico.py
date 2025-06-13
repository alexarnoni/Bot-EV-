import os
import csv
from datetime import datetime
from formatadores import montar_nome_mercado, extrair_odd, formatar_data_br

def registrar_alerta(chat_id, evento, ev, stake, stake_sugerida):
    pasta = "historico_apostas"
    os.makedirs(pasta, exist_ok=True)
    arquivo = os.path.join(pasta, f"{chat_id}.csv")

    campos = [
        "data_envio", "esporte", "home", "away", "mercado",
        "odd", "stake", "stake_sugerida", "ev", "data_jogo", "url_bet"
    ]

    data_envio = datetime.now().strftime("%d/%m/%Y %H:%M")
    mercado = montar_nome_mercado(evento)
    odd = extrair_odd(evento)
    data_jogo = formatar_data_br(evento.get("commence_time") or evento.get("date") or "")
    url_bet = evento.get("event_url", "")

    linha = [
        data_envio,
        evento.get("sport", ""),
        evento.get("home", ""),
        evento.get("away", ""),
        mercado,
        f"{odd:.2f}",
        f"{stake:.2f}",
        f"{stake_sugerida:.2f}",
        f"{ev:.4f}",
        data_jogo,
        url_bet
    ]

    novo_arquivo = not os.path.exists(arquivo)

    with open(arquivo, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if novo_arquivo:
            writer.writerow(campos)
        writer.writerow(linha)
