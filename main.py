import logging
from api_client import OddsAPI
from cache import carregar_cache, salvar_cache, gerar_hash_alerta
from bot_ev import enviar_alerta
from bot_core import definir_stake
from utils import salvar_ligas_api_completo
import os
import json
import schedule
import time
from datetime import datetime, timezone

print("⚙️ main.py iniciado.")

# Configurar logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

def carregar_filtros():
    try:
        with open("filtros_por_chat.json", "r") as f:
            return json.load(f)
    except Exception:
        return {}
    
def main():
    logging.info("🔍 Iniciando busca por apostas com EV+ ...")
    api = OddsAPI()
    cache = carregar_cache()
    novas_apostas = 0

    # Carregar filtro do chat
    chat_id = str(os.getenv("TELEGRAM_CHAT_ID"))
    filtros = carregar_filtros()
    ligas_permitidas = filtros.get(chat_id, {}).get("ligas", None)
    esportes_permitidos = filtros.get(chat_id, {}).get("esportes", None)

    eventos = api.get_eventos_geral()
    
    if not eventos:
        logging.warning("Nenhum evento encontrado.")
        return

    chat_id = int(os.getenv("TELEGRAM_CHAT_ID"))

    for evento in eventos:
        try:
            # Filtro de Liga Dinâmico
            if esportes_permitidos and evento.get("sport") not in esportes_permitidos:
                continue
            if ligas_permitidas and evento.get("league") not in ligas_permitidas:
                continue

            # Checagens de odds válidas
            odd_bet365 = evento['bet365_odds']
            if odd_bet365 < 1.01 or odd_bet365 > 100:
                logging.info(f"⛔ Odd inválida ({odd_bet365}) para {evento['market_name']}")
                continue

            ev = evento['ev']
            stake, stake_sugerida = definir_stake(ev, odd_bet365)

            # Só envia se stake >= 0.1u e EV > 0.05
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

            # Adiciona aviso de stake sugerida > 2u
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
    salvar_ligas_api_completo(eventos)
    logging.info(f"🏁 Busca finalizada. {novas_apostas} alertas enviados.")
    logging.info(f"⏱️ main.py executado em {datetime.now(timezone.utc).isoformat()}")

def run_loop():
    main()  # roda a primeira vez assim que iniciar
    # agenda para rodar a cada 1 hora
    schedule.every(1).hours.do(main)
    print("⏰ Bot agendado para rodar a cada 1 hora.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_loop()
    # main() # Se quiser rodar só uma vez e sair, use só
