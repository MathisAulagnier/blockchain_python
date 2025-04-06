import yfinance as yf


def get_value():
    """
    Récupère la valeur actuelle de Euro en USD.
    Récupère la valeur actuelle du Yen en USD.
    Retourne (1 + valeur Euro + valeur Yen) / 3
    """
    try:
        euro = yf.Ticker('EURUSD=X')
        yen = yf.Ticker('JPYUSD=X')

        # print(f"Valeur Euro: {round(euro.info['regularMarketPrice'], 2)}")
        # print(f"Valeur Yen: {round(yen.info['regularMarketPrice'], 2)}")
    
        # Calculer la valeur
        value = (1 + euro.info['regularMarketPrice'] + yen.info['regularMarketPrice']) / 3
        return round(value, 2)
    except Exception as e:
        print(f"Erreur lors de la récupération des valeurs: {e}")
        # Valeur par défaut en cas d'erreur
        return None


# print(get_value())