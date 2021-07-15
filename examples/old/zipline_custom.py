import numpy as np
import json
from zipline.pipeline import CustomFactor, CustomFilter
from zipline.pipeline.data import USEquityPricing
from zipline.data import bundles

from alphacompiler.data.sf1_fundamentals import Fundamentals


class MedianDollarVolume(CustomFactor):
    """
    Customer factor calculating the median average dollar volume of an equity

    Default to 200-day window length
    """
    # Default inputs
    inputs = [USEquityPricing.close, USEquityPricing.volume]
    window_length = 200

    def compute(self, today, assets, out, price, volume):
        out[:] = np.nanmedian(price * volume, axis=0)


class CountMissingPrice(CustomFactor):
    """
    Custome factor calculating total days on which the close price of an equity is missing
    """
    # Default inputs
    inputs = [USEquityPricing.close]

    def compute(self, today, assets, out, close_price):
        out[:] = np.sum(np.isnan(close_price), axis=0)


class AverageMarketCap(CustomFactor):
    """
    Customer factor calculating the moving average market capitalization

    Default to 20-day window length
    """
    # Default inputs
    inputs = [Fundamentals().marketcap_ART]
    window_length = 20

    def compute(self, today, assets, out, cap):
        out[:] = np.nanmean(cap, axis=0)


class CommonStockFilter(CustomFilter):
    bundle_data = bundles.load('abc')

    with open('../data/common_stocks.txt', 'r') as f:
        symbols = f.read().split()

    inputs = []
    window_length = 1
    securities = bundle_data.asset_finder.lookup_symbols(symbols, as_of_date=None)

    def compute(self, today, assets, out):
        out[:] = np.in1d(assets, self.securities)


class SigmaTradableFilter(CustomFilter):
    bundle_data = bundles.load('abc')

    with open("../data/ticker_to_sector.json", 'r') as f:
        sectors = json.load(f)

    inputs = []
    window_length = 1
    securities = bundle_data.asset_finder.lookup_symbols(sectors.keys(), as_of_date=None)

    def compute(self, today, assets, out):
        out[:] = np.in1d(assets, self.securities)


def QTradableStocksUS():
    """
    Simulating Quantopian's QTradableStocksUS

    return: zipline.pipeline.Pipeline

    Criterion:

    First Pass: 1. The stock must be a common (not preferred) stock
                2. The stock must be a depository receipt
                3. The stock must not be a limited partnership
                4. The stock must not be traded OTC

    Second Pass: Equities must be the primary share of the companies

    Third Pass: 1. The stock must have a 200-day median daily dollar volume exceeding 2.5 million USD
                2. The stock must have a moving average market capitalization of at least 350 million
                over the last 20 days
                3. The stock must not have more than 20 days of missing close price in the last 200 days
                and must not have any missing close price in the last 20 days
    """
    # Filters

    # First Pass
    common_stocks = CommonStockFilter()

    # Third Pass
    # 1.
    median_dollar_volume = MedianDollarVolume() > 2500000

    # 2.
    avg_market_cap = AverageMarketCap() > 350000000

    # 3.
    two_hundred__day_missing_price = CountMissingPrice(window_length=200) <= 20

    twenty_day_missing_price = CountMissingPrice(window_length=20) < 1

    sigma = SigmaTradableFilter()

    filters = common_stocks & median_dollar_volume & avg_market_cap & two_hundred__day_missing_price \
              & twenty_day_missing_price & sigma

    return filters
