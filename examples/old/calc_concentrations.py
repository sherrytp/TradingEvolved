from utils.mapper import Mapper
from api.sigma import TradeTwoSigma


etf = Mapper().ETF_universe
sectors = Mapper().sectors


def individual_concentration(positions, base_capital):
    """
    Print the individual concentration in the portfolio given existing positions and base capital
    :param positions: list of dict
    :param base_capital: int or float
    """
    for i in positions:
        ticker = two.lookup_ticker(i['instrumentId'])['ticker']
        if ticker not in etf:
            print('{} - {} - {:.2f}%'.format('Equity', ticker, 100 * i['totalShares'] * i['avgEntryPrice'] /
                                             base_capital))
        else:
            print('{} - {} - {:.2f}%'.format('ETF', ticker, 100 * i['totalShares'] * i['avgEntryPrice'] /
                                             base_capital))


def sector_concentratioin(positions, base_capital):
    """
    Print the sector concentration in the portfolio given existing positions and base capital
    :param positions: list of dict
    :param base_capital: int or float
    """
    concentration = {}
    col = []

    for i in positions:
        ticker = two.lookup_ticker(i['instrumentId'])['ticker']
        if ticker not in etf:
            concentration[ticker] = {'exposure': i['avgEntryPrice'] * i['totalShares'], 'sector': sectors[ticker]}

    for i in concentration:
        col.append(concentration[i]['sector'])

    for i in set(col):
        money = 0
        for j in concentration:
            if concentration[j]['sector'] == i:
                money += concentration[j]['exposure']
        print('{} - {:.2f}%'.format(i, 100 * (money / base_capital)))


if __name__ == '__main__':
    two = TradeTwoSigma('8a6b5c00-78eb-4a16-a02a-658800f8be28')
    postitions = two.get_positions(get_all=True)

    individual_concentration(postitions, 100000000)
    print()
    sector_concentratioin(postitions, 100000000)
