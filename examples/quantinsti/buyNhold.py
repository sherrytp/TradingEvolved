"""
buy_and_hold.py
===========================
    author: erichamer
"""

import numpy as np

def myTradingSystem(DATE, OPEN, HIGH, LOW, CLOSE, VOL, OI, exposure, equity, settings):
    '''
    based on the number of markets, set our exposure to 1, completely long
    '''
    n_markets = CLOSE.shape[1]
    pos = np.ones((1, n_markets))
    pos = pos/np.sum(abs(pos))

    return pos, settings


##### Do not change this function definition #####
def mySettings():
    '''
    Define your market list and other settings here.
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

    settings['lookback'] = 252
    settings['budget'] = 10**6
    settings['slippage'] = 0.05

    return settings


# Evaluate trading system defined in current file.
if __name__ == '__main__':
    '''
    import the toolbox and use it to run this strategy
    '''
    from quantiacsToolbox.quantiacsToolbox import runts, stats
    res = runts(__file__)

    lst_markets = res['settings']['markets']
    try:
        i = lst_markets.index('fundEquity')
        del lst_markets[i]
    except:
        pass

    for i in range(0, len(lst_markets)):
        ticker = lst_markets[i]
        market_equity = np.array(res['marketEquity'])
        equity = market_equity[:,i]
        my_stats = stats(equity)
        print('ticker ' + ticker + ' Sharpe:' + str(my_stats['sharpe']))
