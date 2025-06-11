import logging
import sys
import io
import os
import json
import schedule
import time
from datetime import datetime, timezone
from api_client import OddsAPI
from cache import carregar_cache, salvar_cache, gerar_hash_alerta
from bot_ev import enviar_alerta
from bot_core import definir_stake
from utils import salvar_ligas_api_completo

# Corrige problemas de emoji no terminal Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("⚙️ main.py iniciado.")

# Configurar logs para terminal e arquivo
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("main.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def carregar_filtros():
    try:
        with open("filtros_por_chat.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def main():
    logging.info("🔍 Iniciando busca por apostas com EV+ ...")
    api = OddsAPI()
    filtros = carregar_filtros()
    eventos = api.get_eventos_geral()

    if not eventos:
        logging.warning("Nenhum evento encontrado.")
        return

    total_alertas = 0

    for chat_id, filtro in filtros.items():
        chat_id_str = str(chat_id)
        cache = carregar_cache(chat_id_str)
        novas_apostas = 0

        ligas_permitidas = filtro.get("ligas", None)
        esportes_permitidos = filtro.get("esportes", None)

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
                if alerta_hash in cache:
                    continue

                alerta_extra = ""
                if stake_sugerida > 2.0:
                    alerta_extra = "\n⚠️ <b>Stake sugerida acima de 2u! Reveja o risco antes de apostar.</b>"

                enviar_alerta(int(chat_id), evento, ev, stake, stake_sugerida, alerta_extra=alerta_extra)
                cache.add(alerta_hash)
                novas_apostas += 1
            except Exception as e:
                logging.error(f"[{chat_id}] Erro ao processar evento: {e}")
                continue

        salvar_cache(cache, chat_id_str)
        logging.info(f"✅ [{chat_id}] {novas_apostas} alertas enviados.")
        total_alertas += novas_apostas

    salvar_ligas_api_completo(eventos)
    logging.info(f"🏁 Busca finalizada. Total: {total_alertas} alertas enviados.")
    logging.info(f"⏱️ main.py executado em {datetime.now(timezone.utc).isoformat()}")

def run_loop():
    main()
    schedule.every(1).hours.do(main)
    print("⏰ Bot agendado para rodar a cada 1 hora.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_loop()
