def obter_probabilidade_real(odd_pinnacle):
    return 1 / odd_pinnacle if odd_pinnacle > 0 else 0

def calcular_ev(odd_bet365, odd_pinnacle):
    try:
        prob_real = 1 / odd_pinnacle if odd_pinnacle > 0 else 0
        return (odd_bet365 * prob_real) - 1
    except Exception as e:
        print(f"Erro no cálculo de EV: {e}")
        return 0

def definir_stake(ev, odd, bankroll=1.0):
    """
    Stake dinâmica híbrida:
    - Odds muito baixas (<1.40): só aposta se EV > 3%, máximo 0.25u
    - Odds baixas (1.40–1.79): Kelly fracionado (mais conservador)
    - Odds médias (1.8–3.0) + EV ≥ 5%: stake nunca menor que 1u
    - Odds médias/altas: Kelly fracionado
    - Odds muito altas (>10): sempre 1/4 Kelly
    Stake mínima 0.10u, máxima 2.0u
    Retorna: (stake_usada, stake_sugerida)
    """
    if ev < 0.05:
        return 0, 0

    def fracao_kelly_dinamico(ev, odd):
        if odd > 10 or odd < 1.4:
            return 0.25
        if ev < 0.06:
            return 0.25
        elif ev < 0.12:
            return 0.5
        else:
            return 0.75

    # Odds muito baixas: limita aposta
    if odd < 1.40:
        if ev < 0.03:
            return 0, 0
        stake = min(0.25, ev * 15)
    else:
        k = fracao_kelly_dinamico(ev, odd)
        b = odd - 1
        p = (ev + 1) / odd
        q = 1 - p
        stake = k * ((b * p - q) / b) * bankroll
        if stake <= 0:
            return 0, 0

    stake = max(0.10, stake)
    stake_arred = round(stake * 20) / 20  # arredonda para 0.05u

    # Odds médias: stake mínima de 1u se EV >= 5%
    if 1.5 <= odd <= 3.0 and ev >= 0.05:
        stake_arred = max(stake_arred, 1.0)

    # Limita máximo prático (2u)
    if stake_arred > 2.0:
        return 2.0, stake_arred
    return stake_arred, stake_arred

def calcular_odd_minima(ev, prob_real):
    """Calcula a odd mínima para manter o mesmo EV do alerta."""
    try:
        return (ev + 1) / prob_real if prob_real > 0 else None
    except Exception:
        return None
