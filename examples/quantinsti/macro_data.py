"""
macro_data.py
===========================
    author: erichamer

    base the investment position entirely on durable goods
"""

### Quantiacs Trading System Template
# import necessary Packages below:
import numpy as np


def myTradingSystem(DATE, CLOSE, USA_DUR, exposure, equity, settings):
    '''Define your trading system here.
        if the durable goods data is above zero, then go long in all positions.
        if it is less than zero, then go short in all positions
    '''
    n_markets = CLOSE.shape[1]
    if 0 < USA_DUR[0]:
        pos = np.ones((1, n_markets))
    else:
        pos = -1 * np.ones((1, n_markets))

    pos = pos/np.sum(abs(pos))

    return pos, settings


def mySettings():
    '''Define your market list and other settings here.
    The function name "mySettings" should not be changed.
    '''

    settings = {}

    # Futures Contracts
    settings['markets'] = ['CASH', 'F_AD', 'F_AE', 'F_AH', 'F_AX', 'F_BC', 'F_BG', 'F_BO', 'F_BP', 'F_C',  'F_CA',
                           'F_CC', 'F_CD', 'F_CF', 'F_CL', 'F_CT', 'F_DL', 'F_DM', 'F_DT', 'F_DX', 'F_DZ', 'F_EB',
                           'F_EC', 'F_ED', 'F_ES', 'F_F',  'F_FB', 'F_FC', 'F_FL', 'F_FM', 'F_FP', 'F_FV', 'F_FY',
                           'F_GC', 'F_GD', 'F_GS', 'F_GX', 'F_HG', 'F_HO', 'F_HP', 'F_JY', 'F_KC', 'F_LB', 'F_LC',
                           'F_LN', 'F_LQ', 'F_LR', 'F_LU', 'F_LX', 'F_MD', 'F_MP', 'F_ND', 'F_NG', 'F_NQ', 'F_NR',
                           'F_NY', 'F_O',  'F_OJ', 'F_PA', 'F_PL', 'F_PQ', 'F_RB', 'F_RF', 'F_RP', 'F_RR', 'F_RU',
                           'F_RY', 'F_S',  'F_SB', 'F_SF', 'F_SH', 'F_SI', 'F_SM', 'F_SS', 'F_SX', 'F_TR', 'F_TU',
                           'F_TY', 'F_UB', 'F_US', 'F_UZ', 'F_VF', 'F_VT', 'F_VW', 'F_VX',  'F_W', 'F_XX', 'F_YM',
                           'F_ZQ']

    settings['beginInSample'] = '19920601'
    settings['lookback'] = 10
    settings['budget'] = 10**6
    settings['slippage'] = 0.05

    return settings


# Evaluate trading system defined in current file.
if __name__ == '__main__':
    from quantiacsToolbox.quantiacsToolbox import runts
    runts(__file__)
