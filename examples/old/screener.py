import os
import quandl
import numpy as np
import pandas as pd
# Replace <your_key> with you api key
quandl.ApiConfig.api_key = '<your_key>'


def data_tackle():
    ticker = ['AAPL', 'AXP', 'CAT', 'CSCO', 'CVX', 'DD', 'DIS', 'GE', 'GS', 'HD', 'IBM', 'INTC', 'JNJ', 'JPM', 'KO',
              'MCD', 'MMM', 'MRK', 'MSFT', 'NKE', 'PFE', 'PG', 'TRV', 'UNH', 'UTX', 'V', 'VZ', 'WMT', 'XOM']
    for t in ticker:
        df_fr = quandl.get_table('ZACKS/FR', ticker=t)
        df_fc = quandl.get_table('ZACKS/FC', ticker=t)
        df_rf160 = quandl.get_table('ZACKS/RF160', ticker=t)
        df_rm361 = None # pd.read_csv('D:/Trading/Stocker/Data/' + t + '/' + t + '_RM361' + '.csv', index_col=0)

    df_fr = df_fr.sort_values(by=['per_type', 'per_fisc_year'], ascending=[True, False])
    df_fc = df_fc.sort_values(by=['per_type', 'per_fisc_year'], ascending=[True, False])
    df_rf160 = df_rf160.sort_values(by=['per_end_date'], ascending=[False])
    df_rm361 = df_rm361.sort_values(by=['per_end_date'], ascending=[False])
    df_fr = df_fr.reset_index(drop=True)
    df_fc = df_fc.reset_index(drop=True)
    df_rf160 = df_rf160.reset_index(drop=True)
    df_rm361 = df_rm361.reset_index(drop=True)

    roa = np.array(df_fr['ret_asset'])
    roa_cur = df_fr['ret_asset'][0]
    cashflow_op_cur = df_fc['cash_flow_oper_activity'][0]
    ltdebt_eq = np.array(df_rf160['ltdebt_eq'])
    ltdebt_eq = ltdebt_eq[np.isfinite(ltdebt_eq)]
    curr_ratio = np.array(df_fr['curr_ratio'])
    nbr_shares_out = np.array(df_fc['nbr_shares_out'])
    gross_margin = np.array(df_fr['gross_margin'])
    asset_turn = np.array(df_fr['asset_turn'])
    positive_ROA(roa_cur)
    positive_operating_cashflow(cashflow_op_cur)
    cashflow_op_greater_roa(roa_cur, cashflow_op_cur)
    roa_compar(roa)
    ltdebt_eq_compar(ltdebt_eq)
    curr_ratio_compar(curr_ratio)
    nbr_shares_out_compar(nbr_shares_out)
    gross_margin_compar(gross_margin)
    asset_turn_compar(asset_turn)
    score = cal_score()
    return score


def positive_ROA(roa_cur):
    output_frame['p_score_1'] = np.where(roa_cur > 0, 1, 0)
    return output_frame


def positive_operating_cashflow(cashflow_op_cur):
    output_frame['p_score_2'] = np.where(cashflow_op_cur > 0, 1, 0)
    #     print(output_frame['p_score_2'])
    return output_frame


def cashflow_op_greater_roa(roa_cur, cashflow_op_cur):
    output_frame['p_score_3'] = np.where(cashflow_op_cur > roa_cur, 1, 0)
    return output_frame


def roa_compar(roa):
    output_frame['p_score_4'] = np.where(roa[0] > roa[1], 1, 0)
    return output_frame


def ltdebt_eq_compar(ltdebt_eq):
    output_frame['p_score_5'] = np.where(ltdebt_eq[0] < ltdebt_eq[1], 1, 0)
    return output_frame


def curr_ratio_compar(curr_ratio):
    output_frame['p_score_6'] = np.where(curr_ratio[0] > curr_ratio[1], 1, 0)
    return output_frame


def nbr_shares_out_compar(nbr_shares_out):
    output_frame['p_score_7'] = np.where(nbr_shares_out[0] < nbr_shares_out[1], 1, 0)
    return output_frame


def gross_margin_compar(gross_margin):
    output_frame['p_score_8'] = np.where(gross_margin[0] > gross_margin[1], 1, 0)
    return output_frame


def asset_turn_compar(asset_turn):
    output_frame['p_score_9'] = np.where(asset_turn[0] > asset_turn[1], 1, 0)
    return output_frame


def cal_score():
    score = np.sum(
        [output_frame['p_score_1'], output_frame['p_score_2'], output_frame['p_score_3'], output_frame['p_score_4'],
         output_frame['p_score_5'], output_frame['p_score_6'],
         output_frame['p_score_7'], output_frame['p_score_8'], output_frame['p_score_9']])
    return score


if __name__ == '__main__':
    stock_compar = {}
    output_frame = {}
    stockn = []
    stock_score = []
    # ticker = ['AAPL', 'AXP', 'CAT', 'CSCO', 'CVX', 'DD', 'DIS', 'GE', 'GS', 'HD', 'IBM', 'INTC', 'JNJ', 'JPM', 'KO',
    #           'MCD', 'MMM', 'MRK', 'MSFT', 'NKE', 'PFE', 'PG', 'TRV', 'UNH', 'UTX', 'V', 'VZ', 'WMT', 'XOM']
    # for t in ticker:
    #     print(t)
    #     s = int(data_tackle(t))
    stock_score.append(data_tackle())
    stockn.append(t)

    df_score = pd.DataFrame(stock_score, columns=['Score'])
    df_name = pd.DataFrame(stockn, columns=['Stock'])
    stock_rank = df_name.copy()
    stock_rank['Score'] = np.array(stock_score)
    stock_rank = stock_rank.sort_values(by=['Score'], ascending=[False])
    stock_rank = stock_rank.reset_index(drop=True)
    print(stock_rank)