"""
Module for building a complete daily dataset from quandl sharadar equity and fund's dataset.
written by Amir Vahid modified from https://github.com/ajjcoppola

make sure you set the QUANDL_API_KEY env variable to use this bundle
"""
from io import BytesIO
from zipfile import ZipFile

import numpy as np
import pandas as pd
import requests
from click import progressbar
from logbook import Logger
from six import iteritems
from six.moves.urllib.parse import urlencode
from trading_calendars import register_calendar_alias
from zipline.data.bundles import core as bundles  # looking in .zipline/extensions.py

# Code from:
# Quantopian Zipline Issues:
# "Cannot find data bundle during ingest #2275"
# https://github.com/quantopian/zipline/issues/2275

log = Logger(__name__)

TEN_MEGABYTE = 2048 * 2048
QUANDL_EQUITY_URL = (
    'https://www.quandl.com/api/v3/datatables/SHARADAR/SEP.csv?'
)
QUANDL_FUND_URL = (
    'https://www.quandl.com/api/v3/datatables/SHARADAR/SFP.csv?'
)


@bundles.register('qefp')
def sharadar_equity_fund_bundle(environ,
                                asset_db_writer,
                                minute_bar_writer,
                                daily_bar_writer,
                                adjustment_writer,
                                calendar,
                                start_session,
                                end_session,
                                cache,
                                show_progress,
                                output_dir):
    api_key = environ.get('QUANDL_API_KEY')
    if api_key is None:
        raise ValueError(
            "Please set your QUANDL_API_KEY environment variable and retry."
        )

    ###ticker2sid_map = {}

    raw_data_equity = fetch_data_table_equity(
        api_key,
        show_progress,
        environ.get('QUANDL_DOWNLOAD_ATTEMPTS', 5)
    )

    raw_data_fund = fetch_data_table_fund(
        api_key,
        show_progress,
        environ.get('QUANDL_DOWNLOAD_ATTEMPTS', 5)
    )

    raw_data = raw_data_equity.append(raw_data_fund, ignore_index=True)
    # raw_data.reset_index(drop=True, inplace=True)

    # asset_metadata_equity = gen_asset_metadata(
    #     raw_data_equity[['symbol', 'date']],
    #     show_progress
    # )
    #
    # asset_metadata_fund = gen_asset_metadata(
    #     raw_data_fund[['symbol', 'date']],
    #     show_progress
    # )
    asset_metadata = gen_asset_metadata(
        raw_data[['symbol', 'date']],
        show_progress
    )

    # asset_db_writer.write(asset_metadata_equity)

    # asset_db_writer.write(asset_metadata_fund)
    asset_db_writer.write(asset_metadata)

    # symbol_map_equity = asset_metadata_equity.symbol
    # symbol_map_fund = asset_metadata_fund.symbol
    symbol_map = asset_metadata.symbol
    sessions = calendar.sessions_in_range(start_session, end_session)

    # raw_data_equity.set_index(['date', 'symbol'], inplace=True)
    # raw_data_fund.set_index(['date', 'symbol'], inplace=True)
    raw_data.set_index(['date', 'symbol'], inplace=True)
    # daily_bar_writer.write(
    #     parse_pricing_and_vol(
    #         raw_data_equity,
    #         sessions,
    #         symbol_map_equity
    #     ),
    #     show_progress=show_progress
    # )
    # daily_bar_writer.write(
    #     parse_pricing_and_vol(
    #         raw_data_fund,
    #         sessions,
    #         symbol_map_fund
    #     ),
    #     show_progress=show_progress
    # )
    daily_bar_writer.write(
        parse_pricing_and_vol(
            raw_data,
            sessions,
            symbol_map
        ),
        show_progress=show_progress
    )

    # raw_data_equity.reset_index(inplace=True)
    # raw_data_fund.reset_index(inplace=True)
    raw_data.reset_index(inplace=True)
    # raw_data.index = pd.DatetimeIndex(raw_data.date)
    ###ajjc changes
    # raw_data_equity['symbol'] = raw_data_equity['symbol'].astype('category')
    # raw_data_equity['sid'] = raw_data_equity.symbol.cat.codes
    # raw_data_fund['symbol'] = raw_data_fund['symbol'].astype('category')
    # raw_data_fund['sid'] = raw_data_fund.symbol.cat.codes
    raw_data['symbol'] = raw_data['symbol'].astype('category')
    raw_data['sid'] = raw_data.symbol.cat.codes
    # read in Dividend History
    # ajjc pharrin----------------------

    ###uv = raw_data.symbol.unique()  # get unique m_tickers (Zacks primary key)
    # iterate over all the unique securities and pack data, and metadata
    # for writing
    # counter of valid securites, this will be our primary key
    ###sec_counter = 0

    ###for tkr in uv:
    ###    #df_tkr = raw_data[raw_data['symbol'] == tkr]
    ###    ticker2sid_map[tkr] = sec_counter  # record the sid for use later
    ###    sec_counter += 1

    ### dfd = pd.read_csv(file_name, index_col='date',
    ###                 parse_dates=['date'], na_values=['NA'])
    # drop rows where dividends == 0.0
    # raw_data_equity = raw_data_equity[raw_data_equity["dividends"] != 0.0]
    # raw_data_fund = raw_data_fund[raw_data_fund["dividends"] != 0.0]
    raw_data = raw_data[raw_data["dividends"] != 0.0]
    # raw_data_equity.set_index(['date', 'sid'], inplace=True)
    # raw_data_fund.set_index(['date', 'sid'], inplace=True)
    raw_data.set_index(['date', 'sid'], inplace=True)
    # raw_data.loc[:, 'ex_date'] = raw_data.loc[:, 'record_date'] = raw_data.date
    # raw_data.loc[:, 'declared_date'] = raw_data.loc[:, 'pay_date'] = raw_data.date
    #
    raw_data.loc[:, 'ex_date'] = raw_data.loc[:, 'record_date'] = raw_data.index.get_level_values(
        'date')
    # raw_data_equity.loc[:, 'declared_date'] = raw_data_equity.loc[:,
    #                                           'pay_date'] = raw_data_equity.index.get_level_values('date')
    # raw_data_fund.loc[:, 'declared_date'] = raw_data_fund.loc[:,
    #                                         'pay_date'] = raw_data_fund.index.get_level_values('date')
    raw_data.loc[:, 'declared_date'] = raw_data.loc[:,
                                       'pay_date'] = raw_data.index.get_level_values('date')
    # raw_data.loc[:, 'sid'] = raw_data.loc[:, 'symbol'].apply(lambda x: ticker2sid_map[x])
    # raw_data_equity = raw_data_equity.rename(columns={'dividends': 'amount'})
    # raw_data_fund = raw_data_fund.rename(columns={'dividends': 'amount'})
    raw_data = raw_data.rename(columns={'dividends': 'amount'})
    # raw_data = raw_data.drop(['open', 'high', 'low', 'close', 'volume','symbol'], axis=1)

    # raw_data_equity.reset_index(inplace=True)
    # raw_data_fund.reset_index(inplace=True)
    raw_data.reset_index(inplace=True)
    # raw_data_equity = raw_data_equity.drop(['open', 'high', 'low', 'close', 'volume', 'symbol', 'date'], axis=1)
    # raw_data_fund = raw_data_fund.drop(['open', 'high', 'low', 'close', 'volume', 'symbol', 'date'], axis=1)
    raw_data = raw_data.drop(['open', 'high', 'low', 'close', 'volume', 'symbol', 'date'], axis=1)
    # raw_data = raw_data.drop(['open', 'high', 'low', 'close', 'volume', 'lastupdated', 'ticker', 'closeunadj'], axis=1)
    # # format dfd to have sid
    # adjustment_writer.write(dividends=raw_data_equity)
    # adjustment_writer.write(dividends=raw_data_fund)
    adjustment_writer.write(dividends=raw_data)
    # ajjc ----------------------------------


