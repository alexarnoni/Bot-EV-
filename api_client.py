import requests
import os
from dotenv import load_dotenv

load_dotenv()

class OddsAPI:
    def __init__(self):
        self.api_key = os.getenv("ODDS_API_KEY")
        self.base_url = "https://api.odds-api.io/v2/"
        self.bookmaker = "Bet365"  # pode ser parametrizado

    def get_value_bets(self):
        url = f"{self.base_url}value-bets"
        params = {
            "apiKey": self.api_key,
            "bookmaker": self.bookmaker,
            "includeEventDetails": "true"
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data
        except Exception as e:
            print(f"Erro ao buscar value bets: {e}")
            return []

    def get_eventos_futebol(self):
        raw_bets = self.get_value_bets()
        # print("EXEMPLO DE RAW BETS:", raw_bets[:2])  Ajuda debug!
        eventos = []
        for bet in raw_bets:
            try:
                # print("LIGA:", bet['event'].get('league', 'SEM LIGA'))
                # Só futebol e mercado principal Bet365
                if bet.get('event', {}).get('sport', '').lower() != 'football':
                    continue

                market_name = bet['market'].get('name', '').lower()  # ex: 'spread', 'ml'
                mercados_permitidos = [
                    "spread", "ml", "ou", "dnb", "btts", "team_total", "anytime_goalscorer"
                ]
                if market_name not in mercados_permitidos:
                    continue

                # Odds
                bookmaker = bet.get('bookmaker', '').lower()
                if bookmaker != "bet365":
                    continue

                # Pega os times, odds, link, etc
                home = bet['event'].get('home', '')
                away = bet['event'].get('away', '')
                commence_time = bet['event'].get('date', '')
                event_id = bet.get('eventId', '')
                url = bet.get('bookmakerOdds', {}).get('href', '#')
                expected_value = bet.get('expectedValue', 0)
                
                # Odd para cada tipo de mercado
                # Exemplos:
                # Para Spread: odds em bookmakerOdds['home'] e bookmakerOdds['away']
                # Para ML: odds em bookmakerOdds['home'], ['draw'], ['away']
                odds = bet.get('bookmakerOdds', {})
                # Pega a odd conforme o lado da aposta
                bet_side = bet.get('betSide', '').lower()  # home, away, draw
                odd_bet = None
                if bet_side in odds:
                    try:
                        odd_bet = float(odds[bet_side])
                    except Exception:
                        continue
                else:
                    continue

                # Em alguns casos pode ter odd absurda, filtra
                if not odd_bet or odd_bet < 1.01 or odd_bet > 100:
                    continue

                # **Pinnacle odds não vem** – use só como exemplo, ou coloque None
                eventos.append({
                    "home": bet['event'].get('home', ''),
                    "away": bet['event'].get('away', ''),
                    "league": bet['event'].get('league', ''),
                    "commence_time": bet['event'].get('date', ''),  # pode ser 'commence_time' dependendo do endpoint
                    "id": bet.get('eventId', bet.get('id', '')),
                    "market_type": bet.get('market', {}).get('name', bet.get('market_type', '')),
                    "market_name": bet.get('market', {}).get('name', ''),
                    "bet_side": bet.get('betSide', ''),  # home/away/draw/over/under etc
                    "bet365_odds": float(bet.get('bookmakerOdds', {}).get(bet.get('betSide', ''), 0.0)),
                    "odds_home": float(bet.get('bookmakerOdds', {}).get('home', 0.0)),
                    "odds_away": float(bet.get('bookmakerOdds', {}).get('away', 0.0)),
                    "odds_draw": float(bet.get('bookmakerOdds', {}).get('draw', 0.0)),
                    "hdp": bet.get('market', {}).get('hdp'),
                    "total": bet.get('market', {}).get('total'),
                    "ev": (bet.get('expectedValue', 0) / 100) - 1,
                    "event_url": bet.get('bookmakerOdds', {}).get('href', ''),
                })
            except Exception as e:
                print(f"Erro ao processar value bet: {e}")
                continue
        return eventos


