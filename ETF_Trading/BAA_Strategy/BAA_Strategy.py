import datetime
import yfinance as yf
import pandas as pd

# Asset tickers
defensive_tickers = ["TIP", "DBC", "BIL", "IEF", "TLT", "LQD", "AGG"]
canary_tickers = ["SPY", "EEM", "EFA", "AGG"]
offensive_aggressive_tickers = ["QQQ", "EEM", "EFA", "AGG"]
offensive_balanced_tickers = ["SPY", "QQQ", "IWM", "VGK", "EWJ", "EEM", "VNQ", "DBC", "GLD", "TLT", "HYG", "LQD"]
baa_tickers = ["SPY", "QQQ", "IWM", "VGK", "EWJ", "EEM", "VNQ", "DBC", "GLD", "TLT", "HYG", "LQD", "EFA", "AGG", "TIP", "BIL", "IEF"]

# Periods (Months) & Weights for Assets
weights = [12, 4, 2, 1]
periods = [1, 3, 6, 12]


# Function to download data from Yahoo Finance
def fetch_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)
    return data['Adj Close']


# Downloaded Data
online = pd.DataFrame(fetch_data(baa_tickers, '2022-01-01', '2024-01-30'))

# Online data grouped by month
online_monthly = online.resample("BM").last()
online_monthly.rename(index={online_monthly.index[-1]: datetime.datetime.today()}, inplace=True)
online_monthly.index = online_monthly.index.strftime('%B %d, %Y')


# Function to compute the 13612W Momentum
def calculate_13612W_momentum(data_monthly, weights, periods):
    weighted_momentum_score = sum([(data_monthly / data_monthly.shift(month) - 1)*weight / 4 for month, weight in zip(periods, weights)]).dropna()
    return weighted_momentum_score*100


weighted_momentum_df = calculate_13612W_momentum(
    online_monthly, weights, periods
    )


# Function to compute the 13612W Momentum
def calculate_relative_momentum(data_monthly):
    # Calculate the 13 month-end prices average (p0...p12)
    rolling_avg = data_monthly.rolling(window=13, min_periods=13).mean()

    # Calculate the relative momentum score
    relative_momentum_score = data_monthly / rolling_avg

    # Remove NaN values resulting from the shift
    relative_momentum_score.dropna(inplace=True)
    return relative_momentum_score


relative_momentum_df = calculate_relative_momentum(online_monthly)


def canary_chant(relative_momentum):

    # Universes of assets
    offensive_aggressive_assets = relative_momentum[
        offensive_aggressive_tickers]
    offensive_balanced_assets = relative_momentum[offensive_balanced_tickers]
    defensive_assets = relative_momentum[defensive_tickers]

    # Access to the last row of Canary Assets
    canary_assets = relative_momentum[canary_tickers].iloc[-1]
    canary_assets = pd.DataFrame(canary_assets.map(
        lambda x: True if x > 0 else False)).transpose()

    # Access to BIL Asset
    bil_asset = relative_momentum[["BIL"]].iloc[-1].iloc[0]

    # Access to Top Defensive Assets (Tickers and Values)
    top_defensive_assets = defensive_assets.iloc[-1].nlargest(3).index.tolist()
    top_defensive_assets_values = defensive_assets[top_defensive_assets].iloc[-1].to_list()

    zipped = zip(top_defensive_assets, top_defensive_assets_values)
    # Assets to cash
    assets_to_cash = [(asset, asset_value < bil_asset) for asset, asset_value
                      in zipped]

    off_agg = offensive_aggressive_assets.iloc[-1].idxmax()
    off_bal = offensive_balanced_assets.iloc[-1].nlargest(6).index.tolist()

    # Cases to consider
    if all(canary_assets):
        print(f"\nIn {canary_assets.index[0]} we switch to Offensive Universe.\n")
        print(f"    Offensive-Aggressive Asset (Top 1/4): {off_agg}")
        print(f"    Offensive-Balanced Assets (Top 6/12): {off_bal}\n")
    else:
        print(f"\nIn {canary_assets.index[0]} we switch to Defensive Universe.\n")
        print(f"    Defensive Assets (Top 3/7): {top_defensive_assets}")
        print(f"    Defensive Assets to cash: {assets_to_cash}\n")


canary_chant(relative_momentum_df)
