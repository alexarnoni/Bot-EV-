import os
import json
import logging
from cache import excluir_cache

# Garantir que o logging vá para o main.log também neste módulo
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("main.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def remover_usuario(chat_id):
    try:
        chat_id_str = str(chat_id)

        # Remover filtros
        if os.path.exists("filtros_por_chat.json"):
            with open("filtros_por_chat.json", "r", encoding="utf-8") as f:
                filtros = json.load(f)

            if chat_id_str in filtros:
                del filtros[chat_id_str]
                with open("filtros_por_chat.json", "w", encoding="utf-8") as f:
                    json.dump(filtros, f, indent=2, ensure_ascii=False)
                logging.info(f"🧹 Filtros de {chat_id} removidos.")

        # Remover cache
        excluir_cache(chat_id_str)
        logging.info(f"⚠️ Usuário {chat_id} bloqueou o bot. Removido da lista.")

    except Exception as e:
        logging.error(f"❌ Erro ao remover usuário {chat_id}: {e}")
