import yfinance as yf
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns

from IPython.display import display


def download_etf_data(ticker_symbol: str, period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    """
    Downloads historical ETF data for a given ticker symbol.

    Args:
        ticker_symbol (str): The ticker symbol of the ETF.
        period (str): The period over which to download data (e.g., "5y", "1y", "3mo").
        interval (str): The interval of the data (e.g., "1d", "1wk", "1mo").

    Returns: 
        pd.DataFrame: A DataFrame containing the historical ETF data.
    """
    print(f"Downloading data for {ticker_symbol}...")
    df = yf.download(ticker_symbol, period=period, interval=interval, auto_adjust=False)
    df = df.reset_index()
    return df


def save_dataframe_to_csv(df: pd.DataFrame, filename: str) -> None:
    """
    Saves a pandas DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        filename (str): The name of the CSV file.
    """
    print(f"Saving data to {filename}...")
    df.to_csv(filename, index=False)
    print("Data saved successfully.")
    return 

ticker = "HDFCGOLD.NS"
file_name = "hdfc_gold_5_year_etf.csv"
hdfc_gold_5_year_etf = download_etf_data(ticker_symbol=ticker, period="5y", interval="1d")
save_dataframe_to_csv(df=hdfc_gold_5_year_etf, filename=file_name)


def get_scheme_code_list (scheme_name: str) -> pd.DataFrame:

  res = requests.get("https://api.mfapi.in/mf")
  data = res.json()
  mf_df = pd.DataFrame(data)

  df_scheme = mf_df[mf_df["schemeName"].str.contains(scheme_name, case=False, na=False)]
  return df_scheme


df_scheme = get_scheme_code_list(scheme_name='hdfc gold')
display(df_scheme)


def get_nav(scheme_code: str) -> pd.DataFrame:

  res = requests.get(f"https://api.mfapi.in/mf/{scheme_code}")
  data = res.json()
  df_nav = pd.DataFrame(data['data'])
  df_nav.to_csv(f"{scheme_code}.csv", index=False)
  return df_nav


df_nav = get_nav(scheme_code='119132')


def compare_mf_nav_with(mf_csv, nav_csv) -> pd.DataFrame:
  df_mf = pd.read_csv(mf_csv)
  df_nav = pd.read_csv(nav_csv)

  df_nav = df_nav.rename(columns={'date': 'Date'})
  df_nav['Date'] = pd.to_datetime(df_nav['Date'])

  df_mf = df_mf.drop(columns=['Open', 'High', 'Low', 'Adj Close', 'Volume'])
  df_mf = df_mf.dropna()
  df_mf['Date'] = pd.to_datetime(df_mf['Date'])
  df_mf['Close'] = df_mf['Close'].str.replace(',', '').astype(float)

  combine_df = pd.merge(df_mf, df_nav, on='Date', how='inner')

  combine_df.sort_values(by='Date', ascending=True, inplace=True)
  display(combine_df.head())
  correlation = combine_df['Close'].corr(combine_df['nav'])
  print(f"Correlation between Close and NAV: {correlation}")

  fig, ax1 = plt.subplots(figsize=(10, 5))

  # Plot Close Price on primary y-axis with a solid blue line
  sns.lineplot(data=combine_df, x='Date', y='Close', label='Close Price', color='blue', linestyle='-', ax=ax1)
  ax1.set_xlabel('Date')
  ax1.set_ylabel('Close Price', color='blue')
  ax1.tick_params(axis='y', labelcolor='blue')
  ax1.legend(loc='upper left')

  # Create a secondary y-axis for NAV with a dashed red line
  ax2 = ax1.twinx()
  sns.lineplot(data=combine_df, x='Date', y='nav', label='NAV (Net Asset Value)', color='red', linestyle='--', ax=ax2)
  ax2.set_ylabel('NAV (Net Asset Value)', color='red')
  ax2.tick_params(axis='y', labelcolor='red')
  ax2.legend(loc='upper right')

  plt.title('Close Price and NAV over Time')
  plt.grid(True)
  plt.xticks(rotation=45)
  plt.tight_layout()
  plt.show()

  return combine_df

combine_df = compare_mf_nav_with(mf_csv='hdfc_gold_5_year_etf.csv', nav_csv='119132.csv')