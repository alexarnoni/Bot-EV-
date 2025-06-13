def obter_probabilidade_real(odd_pinnacle):
    return 1 / odd_pinnacle if odd_pinnacle > 0 else 0

def calcular_ev(odd_bet365, odd_pinnacle):
    try:
        prob_real = 1 / odd_pinnacle if odd_pinnacle > 0 else 0
        return (odd_bet365 * prob_real) - 1
    except Exception as e:
        print(f"Erro no cálculo de EV: {e}")
        return 0

def calcular_odd_minima(ev, prob_real):
    """Calcula a odd mínima para manter o mesmo EV do alerta."""
    try:
        return (ev + 1) / prob_real if prob_real > 0 else None
    except Exception:
        return None

def definir_stake(ev, odd):
    """
    Define stake fixa com base apenas na odd:
    - Odds entre 1.50 e 3.50 → 1.0u
    - Odds entre 3.51 e 8.00 → 0.5u
    - Odds acima de 8.00       → 0.25u
    - Odds fora desses intervalos → 0.1u (ou 0 se EV baixo)

    EV mínimo para considerar: 5%
    Stake mínima real: 0.10u
    Stake máxima sugerida: 2.00u
    Retorna: (stake_usada, stake_sugerida)
    """
    if ev < 0.05:
        return 0, 0  # Ignora apostas com pouco valor esperado

    if 1.50 <= odd <= 3.50:
        stake = 1.0
    elif 3.51 <= odd <= 8.00:
        stake = 0.5
    elif odd > 8.00:
        stake = 0.25
    else:
        stake = 0.1  # Odds muito baixas, ainda assim permitido com stake mínima

    stake = round(stake, 2)
    stake_sugerida = min(stake, 2.0)
    return stake_sugerida, stake_sugerida
