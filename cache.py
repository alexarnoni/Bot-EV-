import pickle
import hashlib
import os

CACHE_FILE = "alert_cache.pkl"

def gerar_hash_alerta(evento):
    try:
        base = f"{evento['id']}|{evento['market_type']}|{evento['bet365_odds']}"
        return hashlib.sha256(base.encode()).hexdigest()
    except Exception as e:
        print(f"Erro ao gerar hash do alerta: {e}")
        return None

def carregar_cache():
    if not os.path.exists(CACHE_FILE):
        return set()
    with open(CACHE_FILE, "rb") as f:
        return pickle.load(f)

def salvar_cache(cache):
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache, f)