def format_metadata_url_equity(api_key):
    """ Build the query URL for Quandl Prices metadata.
    """
    query_params = [('api_key', api_key), ('qopts.export', 'true')]

    return (
            QUANDL_EQUITY_URL + urlencode(query_params)
    )


def format_metadata_url_fund(api_key):
    """ Build the query URL for Quandl Prices metadata.
    """
    query_params = [('api_key', api_key), ('qopts.export', 'true')]

    return (
            QUANDL_FUND_URL + urlencode(query_params)
    )


def load_data_table(file,
                    index_col,
                    show_progress=False):
    """ Load data table from zip file provided by Quandl.
    """
    with ZipFile(file) as zip_file:
        file_names = zip_file.namelist()
        assert len(file_names) == 1, "Expected a single file from Quandl."
        wiki_prices = file_names.pop()
        with zip_file.open(wiki_prices) as table_file:
            if show_progress:
                log.info('Parsing raw data.')
            data_table = pd.read_csv(
                table_file,
                parse_dates=['date'],
                index_col=index_col,
                usecols=[
                    'ticker',
                    'date',
                    'open',
                    'high',
                    'low',
                    'close',
                    'volume',
                    'dividends',
                    ##'closeunadj',
                    ##'lastupdated' #prune last two columns for zipline bundle load
                ],
            )

    data_table.rename(
        columns={
            'ticker': 'symbol'
        },
        inplace=True,
        copy=False,
    )
    return data_table


