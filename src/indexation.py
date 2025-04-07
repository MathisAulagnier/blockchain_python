import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


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

def download_data(symbol, start_date, end_date, interval):
    """
    Télécharge les données historiques d'un ETF à partir de yfinance.
    
    :param etf_symbol: Symbole de l'ETF (e.g., 'SPY')
    :param start_date: Date de début (format 'YYYY-MM-DD')
    :param end_date: Date de fin (format 'YYYY-MM-DD')
    :return: Un DataFrame contenant les données historiques (OHLCV)
    """
    stock = yf.Ticker(symbol)
    data = stock.history(start=start_date, end=end_date, interval=interval, )
    return stock, data

def get_date(date : str , day_before : int):
    """
    Récupère la date actuelle moins un certain nombre de jours.
    
    :param date: Date actuelle (format 'YYYY-MM-DD')
    :param day_before: Nombre de jours à soustraire
    :return: Date modifiée (format 'YYYY-MM-DD')
    """
    date = datetime.strptime(date, '%Y-%m-%d')
    date = date - timedelta(days=day_before)
    return date.strftime('%Y-%m-%d')

def get_current_date():
    """
    Récupère la date actuelle au format 'YYYY-MM-DD'.
    
    :return: Date actuelle (format 'YYYY-MM-DD')
    """
    return datetime.now().strftime('%Y-%m-%d')


def plot_value(period, show_derivate_product=False):
    """
    Affiche la valeur du token ((euro$ + yen$ + usd$) / 3) sur une période donnée.

    Paramètres :
    period (int) : Nombre de jours à afficher. 
    show_derivate_product (bool) : Indique si les valeurs des devises individuelles doivent être affichées.
    """

    # Récupérer la date actuelle
    today = datetime.now().strftime('%Y-%m-%d')
    # Calculer la date de début
    start_date = get_date(today, period)

    # Télécharger les données
    data_euro = download_data('EURUSD=X', start_date, today, '1d')[1]
    data_euro = data_euro[['Close']]

    data_yen = download_data('JPYUSD=X', start_date, today, '1d')[1]
    data_yen = data_yen[['Close']]

    
    data_usd = (data_euro['Close'] - data_euro['Close'] + 1)
    data_usd.index = data_usd.index.strftime('%Y-%m-%d')
    # print(data_usd)


    # Créer data_token
    data_token = data_euro.copy()
    data_token['Close'] = (data_euro['Close'] + data_yen['Close'] + 1) / 3
    data_token = data_token.rename(columns={'Close': 'Value'})
    data_token = data_token[['Value']]
    data_token.index = data_token.index.strftime('%Y-%m-%d')

    #print(data_token)
    
    # Calculer la valeur
    data_value = (data_euro['Close'] + data_yen['Close'] + 1) / 3
    data_value = data_value.rename("Value")
    # print(data_value)

    # Implémentation de la fonction d'affichage
    plt.figure(figsize=(10, 5))
    plt.plot(data_value.index, data_value, label='Token Value')
    plt.title('Token Value Over Time')

    if show_derivate_product:
        plt.plot(data_euro.index, data_euro['Close'], label='Euro Value')
        plt.plot(data_yen.index, data_yen['Close'], label='Yen Value')
        plt.axhline(y=1, color='orange', linestyle='-', label='Dollar Value')
    
    plt.xlabel('Date')
    plt.ylabel('Valeur')
    plt.legend()
    plt.show()

        


# print(get_value())
# plot_value(30, True)