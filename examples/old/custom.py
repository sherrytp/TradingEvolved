from zipline.pipeline import CustomFactor, Pipeline, CustomFilter
from zipline import TradingAlgorithm
from zipline.api import symbols, attach_pipeline, schedule_function, pipeline_output
from zipline.utils.events import date_rules, time_rules
from zipline.pipeline.factors import Returns, SimpleBeta
import numpy as np
import pandas as pd
from datetime import datetime
from zipline import run_algorithm
from zipline.api import order, record, symbol
import pytz
from zipline.data.bundles import load
import os


class SecurityInList(CustomFactor):
    inputs = []
    window_length = 1
    securities = []

    def compute(self, today, assets, out):
        out[:] = np.in1d(assets, self.securities)


def initialize(context):
    #     do NOT import symbols in RESEARCH and use following to define symbol list
    sec_list = [symbols('AAAP'),symbols('VEU'), symbols('SHY'), symbols('TLT'), symbols('AGG')]
    # cols = 'A', 'AA', 'AAAGY', 'AAAP', 'AACC', 'AACG', 'AACH'
    # sec_list = symbols(*cols) # symbols('MDY', 'EFA')
    # now = pd.Timestamp.utcnow()
    # bundle = load('qefp', os.environ, now)
    # syms = set(str(asset.symbol)
    #        for asset in bundle.asset_finder.retrieve_all(
    #     bundle.asset_finder.equities_sids))
    # print(syms)
    # print(tuple(syms))
    # cols = list(syms)
    # sec_list = symbols(*cols)
    attach_pipeline(make_pipeline(sec_list, context), 'my_pipeline')
    schedule_function(func=rebalance,
                      date_rule=date_rules.every_day(),
                      time_rule=time_rules.market_open(minutes=30))


def make_pipeline(sec_list, context):
    # Return Factors
    mask = SecurityInList()
    mask.securities = sec_list
    mask = mask.eq(1)  # this is used with CustomFactor
    yr_returns = Returns(window_length=252, mask=mask)
    beta = SimpleBeta(target=symbol('SPY'), regression_length=125)
    pipe = Pipeline(
        screen=mask,
        columns={
            'yr_returns': yr_returns,
            'beta': beta,
        }
    )
    return pipe


# def before_trading_start(context, data):
#     """
#     Called every day before market open.
#     """
#     context.output = pipeline_output('my_pipeline')
#     print(context.output)


def rebalance(context, data):
    #     print (dir(context))
    print('This is my separation')
    print(pipeline_output('my_pipeline'))
    pass


capital_base = 10000
start = pd.Timestamp('2017-01-02', tz='utc')
end = pd.Timestamp('2018-04-20', tz='utc')
result = run_algorithm(start=start,
                       end=end,
                       initialize=initialize,
                       capital_base=capital_base,
                       bundle='sep')
