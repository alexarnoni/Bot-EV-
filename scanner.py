import logging
from api_client import OddsAPI
from cache import carregar_cache, salvar_cache, gerar_hash_alerta
from bot_ev import enviar_alerta
from bot_core import definir_stake
from utils import salvar_ligas_api_completo, salvar_ligas_encontradas
import os
import json
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

def carregar_filtros():
    try:
        with open("filtros_por_chat.json", "r") as f:
            return json.load(f)
    except Exception:
        return {}

def scan_apostas(chat_id=None):
    logging.info("🔍 Iniciando busca por apostas com EV+ ...")
    api = OddsAPI()
    
    if chat_id is None:
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if chat_id is None:
        logging.error("❌ chat_id não fornecido e não encontrado no ambiente.")
        return "Erro: chat_id ausente."

    chat_id = str(chat_id)
    cache = carregar_cache(chat_id)
    novas_apostas = 0

    filtros = carregar_filtros()
    ligas_permitidas = filtros.get(chat_id, {}).get("ligas", None)
    esportes_permitidos = filtros.get(chat_id, {}).get("esportes", None)

    eventos = api.get_eventos_geral()
    if not eventos:
        logging.warning("Nenhum evento encontrado.")
        return "Nenhum evento encontrado."

    eventos_alertados = []

    for evento in eventos:
        try:
            if esportes_permitidos and evento.get("sport") not in esportes_permitidos:
                continue
            if ligas_permitidas and evento.get("league") not in ligas_permitidas:
                continue

            odd_bet365 = evento['bet365_odds']
            if odd_bet365 < 1.01 or odd_bet365 > 100:
                continue

            ev = evento['ev']
            stake, stake_sugerida = definir_stake(ev, odd_bet365)

            if ev <= 0.05 or stake < 0.1:
                continue

            alerta_hash = gerar_hash_alerta(evento)
            if not alerta_hash or alerta_hash in cache:
                continue

            alerta_extra = ""
            if stake_sugerida > 2.0:
                alerta_extra = "\n⚠️ <b>Stake sugerida acima de 2u! Reveja o risco antes de apostar.</b>"

            enviar_alerta(chat_id, evento, ev, stake, stake_sugerida, alerta_extra=alerta_extra)
            cache.add(alerta_hash)
            novas_apostas += 1
            eventos_alertados.append(evento)
        except Exception as e:
            logging.error(f"Erro ao processar evento: {e}")
            continue

    salvar_cache(cache, chat_id)
    salvar_ligas_api_completo(eventos_alertados)
    salvar_ligas_encontradas(eventos)

    logging.info(f"🏁 Busca finalizada. {novas_apostas} alertas enviados.")
    return f"{novas_apostas} alertas enviados." if novas_apostas else "Nenhum alerta novo."

# --- Execução direta pelo terminal:
if __name__ == "__main__":
    chat_id_env = os.getenv("TELEGRAM_CHAT_ID")
    print(scan_apostas(chat_id=chat_id_env))
