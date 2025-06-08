def salvar_ligas_api_completo(lista_eventos, caminho_arquivo="ligas_api.txt"):
    """
    Salva todas as ligas únicas, mesmo aninhadas, em um arquivo txt.
    Busca 'league' em várias estruturas possíveis.
    """
    ligas = set()

    def extrair_liga(evento):
        # Tenta pegar league no nível mais alto
        if "league" in evento and evento["league"]:
            return evento["league"]
        # Tenta dentro de 'event'
        if "event" in evento and evento["event"]:
            e = evento["event"]
            if isinstance(e, dict) and "league" in e and e["league"]:
                return e["league"]
        # Tenta ainda outros níveis se necessário
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

