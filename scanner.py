import logging
from api_client import OddsAPI
from cache import carregar_cache, salvar_cache, gerar_hash_alerta
from bot_ev import enviar_alerta
from bot_core import definir_stake
from utils import salvar_ligas_api_completo, salvar_ligas_encontradas 
import os
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

def carregar_filtros():
    try:
        with open("filtros_por_chat.json", "r") as f:
            return json.load(f)
    except Exception:
        return {}

def scan_apostas():
    logging.info("🔍 Iniciando busca por apostas com EV+ ...")
    api = OddsAPI()
    cache = carregar_cache()
    novas_apostas = 0

    chat_id = str(os.getenv("TELEGRAM_CHAT_ID"))
    filtros = carregar_filtros()
    ligas_permitidas = filtros.get(chat_id, {}).get("ligas", None)
    esportes_permitidos = filtros.get(chat_id, {}).get("esportes", None)

    eventos = api.get_eventos_geral()

    if not eventos:
        logging.warning("Nenhum evento encontrado.")
        return "Nenhum evento encontrado."

    chat_id = int(os.getenv("TELEGRAM_CHAT_ID"))

    for evento in eventos:
        try:
            if esportes_permitidos and evento.get("sport") not in esportes_permitidos:
                continue
            if ligas_permitidas and evento.get("league") not in ligas_permitidas:
                continue

            odd_bet365 = evento['bet365_odds']
            if odd_bet365 < 1.01 or odd_bet365 > 100:
                logging.info(f"⛔ Odd inválida ({odd_bet365}) para {evento['market_name']}")
                continue

            ev = evento['ev']
            stake, stake_sugerida = definir_stake(ev, odd_bet365)

            if ev <= 0.05 or stake < 0.1:
                logging.info(
                    f"❌ Descartado {evento['home']} vs {evento['away']} [{evento['market_name']}] "
                    f"| EV: {ev:.2%} | Stake: {stake:.2f}u"
                )
                continue

            alerta_hash = gerar_hash_alerta(evento)
            if not alerta_hash or alerta_hash in cache:
                logging.info(
                    f"🔁 Alerta já enviado para {evento['home']} vs {evento['away']} [{evento['market_name']}]"
                )
                continue

            alerta_extra = ""
            if stake_sugerida > 2.0:
                alerta_extra = "\n⚠️ <b>Stake sugerida acima de 2u! Reveja o risco antes de apostar.</b>"

            enviar_alerta(evento, ev, stake, stake_sugerida, alerta_extra=alerta_extra)
            cache.add(alerta_hash)
            novas_apostas += 1
            logging.info(
                f"✅ ALERTA ENVIADO: {evento['home']} vs {evento['away']} [{evento['market_name']}] "
                f"| EV: {ev:.2%} | Stake: {stake:.2f}u"
            )
        except Exception as e:
            logging.error(f"Erro ao processar evento: {e}")
            continue

    salvar_cache(cache)
    salvar_ligas_api_completo([e for e in eventos if gerar_hash_alerta(e) in cache])  # só eventos alertados
    salvar_ligas_encontradas(eventos)  # todos os eventos que vieram da API

    logging.info(f"🏁 Busca finalizada. {novas_apostas} alertas enviados.")

    return f"{novas_apostas} alertas enviados." if novas_apostas else "Nenhum alerta novo."

# --- Se quiser rodar scanner manual pelo terminal:
if __name__ == "__main__":
    print(scan_apostas())
