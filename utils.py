import json

def salvar_ligas_api_completo(lista_eventos, caminho_arquivo="ligas_api.txt"):
    """
    Salva as ligas dos eventos que passaram nos filtros e geraram alerta.
    Ideal para mostrar somente ligas que estão sendo realmente usadas no bot.
    """
    ligas = set()

    def extrair_liga(evento):
        if "league" in evento and evento["league"]:
            return evento["league"]
        if "event" in evento and evento["event"]:
            e = evento["event"]
            if isinstance(e, dict) and "league" in e and e["league"]:
                return e["league"]
        return None

    for evento in lista_eventos:
        liga = extrair_liga(evento)
        if liga:
            ligas.add(liga)

    ligas_ordenadas = sorted(ligas)
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        for liga in ligas_ordenadas:
            f.write(liga + "\n")
    print(f"Ligas salvas em {caminho_arquivo} ({len(ligas_ordenadas)} ligas).")


def salvar_ligas_encontradas(lista_eventos, caminho_arquivo="ligas_encontradas.txt"):
    """
    Salva todas as ligas encontradas na resposta da API, mesmo que não gerem alerta.
    Ideal para explorar ligas novas ou que estão sendo ignoradas.
    """
    ligas = set()

    def extrair_liga(evento):
        if "league" in evento and evento["league"]:
            return evento["league"]
        if "event" in evento and isinstance(evento["event"], dict) and "league" in evento["event"]:
            return evento["event"]["league"]
        return None

    for evento in lista_eventos:
        liga = extrair_liga(evento)
        if liga:
            ligas.add(liga)

    ligas_ordenadas = sorted(ligas)
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        for liga in ligas_ordenadas:
            f.write(liga + "\n")
    print(f"Ligas encontradas salvas em {caminho_arquivo} ({len(ligas_ordenadas)} ligas).")
