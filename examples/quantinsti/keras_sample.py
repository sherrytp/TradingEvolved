"""
keras_sample.py
===========================
    author: erichamer
"""

import numpy as np

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM

'''
    create_and_train creates the Keras NN based on the returns calculated
    from the CLOSE price data.  the price data is normalized base on average
    and std deviation.

    the trained model, the price average, and the std. deviation are stored in
    the settings to persist through the entire backtest
'''
def create_and_train(CLOSE, settings):
    price_data = CLOSE[1:, :]
    average = np.average(price_data)
    std_dev = np.std(price_data)
    price_data = (price_data - average) / std_dev

    return_data = (CLOSE[1:, :] - CLOSE[:- 1, :]) / CLOSE[:- 1, :]

    train_x = np.reshape(price_data, (price_data.shape[0], 1, price_data.shape[1]))
    train_y = return_data

    # create and fit the LSTM network
    model = Sequential()
    model.add(LSTM(4, input_dim=1))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(train_x, train_y, epochs=100, batch_size=1, verbose=2)

    settings['mean'] = average
    settings['std'] = std_dev
    settings['model'] = model

    return

'''
    myTradingSystem is called by the toolkit.
    if the model has not been trained, do so with the lookback data based on
    the starting date.

    Once the model is trained, use it to predict the next return, and base the
    exposure on the return.
'''
def myTradingSystem(DATE, CLOSE, exposure, equity, settings):
    look_back = settings['lookback']

    if 'model' not in settings:
        create_and_train(CLOSE[:look_back - 2], settings)

    model = settings['model']
    average = settings['mean']
    std_dev = settings['std']

    # normalize and format the data for Keras
    test_x = (CLOSE[look_back-1:] - average) / std_dev
    test_x = np.reshape(test_x, (test_x.shape[0], 1, test_x.shape[1]))

    test_y = model.predict(test_x)
    new_delta = test_y[0]
    nMarkets = CLOSE.shape[1]
    pos = np.ones((1, nMarkets))
    if new_delta >= 0:
        pos[0] = 1
    else:
        pos[0] = -1

    return pos, settings

def mySettings():
    ''' Define your trading system settings here '''
    settings = {}

    # Futures Contracts
    settings['markets'] = ['F_ES'] # just the S&P mini
    settings['slippage'] = 0.05
    settings['budget'] = 1000000
    settings['lookback'] = 504
    settings['beginInSample'] = '20140101'

    return settings

# Evaluate trading system defined in current file.
if __name__ == '__main__':
    from quantiacsToolbox import quantiacsToolbox

    np.random.seed(98274534)
    results = quantiacsToolbox.runts(__file__)