def fetch_data_table_equity(api_key,
                            show_progress,
                            retries):
    for _ in range(retries):
        try:
            if show_progress:
                log.info('Downloading Sharadar Equity Prices metadata.')

            metadata_equity = pd.read_csv(
                format_metadata_url_equity(api_key)
            )

            print(metadata_equity)

            # Extract link from metadata and download zip file.
            table_url_equity = metadata_equity.loc[0, 'file.link']

            if show_progress:
                raw_file_equity = download_with_progress(
                    table_url_equity,
                    chunk_size=TEN_MEGABYTE,
                    label="Downloading Prices table from Quandl Sharadar Equity"
                )

            else:
                raw_file_equity = download_without_progress(table_url_equity)

            return load_data_table(
                file=raw_file_equity,
                index_col=None,
                show_progress=show_progress,
            )

        except Exception:
            log.exception("Exception raised reading Quandl data. Retrying.")

    else:
        raise ValueError(
            "Failed to download Quandl data after %d attempts." % (retries)
        )


def fetch_data_table_fund(api_key,
                          show_progress,
                          retries):
    for _ in range(retries):
        try:
            if show_progress:
                log.info('Downloading Sharadar Fund Prices metadata.')

            metadata_fund = pd.read_csv(
                format_metadata_url_fund(api_key)
            )

            print(metadata_fund)

            # Extract link from metadata and download zip file.
            table_url_fund = metadata_fund.loc[0, 'file.link']
            if show_progress:
                raw_file_fund = download_with_progress(
                    table_url_fund,
                    chunk_size=TEN_MEGABYTE,
                    label="Downloading Prices table from Quandl Sharadar Fund"
                )
            else:
                raw_file_fund = download_without_progress(table_url_fund)

            return load_data_table(
                file=raw_file_fund,
                index_col=None,
                show_progress=show_progress,
            )

        except Exception:
            log.exception("Exception raised reading Quandl data. Retrying.")

    else:
        raise ValueError(
            "Failed to download Quandl data after %d attempts." % (retries)
        )


def gen_asset_metadata(data, show_progress):
    if show_progress:
        log.info('Generating asset metadata.')

    data = data.groupby(
        by='symbol'
    ).agg(
        {'date': [np.min, np.max]}
    )
    data.reset_index(inplace=True)
    data['start_date'] = data.date.amin
    data['end_date'] = data.date.amax
    del data['date']
    data.columns = data.columns.get_level_values(0)

    data['exchange'] = 'QUANDL'
    data['auto_close_date'] = data['end_date'].values + pd.Timedelta(days=1)
    return data


def parse_pricing_and_vol(data,
                          sessions,
                          symbol_map):
    for asset_id, symbol in iteritems(symbol_map):
        asset_data = data.xs(
            symbol,
            level=1
        ).reindex(
            sessions.tz_localize(None)
        ).fillna(0.0)
        yield asset_id, asset_data


def download_with_progress(url, chunk_size, **progress_kwargs):
    """
    Download streaming data from a URL, printing progress information to the
    terminal.

    Parameters
    ----------
    url : str
        A URL that can be understood by ``requests.get``.
    chunk_size : int
        Number of bytes to read at a time from requests.
    **progress_kwargs
        Forwarded to click.progressbar.

    Returns
    -------
    data : BytesIO
        A BytesIO containing the downloaded data.
    """
    resp = requests.get(url, stream=True)
    resp.raise_for_status()

    total_size = int(resp.headers['content-length'])
    data = BytesIO()
    with progressbar(length=total_size, **progress_kwargs) as pbar:
        for chunk in resp.iter_content(chunk_size=chunk_size):
            data.write(chunk)
            pbar.update(len(chunk))

    data.seek(0)
    return data


def download_without_progress(url):
    """
    Download data from a URL, returning a BytesIO containing the loaded data.

    Parameters
    ----------
    url : str
        A URL that can be understood by ``requests.get``.

    Returns
    -------
    data : BytesIO
        A BytesIO containing the downloaded data.
    """
    resp = requests.get(url)
    resp.raise_for_status()
    return BytesIO(resp.content)


register_calendar_alias("qefp", "NYSE")
