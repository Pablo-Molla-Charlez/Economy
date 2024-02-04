import datetime
import yfinance as yf
import pandas as pd

# Tickers for each Universe
canary_tickers = ["TIP"]
offensive_tickers = ["SPY", "IWM", "VEA", "VWO", "DBC", "VNQ", "TLT"]
defensive_tickers = ["BIL", "IEF"]
haa_tickers = ["SPY", "IWM", "VEA", "VWO", "DBC", "VNQ", "TLT", "TIP", "BIL", "IEF"]


def fetch_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)
    return data['Adj Close']


# Downloaded data
online = pd.DataFrame(fetch_data(haa_tickers, '2022-01-01', datetime.datetime.today()))

# Online data grouped by month
online_monthly = online.resample("BM").last()
online_monthly.rename(index={online_monthly.index[-1]:datetime.datetime.today()},inplace=True)
online_monthly.index = online_monthly.index.strftime('%B %d, %Y')
online_monthly = online_monthly[:len(online_monthly)-1]

# Periods of months
periods = [1, 3, 6, 12]


# Function to compute the 13612U Momentum
def calculate_13612U_momentum(data_monthly, periods):
    uniform_momentum_score = sum([(data_monthly / data_monthly.shift(month) - 1) / 4 for month in periods]).dropna()
    return uniform_momentum_score*100


uniform_momentum_df = calculate_13612U_momentum(online_monthly, periods)


# Function that determines to which Universe we should invest next month
def canary_chant(uniform_momentum):

    # Universes of assets
    canary_asset = uniform_momentum[canary_tickers]
    offensive_assets = uniform_momentum[offensive_tickers]
    defensive_assets = uniform_momentum[defensive_tickers]

    # Access to the last row of Canary Assets 
    canary_assets = canary_asset.iloc[-1]
    canary_assets = pd.DataFrame(canary_assets.map(lambda x: True if x > 0 else False)).transpose()

    # Access to Top Defensive Assets (Tickers and Values)
    top_defensive_assets = defensive_assets.iloc[-1].idxmax()

    # Access to Top Offensive Assets
    top_offensive_assets = offensive_assets.iloc[-1].nlargest(4).index.tolist()
    top_offensive_assets_values = offensive_assets[top_offensive_assets].iloc[-1].to_list()

    # Offensive assets to Defensive positions
    off_to_def = [(asset, asset_value > 0) for asset, asset_value in zip(top_offensive_assets, top_offensive_assets_values)]

    # Cases to consider
    if all(canary_assets):
        print(f"\nIn {canary_assets.index[0]} we switch to Offensive Universe.\n")
        print(f"    Offensive Assets (Top 4/8): {top_offensive_assets}")
        print(f"    Who remains in Offensive Assets? {off_to_def}\n")

    else:
        print(f"In {canary_assets.index[0]} we switch to Defensive Universe.\n")
        print(f"    Defensive Assets (Top 1/2): {top_defensive_assets}")


canary_chant(uniform_momentum_df)
