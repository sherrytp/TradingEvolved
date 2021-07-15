### Quantiacs Trend Following Trading System Example
# import necessary Packages below:
import numpy
import sys

def myTradingSystem(DATE, OPEN, HIGH, LOW, CLOSE, VOL, OI, P, R, RINFO, exposure, equity, settings):
    ''' This system uses trend following techniques to allocate capital into the desired equities'''

    nMarkets=CLOSE.shape[1]

    periodLong=300 #%[200:10:300]#
    periodShort=90 #%[20:10:100]#

    smaLong=numpy.nansum(CLOSE[-periodLong:,:],axis=0)/periodLong
    smaRecent=numpy.nansum(CLOSE[-periodShort:,:],axis=0)/periodShort

    longEquity= numpy.array(smaRecent > smaLong)
    shortEquity= ~longEquity

    pos=numpy.zeros((1,nMarkets))
    pos[0,longEquity]=20
    pos[0,shortEquity]=-5

    weights = pos/numpy.nansum(abs(pos))

    return weights, settings


def mySettings():
    ''' Define your trading system settings here '''

    settings= {}


    # Futures Contracts

    settings['markets'] = ['CASH', 'F_ES', 'F_MD', 'F_NQ', 'F_RU', 'F_XX',
		 'F_YM', 'F_AX', 'F_CA', 'F_LX', 'F_VX', 'F_AE', 'F_DM',
		 'F_AH', 'F_DZ', 'F_FB', 'F_FM', 'F_FP', 'F_FY', 'F_NY',
		 'F_PQ', 'F_SH', 'F_SX', 'F_GD', 'F_FV', 'F_TU', 'F_TY',
		 'F_US', 'F_DT', 'F_UB', 'F_UZ', 'F_GS', 'F_CF', 'F_GX',
		 'F_VF', 'F_VT', 'F_VW', 'F_ED', 'F_SS', 'F_ZQ', 'F_EB',
		 'F_F', 'F_CL', 'F_HO', 'F_NG', 'F_RB', 'F_BG', 'F_BC',
		 'F_LU', 'F_FL', 'F_HP', 'F_LQ', 'F_GC', 'F_HG', 'F_PA',
		 'F_PL', 'F_SI', 'F_AD', 'F_BP', 'F_CD', 'F_DX', 'F_EC',
		 'F_JY', 'F_MP', 'F_SF', 'F_LR', 'F_RR', 'F_RF', 'F_RP',
		 'F_RY', 'F_TR', 'F_ND', 'F_BO', 'F_C', 'F_CC', 'F_CT', 'F_FC',
		 'F_KC', 'F_LB', 'F_LC', 'F_LN', 'F_NR', 'F_O', 'F_OJ',
		 'F_S', 'F_SB', 'F_SM', 'F_W', 'F_DL']
    settings['endInSample'] = '20181205'
    settings['beginInSample'] = '20080101'
    # settings['beginInSample'] = '20120506'
    # settings['endInSample'] = '20150506'
    settings['lookback'] = 504
    settings['budget'] = 1000000
    settings['slippage'] = 0.01

    return settings

# Evaluate trading system defined in current file.
if __name__ == '__main__':
    import math

    w_1 = 5.0
    w_2 = 8.0
    lr = 0.001
    success = 0.0000001

    '''
    a_new = a_old - lr * grad(F(a_old))
    
    {\displaystyle \mathbf {a} _{n+1}=\mathbf {a} _{n}-\gamma \nabla F(\mathbf {a} _{n})}
    '''
    i = 0
    j_org = 2 * w_1 + 4 * (w_2 * w_2 * w_2)
    while(True):
        w_1_new = w_1 - lr * (2 * w_1)
        w_2_new = w_2 - lr * (w_2 * w_2 * w_2)
        delta = (w_1_new - w_1) * (w_1_new - w_1) + (w_2_new - w_2) * (w_2_new - w_2)
        delta = math.sqrt(delta)
        i += 1
        print('iteration: ' + str(i) + ' delta: ' + str(delta))

        if delta < success:
            break

        if i > 1000000:
            break

        w_1 = w_1_new
        w_2 = w_2_new

    sys.exit(0)

    from quantiacsToolbox import runts

    runts()