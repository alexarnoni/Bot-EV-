import requests
import os
from dotenv import load_dotenv

load_dotenv()

class OddsAPI:
    def __init__(self):
        self.api_key = os.getenv("ODDS_API_KEY")
        if not self.api_key:
            raise ValueError("❌ ODDS_API_KEY não encontrada no .env")
        self.base_url = "https://api.odds-api.io/v2/"
        self.bookmaker = "Bet365"

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
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Erro ao buscar value bets: {e}")
            return []

    def __parse_evento(self, bet):
        try:
            bookmaker = bet.get('bookmaker', '').lower()
            if bookmaker != "bet365":
                return None

            odds = bet.get('bookmakerOdds', {})
            bet_side = bet.get('betSide', '').lower()

            if bet_side not in odds:
                return None

            try:
                odd_bet = float(odds[bet_side])
            except Exception:
                return None

            if not odd_bet or odd_bet < 1.50:
                return None

            return {
                "home": bet['event'].get('home', ''),
                "away": bet['event'].get('away', ''),
                "league": bet['event'].get('league', ''),
                "commence_time": bet['event'].get('date', ''),
                "id": bet.get('eventId', bet.get('id', '')),
                "sport": bet['event'].get('sport', ''),
                "market_type": bet.get('market', {}).get('name', bet.get('market_type', '')),
                "market_name": bet.get('market', {}).get('name', ''),
                "bet_side": bet.get('betSide', ''),
                "bet365_odds": odd_bet,
                "odds_home": float(odds.get('home', 0.0)),
                "odds_away": float(odds.get('away', 0.0)),
                "odds_draw": float(odds.get('draw', 0.0)),
                "hdp": bet.get('market', {}).get('hdp'),
                "total": bet.get('market', {}).get('total'),
                "ev": (bet.get('expectedValue', 0) / 100) - 1,
                "event_url": odds.get('href', '')
            }
        except Exception as e:
            print(f"Erro ao processar aposta: {e}")
            return None

    def get_eventos_geral(self):
        raw_bets = self.get_value_bets()
        eventos = []
        for bet in raw_bets:
            evento = self.__parse_evento(bet)
            if evento:
                eventos.append(evento)
        return eventos

    def get_eventos_futebol(self):
        raw_bets = self.get_value_bets()
        eventos = []
        for bet in raw_bets:
            try:
                if bet.get('event', {}).get('sport', '').lower() != 'football':
                    continue

                market_name = bet['market'].get('name', '').lower()
                mercados_permitidos = [
                    "spread", "ml", "ou", "dnb", "btts", "team_total", "anytime_goalscorer",
                    "bookings", "bookings spread", "bookings totals",
                    "booking", "booking spread", "booking totals",
                    "corners", "corners spread", "corners totals",
                    "corner", "corner spread", "corner totals"
                ]
                if market_name not in mercados_permitidos:
                    continue

                evento = self.__parse_evento(bet)
                if evento:
                    eventos.append(evento)
            except Exception as e:
                print(f"Erro ao processar value bet: {e}")
                continue
        return eventos
