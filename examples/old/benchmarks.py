#
# Copyright 2013 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import numpy as np
import pandas as pd
import pandas_datareader.data as pd_reader

def get_benchmark_returns(symbol, first_date, last_date):
    """
    Get a Series of benchmark returns from IEX associated with `symbol`.
    Default is `SPY`.

    Parameters
    ----------
    symbol : str
        Benchmark symbol for which we're getting the returns.

    The data is provided by Yahoo Finance
    """
    data = pd_reader.DataReader(
        symbol,
        'yahoo',
        first_date,
        last_date
    )

    data = data['Close']

    data[pd.Timestamp('2008-12-15')] = np.nan
    data[pd.Timestamp('2009-08-11')] = np.nan
    data[pd.Timestamp('2012-02-02')] = np.nan

    data = data.fillna(method='ffill')

    return data.sort_index().tz_localize('UTC').pct_change(1).iloc[1:]


def get_benchmark(symbol=None, start=None, end=None):
    import pandas_datareader as pdr
    bm = pdr.get_data_yahoo(symbol, pd.Timestamp(start), pd.Timestamp(end))['Close']
    bm.index = bm.index.tz_localize('UTC')
    return bm.pct_change(periods=1).fillna(0)