import pickle
import hashlib
import os

def gerar_hash_alerta(evento):
    try:
        base = f"{evento['id']}|{evento['market_type']}|{evento['bet365_odds']}"
        return hashlib.sha256(base.encode()).hexdigest()
    except Exception as e:
        print(f"Erro ao gerar hash do alerta: {e}")
        return None

def get_cache_path(chat_id):
    return f"cache/alert_cache_{chat_id}.pkl"

def carregar_cache(chat_id):
    path = get_cache_path(chat_id)
    if not os.path.exists(path):
        return set()
    with open(path, "rb") as f:
        return pickle.load(f)

def salvar_cache(cache, chat_id):
    path = get_cache_path(chat_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(cache, f)

def excluir_cache(chat_id):
    try:
        caminho = get_cache_path(chat_id)  # usa o mesmo padrão do restante
        if os.path.exists(caminho):
            os.remove(caminho)
    except Exception as e:
        print(f"Erro ao excluir cache de {chat_id}: {e}")

